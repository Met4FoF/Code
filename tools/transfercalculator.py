# import h5py
# TODO implent proper multi threaded hdf file handling
import h5pickle as h5py  # be carefull opining more than 100 files in a row kills first file handle !!!
import h5py as h5py_plain
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import pandas as pd
import time
import multiprocessing
from tqdm.contrib.concurrent import process_map
import sys
import time
import sinetools.SineTools as st

# import yappi
import warnings

import os
import shutil
from pathlib import Path
from adccaldata import Met4FOFADCCall
from scipy.optimize import curve_fit  # for fiting of Groupdelay
from scipy import interpolate  # for 1D amplitude estimation

import deepdish as dd  # for dict to hdf serialisation

# used only in transfercalculation because of performance reasonsfrom uncertainties import ufloat
# >>> from uncertainties.umath import *  # sin(), etc.
from uncertainties import ufloat
from uncertainties.umath import *  # sin(), etc.
from met4fofhdftools import add1dsinereferencedatatohdffile

# from met4fofhdftools import addadctransferfunctiontodset
from met4fofhdftools import (
    uncerval,getRAWTFFromExperiemnts,add3compZemaTDMSData
)  # uncerval = np.dtype([("value", np.float), ("uncertainty", np.float)])

import scipy


def ufloattouncerval(ufloat):
    result = np.empty([1], dtype=uncerval)
    result["value"] = ufloat.n
    result["uncertainty"] = ufloat.s
    return result


# plt.rc('font', family='serif')
# plt.rc('text', usetex=True)
PLTSCALFACTOR = 0.5
SMALL_SIZE = 12 * PLTSCALFACTOR
MEDIUM_SIZE = 15 * PLTSCALFACTOR
BIGGER_SIZE = 18 * PLTSCALFACTOR

plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title


def getplotableunitstring(unitstr, Latex=False):
    if not Latex:
        convDict = {
            "\\degreecelsius": "°C",
            "\\degree": "°",
            "\\micro\\tesla": "µT",
            "\\radian\\second\\tothe{-1}": "rad/s",
            "\\metre\\second\\tothe{-2}": "m/s^2",
            "\\metre\\second\\tothe{-1}": "m/s",
            "\\metre": "m",
            "\\volt": "v",
            "\\hertz": "Hz",
        }
    else:
        convDict = {
            "\\degreecelsius": "$^\circ C$",
            "\\degree": "$^\circ$",
            "\\micro\\tesla": "$\micro T$",
            "\\radian\\second\\tothe{-1}": "$\\frac{rad}{s}$",
            "\\metre\\second\\tothe{-2}": "$\\frac{m}{s^2}",
            "\\metre\\second\\tothe{-1}": "$\\frac{m}{s}",
            "\\metre": "m",
            "\\volt": "v",
            "\\hertz": "Hz",
        }
    try:
        result = convDict[unitstr]
    except KeyError:
        result = unitstr
    return result


# code from https://stackoverflow.com/questions/23681948/get-index-of-closest-value-with-binary-search  answered Dec 6 '14 at 23:51 Yaguang
def binarySearch(data, val):
    lo, hi = 0, len(data) - 1
    best_ind = lo
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if data[mid] < val:
            lo = mid + 1
        elif data[mid] > val:
            hi = mid - 1
        else:
            best_ind = mid
            break

        # check if data[mid] is closer to val than data[best_ind]
        dtype = data.dtype
        if data.dtype == np.uint64:
            absmidint = abs(data[mid].astype(np.int64) - val.astype(np.int64))
            absbestind = abs(data[best_ind].astype(np.int64) - val.astype(np.int64))
        else:
            absmidint = abs(data[mid] - val)
            absbestind = abs(data[best_ind] - val)
        if absmidint < absbestind:
            best_ind = mid

    return best_ind


class hdfmet4fofdatafile:
    def __init__(self, hdffile,sensornames=None,dataGroupName='RAWDATA'):
        self.dataGroupName=dataGroupName+'/'
        self.hdffile = hdffile
        if sensornames==None:
            self.senorsnames = list(self.hdffile[self.dataGroupName].keys())
        else:
            self.senorsnames=sensornames
        self.sensordatasets = {}
        for name in self.senorsnames:
            datasets = list(self.hdffile[self.dataGroupName + name].keys())
            keystocheckandremove = [
                "Absolutetime",
                "Absolutetime_uncertainty",
                "Sample_number",
            ]
            for key in keystocheckandremove:
                try:
                    datasets.remove(key)
                except ValueError:
                    raise RuntimeWarning(
                        str(name)
                        + " doese not contain "
                        + str(key)
                        + " dataset is maybe corrupted!"
                    )
            self.sensordatasets[name] = datasets
        print("INIT DONE")
        print("RAW DataGroups are " + str(self.senorsnames))
        print("RAW Datasets are " + str(self.sensordatasets))

    def calcblockwiesestd(self, dataset, blocksize=100):
        # start = time.time()
        blockcount = int(np.floor(dataset.size / blocksize))
        std = np.zeros(blockcount)
        split = np.split(dataset[: blocksize * blockcount], blockcount, axis=0)
        std = np.std(split, axis=1)
        # end = time.time()
        # print("bwstd for dataset " + str(dataset) + "took " + str(end - start) + " secs")
        return std

    def detectnomovment(
        self, datahdfpath, timehdfpath, treshold=0.05, blocksinrow=5, blocksize=100
    ):
        tmpData = np.squeeze(self.hdffile[datahdfpath])
        tmpTime = np.squeeze(self.hdffile[timehdfpath])  # fetch data from hdffile
        mag = np.linalg.norm(tmpData, axis=0)
        std = self.calcblockwiesestd(mag, blocksize=blocksize)
        wasvalide = 0
        nomovementtidx = []
        nomovementtimes = []
        for i in range(std.size):
            if std[i] < treshold:
                wasvalide = wasvalide + 1
            else:
                if wasvalide > blocksinrow:
                    startidx = (i - wasvalide) * blocksize
                    stopidx = (i) * blocksize
                    if stopidx - startidx < 0:
                        print("index error")
                    if tmpTime[stopidx] - tmpTime[startidx] < 0:
                        print("timing error")
                    nomovementtidx.append([startidx, stopidx])
                    nomovementtimes.append([tmpTime[startidx], tmpTime[stopidx]])
                wasvalide = 0
        nomovementidx = np.array(nomovementtidx)
        return nomovementidx, np.array(nomovementtimes)

    def detectmovment(
        self,
        datahdfpath,
        timehdfpath,
        treshold=0.5,
        blocksinrow=5,
        blocksize=100,
        plot=False,
    ):
        tmpData = np.squeeze(self.hdffile[datahdfpath])
        tmpTime = np.squeeze(self.hdffile[timehdfpath])  # fetch data from hdffile
        mag = np.linalg.norm(tmpData, axis=0)
        std = self.calcblockwiesestd(mag, blocksize=blocksize)
        wasvalide = 0
        movementtidx = []
        movementtimes = []
        for i in range(std.size):
            if std[i] > treshold:
                wasvalide = wasvalide + 1
            else:
                if wasvalide > blocksinrow:
                    startidx = (i - wasvalide) * blocksize
                    stopidx = (i) * blocksize
                    movementtidx.append([startidx, stopidx])
                    movementtimes.append([tmpTime[startidx], tmpTime[stopidx]])
                wasvalide = 0
        movementidx = np.array(movementtidx)
        if plot:
            fig, ax = plt.subplots()
            reltime = (tmpTime - tmpTime[0]) / 1e9
            blocktime = reltime[
                0::blocksize
            ]  # cut one block out--> garden fence problem
            ax.plot(blocktime[: std.size], std, label="Data")
            for i in np.arange(len(movementtimes)):
                relmovementimes = (movementtimes[i] - tmpTime[0]) / 1e9
                ax.plot(relmovementimes, np.array([treshold, treshold]), label=str(i))
            fig.show()
        return movementidx, np.array(movementtimes)

    def getnearestidxs(self, sensorname, time):
        absolutimegroupname = self.dataGroupName + sensorname + "/" + "Absolutetime"
        absolutetimes = np.squeeze(self.hdffile[absolutimegroupname])
        idxs = np.copy(time)
        with np.nditer(idxs, op_flags=["readwrite"]) as it:
            for x in it:
                x[...] = binarySearch(absolutetimes, x)
        return idxs

    # TODO move to hdf datafile class
    def addrawtftohdffromexpreiments(self, experimentgroup,
                                     sensor,
                                     numeratorQuantity="Acceleration",
                                     denominatorQuantity="Acceleration",
                                     type="1D_Z",
                                     miscdict={'scale':'Excitation_frequency'},
                                     attrsdict={
            'Phase': {'Unit': '\\radian',
                      'Physical_quantity': ['Phase response'],
                      'Uncertainty_type': "95% coverage gausian"},
            "DUT_Phase": {'Unit': '\\radian',
                          'Physical_quantity': ['Phase of DUT in SSU Time Frame'],
                          'Uncertainty_type': "95% coverage gausian"},
            "REF_Phase": {'Unit': '\\radian',
                        'Physical_quantity': ['Phase betwenn REFerence and Sync'],
                        'Uncertainty_type': "95% coverage gausian"},
            "SSU_ADC_Phase": {'Unit': '\\radian',
                        'Physical_quantity': ['Phase response of the SSU ADC'],
                        'Uncertainty_type': "95% coverage gausian"},
            "DUT_SNYNC_Phase": {'Unit': '\\radian',
                           'Physical_quantity': ['Phase of Reference in SSU Time Frame'],
                           'Uncertainty_type': "95% coverage gausian"},
            'Magnitude': {'Unit': '\\one',
                          'Unit_numerator': '\\metre\\second\\tothe{-2}',
                          'Unit_denominator': '\\metre\\second\\tothe{-2}',
                          'Physical_quantity': ['Magnitude response'],
                          'Uncertainty_type': "95% coverage gausian"},
            'Frequency': {'Unit': '\\hertz',
                          'Physical_quantity': ['Frequency used by sine aproximation'],
                          'Uncertainty_type': "95% coverage gausian"},
            'Excitation_frequency': {'Unit': '\\hertz',
                                     'Physical_quantity': ['Nominal frequency'],
                                     'Uncertainty_type': "95% coverage gausian"},
            'Excitation_amplitude': {'Unit': '\\metre\\second\\tothe{-2}',
                                     'Physical_quantity': ['Excitation Amplitude'],
                                     'Uncertainty_type': "95% coverage gausian"},
            'DUT_amplitude': {'Unit': '\\metre\\second\\tothe{-2}',
                              'Physical_quantity': ['Measured DUT Amplitude'],
                              'Uncertainty_type': "95% coverage gausian"}
                                     }):





        rawtf = getRAWTFFromExperiemnts(experimentgroup,
                                        sensor,
                                        numeratorQuantity,
                                        denominatorQuantity,
                                        type)
        try:
            RAWTRANSFERFUNCTIONGROUP = self.hdffile["RAWTRANSFERFUNCTION"]
        except KeyError:
            RAWTRANSFERFUNCTIONGROUP = self.hdffile.create_group("RAWTRANSFERFUNCTION")
        try:
            SensorRAWTFGROUP = RAWTRANSFERFUNCTIONGROUP[sensor]#->RAWTRANSFERFUNCTION/0x1FE40000_MPU9250
        except KeyError:
            SensorRAWTFGROUP = RAWTRANSFERFUNCTIONGROUP.create_group(sensor)
        try:
            SensorRAWTFGROUPNUM = SensorRAWTFGROUP[numeratorQuantity]#->RAWTRANSFERFUNCTION/0x1FE40000_MPU9250/Acceleration
        except KeyError:
            SensorRAWTFGROUPNUM = SensorRAWTFGROUP.create_group(numeratorQuantity)
        try:
            RAWTFGROUP = SensorRAWTFGROUPNUM[denominatorQuantity]#->RAWTRANSFERFUNCTION/0x1FE40000_MPU9250/Acceleration/Acceleration
        except KeyError:
            RAWTFGROUP = SensorRAWTFGROUPNUM.create_group(denominatorQuantity)
        print(attrsdict)
        for tfcomponentkey in rawtf.keys():
            group=RAWTFGROUP.create_group(tfcomponentkey)
            try:
                attrs=attrsdict[tfcomponentkey]
                for attrkeys in attrs.keys():
                    group.attrs[attrkeys]=attrs[attrkeys]
            except KeyError:
                warnings.warn("for Dataset "+str(tfcomponentkey)+" no attrs are given in attrsdict")
            for vukey in rawtf[tfcomponentkey].keys():# loop over value and uncertanies
                dset=group.create_dataset(vukey,rawtf[tfcomponentkey][vukey].shape, dtype="float64")
                dset[:]=rawtf[tfcomponentkey][vukey]
        scaledataset=RAWTFGROUP[miscdict['scale']]['value']#the values are the scale
        scaledataset.make_scale("Frequency")
        for tfcomponentkey in rawtf.keys():
            if tfcomponentkey!=miscdict['scale']:
                group=RAWTFGROUP[tfcomponentkey]
                group['value'].dims[0].label = "Frequency"
                group['value'].dims[0].attach_scale(scaledataset)
                group['uncertainty'].dims[0].label = "Frequency"
                group['uncertainty'].dims[0].attach_scale(scaledataset)
        print("Done")



class transferfunktion:
    def __init__(self, tfgroup):
        self.group = tfgroup

    def getNearestTF(self, channel, freq):
        Freqs = self.group["Frequency"]['value']
        FreqsUncer = self.group["Frequency"]['uncertainty']
        testFreqIDX = np.argmin(abs(Freqs - freq))
        if (
            Freqs[testFreqIDX] - freq == 0
        ):  # ok we hit an calibrated point no need to interpolate
            return {
                "frequency": ufloat(Freqs[testFreqIDX],FreqsUncer[testFreqIDX]),
                "Magnitude": ufloat(self.group["Magnitude"]['value'][channel][testFreqIDX],self.group["Magnitude"]['uncertainty'][channel][testFreqIDX]),
                "Phase": ufloat(self.group["Phase"]['value'][channel][testFreqIDX],self.group["Phase"]['uncertainty'][channel][testFreqIDX]),
                "N": ufloat(self.group["Phase"]['value'][channel][testFreqIDX],self.group["Phase"]['uncertainty'][channel][testFreqIDX])
            }
        else:
            # interpolate
            A = self.getInterPolated(channel, freq,'Magnitude')
            P = self.getInterPolated(channel, freq,'Phase')
            #TODO add interpolation with frequency 'uncertainty'
            return {"Frequency": ufloat(freq,np.NaN), "Magnitude": A, "Phase": P, "N": ufloat(np.NaN,np.NaN)}

    def __getitem__(self, key):
        if len(key) == 4:
            return self.TransferFunctions[key]
        if len(key) == 2:
            return self.getNearestTF(key[0], key[1])
        else:
            raise ValueError(
                "Invalide Key:  > "
                + str(key)
                + " <Use either [Channel] eg ['ADC1] or [Channel,Frequency] eg ['ADC1',1000]  as key "
            )

    # def getGroupDelay(self, Channel):
    #    freqs = self.TransferFunctions[Channel]['Frequencys']
    #    phases = self.TransferFunctions[Channel]['Phase']
    #    phaseUncer = self.TransferFunctions[Channel]['PhaseUncer']
    #    popt, pcov = curve_fit(PhaseFunc, freqs, phases, sigma=phaseUncer, absolute_sigma=True)
    #    return [popt, pcov]

    def getInterPolated(self, channel, freq,key):
        Freqs = self.group["Frequency"]['value'][:]
        FreqsUncer = self.group["Frequency"]['uncertainty'][:]
        vals = self.group[key]['value'][channel, :]
        valsUncer = self.group[key]['uncertainty'][channel, :]
        testFreqIDX = np.argmin(abs(Freqs - freq))
        DeltaInterpolIDX = 0
        if freq - Freqs[testFreqIDX] < 0:
            DeltaInterpolIDX = -1
        if freq - Freqs[testFreqIDX] > 0:
            DeltaInterpolIDX = 1
        if testFreqIDX + DeltaInterpolIDX < 0:
            assert RuntimeWarning(
                str(freq)
                + " is to SMALL->Extrapolation is not recomended! minimal Frequency is "
                + str(Freqs[0])
            )
            return vals[0]
        if testFreqIDX + DeltaInterpolIDX >= Freqs.size:
            raise ValueError(
                str(freq)
                + " is to BIG->Extrapolation not supported! maximal Frequency is "
                + str(Freqs[-1])
            )
        if DeltaInterpolIDX == 0:
            return vals[testFreqIDX]
        elif DeltaInterpolIDX == -1:
            IDX = [testFreqIDX - 1, testFreqIDX]
        elif DeltaInterpolIDX == 1:
            IDX = [testFreqIDX, testFreqIDX + 1]
        x = Freqs[IDX]
        if not (np.isnan(FreqsUncer[IDX])).all():
                warnings.warn(RuntimeWarning("Interpolation with frequency uncertantiy not supported by getInterPolatedAmplitude Fix this"))
        A = vals[IDX]
        AErr = valsUncer[IDX]
        fA = interpolate.interp1d(x, A)
        fAErr = interpolate.interp1d(x, AErr)
        print(
            "Interpolateded transferfunction for Channel "
            + str(channel)
            + "at Freq "
            + str(freq)
        )  # will not print anything
        return ufloat(fA(freq), fAErr(freq))


class experiment:
    def __init__(self, hdfmet4fofdatafile, times, experemientTypeName, experiementID):
        self.params = {
            "experemientTypeName": experemientTypeName,
        }
        self.met4fofdatafile = hdfmet4fofdatafile
        self.dataGroupName=self.met4fofdatafile.dataGroupName
        self.datafile = self.met4fofdatafile.hdffile
        self.experiemntID = experiementID
        self.timepoints = times
        self.idxs = {}
        self.data = (
            {}
        )  # all elements in this dict are new an will be saved in the hdf file
        self.runtimeData = {}  # all data here will NOT saved into the hdf file
        self.flags = {"saved_to_disk":False}

        for name in self.met4fofdatafile.senorsnames:
            self.idxs[name] = self.met4fofdatafile.getnearestidxs(name, self.timepoints)
            if self.idxs[name][1] - self.idxs[name][0] == 0:
                raise ValueError("EMPTY DATA SET  in "+ experiementID+'\n'+str(name)+' IDXs'+str(self.idxs[name][1])+' '+str(self.idxs[name][0]))
            self.data[name] = {}
            self.runtimeData[name] = {}
            for dataset in self.met4fofdatafile.sensordatasets[name]:
                self.data[name][dataset] = {}
                self.runtimeData[name][dataset] = {}
        #print("EX base class Init done")

    def plotall(self, absolutetime=False):
        cols = len(self.met4fofdatafile.sensordatasets)  # one colum for every sensor
        datasetspersensor = []
        for sensors in self.met4fofdatafile.sensordatasets:
            datasetspersensor.append(len(self.met4fofdatafile.sensordatasets[sensors]))
        rows = np.max(datasetspersensor)
        fig, axs = plt.subplots(cols, rows, sharex="all")
        icol = 0
        for sensor in self.met4fofdatafile.sensordatasets:
            irow = 0
            idxs = self.idxs[sensor]
            axs[icol, 0].annotate(
                sensor.replace("_", " "),
                xy=(0, 0.5),
                xytext=(-axs[icol, 0].yaxis.labelpad - 5, 0),
                xycoords=axs[icol, 0].yaxis.label,
                textcoords="offset points",
                size="large",
                ha="right",
                va="center",
                rotation=90,
            )

            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                dsetattrs = self.datafile[self.dataGroupName + sensor + "/" + dataset].attrs
                time = self.datafile[self.dataGroupName + sensor + "/" + "Absolutetime"][
                    0, idxs[0] : idxs[1]
                ]
                if not absolutetime:
                    time = time.astype("int64") - self.timepoints[0].astype("int64")
                time = time / 1e9
                # print(dsetattrs.keys())
                axs[icol, irow].set_ylabel(getplotableunitstring(dsetattrs["Unit"]))
                if not absolutetime:
                    axs[icol, irow].set_xlabel("Relative time in s")
                else:
                    axs[icol, irow].set_xlabel("Unixtime in s")
                axs[icol, irow].set_title(dataset.replace("_", " "))
                for i in np.arange(
                    self.datafile[self.dataGroupName + sensor + "/" + dataset].shape[0]
                ):
                    label = dsetattrs["Physical_quantity"][i]
                    data = self.datafile[self.dataGroupName + sensor + "/" + dataset][
                        i, idxs[0] : idxs[1]
                    ]
                    axs[icol, irow].plot(time, data, label=label)
                    axs[icol, irow].legend()
                    axs[icol, irow].grid()
                irow = irow + 1
            icol = icol + 1
        fig.show()

    def createHDFGroup(self):
        try:
            EXPERIMENTS = self.datafile["EXPERIMENTS"]
        except KeyError:
            EXPERIMENTS = self.datafile.create_group("EXPERIMENTS")
        try:
            SINEEX = EXPERIMENTS[self.params["experemientTypeName"]]
        except KeyError:
            SINEEX = EXPERIMENTS.create_group(self.params["experemientTypeName"])
        try:
            EXPGROUP = SINEEX[self.experiemntID]
            print(str(EXPGROUP.name) + "existed allready returning groupname")
        except KeyError:
            EXPGROUP = SINEEX.create_group(self.experiemntID)
        self.datafile.flush()
        return EXPGROUP


class sineexcitation(experiment):
    def __init__(self, hdfmet4fofdatafile, times, experiementID,namePrefix=''):
        super().__init__(hdfmet4fofdatafile, times, namePrefix+"Sine excitation", experiementID)

    def dofft(self):
        for sensor in self.met4fofdatafile.sensordatasets:
            idxs = self.idxs[sensor]
            points = idxs[1] - idxs[0]
            time = self.datafile[self.dataGroupName + sensor + "/" + "Absolutetime"][
                0, idxs[0] : idxs[1]
            ]
            reltime = time.astype("int64") - self.timepoints[0].astype("int64")
            self.runtimeData[sensor]["Mean Delta T"] = np.mean(np.diff(reltime / 1e9))
            self.runtimeData[sensor]["RFFT Frequencys"] = np.fft.rfftfreq(
                points, self.runtimeData[sensor]["Mean Delta T"]
            )
            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                data = self.datafile[self.dataGroupName + sensor + "/" + dataset][
                    :, idxs[0] : idxs[1]
                ]
                self.runtimeData[sensor][dataset]["RFFT"] = np.fft.rfft(data, axis=1)
                self.runtimeData[sensor][dataset]["FFT_max_freq"] = self.runtimeData[
                    sensor
                ]["RFFT Frequencys"][
                    np.argmax(
                        abs(
                            np.sum(
                                self.runtimeData[sensor][dataset]["RFFT"][:, 1:], axis=0
                            )
                        )
                    )
                    + 1
                ]
                # print(self.Data[sensor][dataset]['FFT_max_freq'])
        self.flags["FFT Calculated"] = True

    def do3paramsinefits(self, freqs, periods=10):
        if not self.flags["FFT Calculated"]:
            self.dofft()
        for sensor in self.met4fofdatafile.sensordatasets:
            idxs = self.idxs[sensor]
            points = idxs[1] - idxs[0]
            time = self.datafile[self.dataGroupName + sensor + "/" + "Absolutetime"][
                0, idxs[0] : idxs[1]
            ]
            reltime = time.astype("int64") - self.timepoints[0].astype("int64")
            reltime = reltime / 1e9
            excitationfreqs = freqs
            uniquexfreqs = np.sort(np.unique(excitationfreqs))
            idxs = self.idxs[sensor]
            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                try:
                    fftmaxfreq = self.runtimeData[sensor][dataset]["FFT_max_freq"]
                except NameError:
                    self.dofft()
                freqidx = binarySearch(uniquexfreqs, fftmaxfreq)
                datasetrows = self.datafile[self.dataGroupName + sensor + "/" + dataset].shape[
                    0
                ]
                f0 = uniquexfreqs[freqidx]
                self.data[sensor][dataset]["Sin_Fit_freq"] = f0 * np.ones(
                    [datasetrows, 1]
                )  # we doing an singe frequency fit
                # calc first row and create output array[:,idxs[0]:idxs[1]]
                sineparams, sectionStartTimes = st.seq_threeparsinefit(
                    self.datafile[self.dataGroupName + sensor + "/" + dataset][
                        0, idxs[0] : idxs[1]
                    ],
                    reltime,
                    f0,
                    periods=periods,
                    multiTasiking=False,
                    returnSectionStartTimes=True
                )
                self.data[sensor][dataset]["SinPOpt"] = np.zeros([datasetrows, 4])
                self.data[sensor][dataset]["SinPCov"] = np.zeros([datasetrows, 5, 5])
                self.data[sensor][dataset]["SinParams"] = np.zeros(
                    [datasetrows, sineparams.shape[0], 3]
                )
                self.data[sensor][dataset]["SinParams"][0] = sineparams
                for i in np.arange(1, datasetrows):
                    sineparams,sectionStartTimes = st.seq_threeparsinefit(
                        self.datafile[self.dataGroupName + sensor + "/" + dataset][
                            i, idxs[0] : idxs[1]
                        ],
                        reltime,
                        f0,
                        periods=periods,
                        multiTasiking=False,
                        returnSectionStartTimes=True
                    )
                    self.data[sensor][dataset]["SinParams"][i] = sineparams
                for i in np.arange(datasetrows):
                    sineparams = self.data[sensor][dataset]["SinParams"][i]
                    DC = sineparams[:, 2]
                    Complex = sineparams[:, 1] + 1j * sineparams[:, 0]
                    Freq = np.ones(sineparams.shape[0]) * f0
                    lengthMean = np.mean(abs(Complex))
                    nomalized = Complex / abs(Complex)#all vectors ar normalized
                    radialCord = np.sum(nomalized)/nomalized.size #all vectors are added to have one vector pointing in the direction of the mean value
                    deltaAng=np.angle(nomalized)-np.angle(radialCord)#differences of the angles this value can be bigger than -180 -- 180 deg
                    mappedDeltaAngle = np.arctan2(np.sin(deltaAng),
                                                  np.cos(deltaAng))  # map angle differences to +- 180°
                    self.data[sensor][dataset]["SinPOpt"][i, :] = [
                        lengthMean,
                        np.mean(DC),
                        np.mean(Freq),
                        np.angle(radialCord),
                    ]
                    CoVarData = np.stack((
                        abs(Complex)-lengthMean,# subtracting mean, just for safty this should change anything here
                        DC,
                        Freq,
                        deltaAng,# Important Phase mean needs to be substraced and data needs to be maped into -180 -- 180 deg
                        sectionStartTimes),# variance against time is intresting to se reidual phase du to frequency mismatch
                        axis=0
                    )
                    self.data[sensor][dataset]["SinPCov"][i, :] = np.cov(
                        CoVarData, bias=True
                    )  # bias=True Nomation With N like np.std
        self.flags["Sine fit calculated"] = True
        return

    def plotXYsine(
        self, sensor, dataset, axis, fig=None, ax=None, mode="XY", alpha=0.05
    ):
        dsetattrs = self.datafile[self.dataGroupName + sensor + "/" + dataset].attrs
        idxs = self.idxs[sensor]
        time = self.datafile[self.dataGroupName + sensor + "/" + "Absolutetime"][
            0, idxs[0] : idxs[1]
        ]
        reltime = time.astype("int64") - self.timepoints[0].astype("int64")
        reltime = reltime / 1e9
        sinparams = self.data[sensor][dataset]["SinPOpt"]
        f0 = sinparams[axis, 2]
        dc = sinparams[axis, 1]
        amp = sinparams[axis, 0]
        phi = sinparams[axis, 3]
        undisturbedsine = np.sin(2 * np.pi * f0 * reltime + phi) * amp + dc
        sinedata = self.datafile[self.dataGroupName + sensor + "/" + dataset][
            axis, idxs[0] : idxs[1]
        ]
        if fig == None and ax == None:
            fig, ax = plt.subplots()
            ax.set_xlabel(
                "Nonminal "
                + dsetattrs["Physical_quantity"][axis]
                + " calculated from sine in "
                + getplotableunitstring(dsetattrs["Unit"])
            )
        if mode == "XY":
            data = sinedata
            ax.set_ylabel(
                dsetattrs["Physical_quantity"][axis]
                + "in "
                + getplotableunitstring(dsetattrs["Unit"])
            )
        if mode == "diff":
            data = sinedata - undisturbedsine
            ax.set_ylabel(
                dsetattrs["Physical_quantity"][axis]
                + "in "
                + getplotableunitstring(dsetattrs["Unit"])
            )
        if mode == "XY+fit":
            ax.set_ylabel(
                dsetattrs["Physical_quantity"][axis]
                + "in "
                + getplotableunitstring(dsetattrs["Unit"])
            )
            data = sinedata
            polycoevs = np.polyfit(undisturbedsine, data, 2)
            print(polycoevs)

        ax.scatter(undisturbedsine, data, alpha=alpha, s=1, label="Raw data")
        if mode == "XY+fit":
            max = np.max(undisturbedsine)
            min = np.min(undisturbedsine)
            delta = max - min
            polyx = np.arange(min, max, delta / 2e3)
            poly = np.poly1d(polycoevs)
            ax.plot(polyx, poly(polyx), label="Fit")
            # ax.plot(polyx,polyx,label='Prefect signal')
            ax.legend()
        if mode == "XY+fit":
            return polycoevs
        else:
            return

    def plotsinefit(self, absolutetime=False):
        cols = len(self.met4fofdatafile.sensordatasets)  # one colum for every sensor
        datasetspersensor = []
        for sensors in self.met4fofdatafile.sensordatasets:
            datasetspersensor.append(len(self.met4fofdatafile.sensordatasets[sensors]))
        rows = np.max(datasetspersensor)
        fig, axs = plt.subplots(cols, rows, sharex="all")
        icol = 0
        for sensor in self.met4fofdatafile.sensordatasets:
            irow = 0
            idxs = self.idxs[sensor]
            axs[icol, 0].annotate(
                sensor.replace("_", " "),
                xy=(0, 0.5),
                xytext=(-axs[icol, 0].yaxis.labelpad - 5, 0),
                xycoords=axs[icol, 0].yaxis.label,
                textcoords="offset points",
                size="large",
                ha="right",
                va="center",
                rotation=90,
            )

            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                dsetattrs = self.datafile[self.dataGroupName + sensor + "/" + dataset].attrs
                time = self.datafile[self.dataGroupName + sensor + "/" + "Absolutetime"][
                    0, idxs[0] : idxs[1]
                ]
                if not absolutetime:
                    time = time.astype("int64") - self.timepoints[0].astype("int64")
                time = time / 1e9
                # print(dsetattrs.keys())
                axs[icol, irow].set_ylabel(getplotableunitstring(dsetattrs["Unit"]))
                if not absolutetime:
                    axs[icol, irow].set_xlabel("Relative time in s")
                else:
                    axs[icol, irow].set_xlabel("Unixtime in s")
                axs[icol, irow].set_title(dataset.replace("_", " "))
                for i in np.arange(
                    self.datafile[self.dataGroupName + sensor + "/" + dataset].shape[0]
                ):
                    label = dsetattrs["Physical_quantity"][i]
                    data = self.datafile[self.dataGroupName + sensor + "/" + dataset][
                        i, idxs[0] : idxs[1]
                    ]
                    p = axs[icol, irow].plot(time, data, label=label)
                    sinparams = self.data[sensor][dataset]["SinPOpt"]
                    f0 = sinparams[i, 2]
                    dc = sinparams[i, 1]
                    amp = sinparams[i, 0]
                    phi = sinparams[i, 3]
                    sinelabel = label + " Sine Fit"
                    undisturbedsine = np.sin(2 * np.pi * f0 * time + phi) * amp + dc
                    axs[icol, irow].plot(
                        time,
                        undisturbedsine,
                        label=sinelabel,
                        color=p[0].get_color(),
                        ls="dotted",
                    )
                    axs[icol, irow].legend()
                    axs[icol, irow].grid()
                irow = irow + 1
            icol = icol + 1
        fig.show()

    def calculatetanloguephaseref1freq(
        self,
        refdatagroupname,
        refdataidx,
        analogrefchannelname,
        analogrefchannelidx,
        analogchannelquantity="Voltage",
    ):
        adcreftfname = analogrefchannelname
        adcreftfname = adcreftfname.replace("RAWDATA", "REFERENCEDATA")
        ADCTF = transferfunktion(self.datafile[adcreftfname]["Transferfunction"])
        for sensor in self.met4fofdatafile.sensordatasets:
            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                datasetrows = self.datafile[self.dataGroupName + sensor + "/" + dataset].shape[
                    0
                ]
                self.data[sensor][dataset]["Transfer_coefficients"] = {}
                TC = self.data[sensor][dataset]["Transfer_coefficients"][
                    self.datafile[refdatagroupname].attrs["Refference_Qauntitiy"]
                ] = {}
                TC["Magnitude"] = {}
                TC["Magnitude"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["Magnitude"]["value"][:] = np.NAN
                TC["Magnitude"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["Magnitude"]["uncertainty"][:] = np.NAN

                TC["Excitation_amplitude"] = {}
                TC["Excitation_amplitude"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["Excitation_amplitude"]["value"][:] = np.NAN
                TC["Excitation_amplitude"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["Excitation_amplitude"]["uncertainty"][:] = np.NAN

                TC["DUT_amplitude"] = {}
                TC["DUT_amplitude"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_amplitude"]["value"][:] = np.NAN
                TC["DUT_amplitude"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_amplitude"]["uncertainty"][:] = np.NAN


                TC["Phase"] = {}
                TC["Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["Phase"]["value"][:] = np.NAN
                TC["Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["Phase"]["uncertainty"][:] = np.NAN

                TC["DUT_Phase"] = {}
                TC["DUT_Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_Phase"]["value"][:] = np.NAN
                TC["DUT_Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_Phase"]["uncertainty"][:] = np.NAN

                TC["DUT_SNYNC_Phase"] = {}
                TC["DUT_SNYNC_Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_SNYNC_Phase"]["value"][:] = np.NAN
                TC["DUT_SNYNC_Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["DUT_SNYNC_Phase"]["uncertainty"][:] = np.NAN

                TC["SSU_ADC_Phase"] = {}
                TC["SSU_ADC_Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["SSU_ADC_Phase"]["value"][:] = np.NAN
                TC["SSU_ADC_Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["SSU_ADC_Phase"]["uncertainty"][:] = np.NAN

                TC["REF_Phase"] = {}
                TC["REF_Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["REF_Phase"]["value"][:] = np.NAN
                TC["REF_Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["REF_Phase"]["uncertainty"][:] = np.NAN

                TC["Frequency"] = {}
                TC["Frequency"]["value"] = np.zeros([datasetrows])
                TC["Frequency"]["value"][:] = np.NAN
                TC["Frequency"]["uncertainty"] = np.zeros([datasetrows])
                TC["Frequency"]["uncertainty"][:] = np.NAN
                TC["Excitation_frequency"] = {}
                TC["Excitation_frequency"]["value"] = np.zeros([datasetrows])
                TC["Excitation_frequency"]["value"][:] = np.NAN
                TC["Excitation_frequency"]["uncertainty"] = np.zeros([datasetrows])
                TC["Excitation_frequency"]["uncertainty"][:] = np.NAN
                for j in np.arange(0, datasetrows):
                    for i in np.arange(0, datasetrows):
                        if j == 0:
                            TC["Frequency"]["value"][i] = self.data[sensor][dataset][
                                "Sin_Fit_freq"
                            ][i]
                            TC["Excitation_frequency"]["value"][i] = self.datafile[
                                refdatagroupname
                            ]["Frequency"]["value"][i][refdataidx]
                        fitfreq = self.data[sensor][dataset]["Sin_Fit_freq"][j]
                        #print(refdataidx)
                        reffreq = self.datafile[refdatagroupname]["Frequency"]['value'][
                            i
                        ][refdataidx]
                        if fitfreq != reffreq:
                            warinigstr = (
                                "Frequency mismatach in Sesnor"
                                + sensor
                                + " "
                                + dataset
                                + " fit["
                                + str(i)
                                + "]= "
                                + str(fitfreq)
                                + " ref["
                                + str(refdataidx)
                                + "]= "
                                + str(reffreq)
                                + " Transferfunction will be invaladie !!"
                            )
                            warnings.warn(warinigstr, RuntimeWarning)
                        else:

                            # calculate magnitude response
                            TC["Excitation_amplitude"]["value"][j, i]       = self.datafile[refdatagroupname]["Excitation_amplitude"]["value"][j][refdataidx]
                            TC["Excitation_amplitude"]["uncertainty"][j, i] = self.datafile[refdatagroupname]["Excitation_amplitude"][ "uncertainty"][j][refdataidx]
                            ufexamp = ufloat(TC["Excitation_amplitude"]["value"][j, i],TC["Excitation_amplitude"]["uncertainty"][j, i])
                            if ufexamp == 0:
                                ufexamp = np.NaN
                            ufmeasamp = ufloat(
                                self.data[sensor][dataset]["SinPOpt"][i][0],
                                2*np.sqrt(self.data[sensor][dataset]["SinPCov"][i][0, 0]),
                            )
                            mag = ufmeasamp / ufexamp
                            TC["Magnitude"]["value"][j, i] = mag.n
                            TC["Magnitude"]["uncertainty"][j, i] = mag.s
                            TC["DUT_amplitude"]["value"][j, i] = ufmeasamp.n
                            TC["DUT_amplitude"]["uncertainty"][j, i] = ufmeasamp.s
                            # calculate phase
                            adcname = analogrefchannelname.replace(self.dataGroupName, "")

                            ufdutphase = ufloat(
                                self.data[sensor][dataset]["SinPOpt"][j][3],
                                2*np.sqrt(self.data[sensor][dataset]["SinPCov"][j][3, 3]),
                            )

                            ufanalogrefphase = ufloat(
                                self.data[adcname][analogchannelquantity]["SinPOpt"][
                                    analogrefchannelidx
                                ][3],
                                2*np.sqrt(self.data[adcname][analogchannelquantity]["SinPCov"][
                                    analogrefchannelidx
                                ][3, 3]),
                            )

                            ufADCTFphase = ADCTF.getNearestTF(analogrefchannelidx, fitfreq)['Phase']

                            ufrefphase = ufloat(
                                self.datafile[refdatagroupname]["Phase"]['value'][j][refdataidx]+np.pi,self.datafile[refdatagroupname]["Phase"]["uncertainty"][j][refdataidx]#+np.pi beause original data are velocitiy so deviation from sine is cos --> 90deg phase shift
                            )  # in rad
                            phase = (
                                ufdutphase
                                - (ufanalogrefphase + ufADCTFphase)
                                + ufrefphase
                            )
                            TC["DUT_Phase"]['value'][j, i] =ufdutphase.n
                            TC["DUT_Phase"]["uncertainty"][j, i] = ufdutphase.s
                            TC["REF_Phase"]['value'][j, i] =ufrefphase.n
                            TC["REF_Phase"]["uncertainty"][j, i] = ufrefphase.s
                            TC["SSU_ADC_Phase"]['value'][j, i]=ufADCTFphase.n
                            TC["SSU_ADC_Phase"]["uncertainty"][j, i]= ufADCTFphase.s
                            TC["DUT_SNYNC_Phase"]['value'][j, i]=ufanalogrefphase.n
                            TC["DUT_SNYNC_Phase"]["uncertainty"][j, i]= ufanalogrefphase.s
                            if phase.n < -np.pi:
                                phase += ufloat(2 * np.pi, 0)
                            elif phase.n > np.pi:
                                phase -= ufloat(2 * np.pi, 0)
                            TC["Phase"]["value"][j, i] = phase.n
                            TC["Phase"]["uncertainty"][j, i] = phase.s
        pass

    #TODO change for useing all experiments from all axes
    def calculateGPSRef1freqFromVelocity(
        self,
        refdatagroupname='0x00000200_OptoMet_Velocity_from_counts',
        refquantity='Velocity',
    ):
        if refquantity!='Velocity':
            raise KeyError("only Velocity is supported right no as input")
        for sensor in self.met4fofdatafile.sensordatasets:
            for dataset in self.met4fofdatafile.sensordatasets[sensor]:
                datasetrows = self.datafile[self.dataGroupName + sensor + "/" + dataset].shape[
                    0
                ]
                self.data[sensor][dataset]["Transfer_coefficients"] = {}
                TC = self.data[sensor][dataset]["Transfer_coefficients"]['Acceleration'] = {}
                TC["Magnitude"] = {}
                TC["Magnitude"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["Magnitude"]["value"][:] = np.NAN
                TC["Magnitude"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["Magnitude"]["uncertainty"][:] = np.NAN

                TC["Excitation_amplitude"] = {}
                TC["Excitation_amplitude"]["value"] = np.zeros(
                    [datasetrows, datasetrows]
                )
                TC["Excitation_amplitude"]["value"][:] = np.NAN
                TC["Excitation_amplitude"]["uncertainty"] = np.zeros(
                    [datasetrows, datasetrows]
                )
                TC["Excitation_amplitude"]["uncertainty"][:] = np.NAN
                TC["Phase"] = {}
                TC["Phase"]["value"] = np.zeros([datasetrows, datasetrows])
                TC["Phase"]["value"][:] = np.NAN
                TC["Phase"]["uncertainty"] = np.zeros([datasetrows, datasetrows])
                TC["Phase"]["uncertainty"][:] = np.NAN
                TC["Frequency"] = {}
                TC["Frequency"]["value"] = np.zeros([datasetrows])
                TC["Frequency"]["value"][:] = np.NAN
                TC["Frequency"]["uncertainty"] = np.zeros([datasetrows])
                TC["Frequency"]["uncertainty"][:] = np.NAN
                TC["Excitation_frequency"] = {}
                TC["Excitation_frequency"]["value"] = np.zeros([datasetrows])
                TC["Excitation_frequency"]["value"][:] = np.NAN
                TC["Excitation_frequency"]["uncertainty"] = np.zeros([datasetrows])
                TC["Excitation_frequency"]["uncertainty"][:] = np.NAN

                for j in np.arange(0, datasetrows):
                    for i in np.arange(0, datasetrows):
                        if j == 0:
                            TC["Frequency"]["value"][i] =self.data[sensor][dataset]["Sin_Fit_freq"][i]
                            TC["Excitation_frequency"]["value"][i] = self.data[refdatagroupname][refquantity]["Sin_Fit_freq"][i]
                        fitfreq = TC["Frequency"]["value"][i]
                        reffreq = TC["Excitation_frequency"]["value"][i]
                        if fitfreq != reffreq:
                            warinigstr = (
                                "Frequency mismatach in Sesnor"
                                + sensor
                                + " "
                                + dataset
                                + " fit["
                                + str(i)
                                + "]= "
                                + str(fitfreq)
                                + " ref["
                                + str(i)
                                + "]= "
                                + str(reffreq)
                                + " Transferfunction will be invaladie and is set to NaN!!"
                            )
                            warnings.warn(warinigstr, RuntimeWarning)
                        else:

                            # calculate magnitude response
                            TC["Excitation_amplitude"]["value"][j, i]       = self.data[refdatagroupname][refquantity]["SinPOpt"][j][0]*np.pi*2*reffreq
                            TC["Excitation_amplitude"]["uncertainty"][j, i] = 2*np.sqrt(self.data[refdatagroupname][refquantity]["SinPCov"][j][0, 0])
                            ufexamp = ufloat(TC["Excitation_amplitude"]["value"][j, i],TC["Excitation_amplitude"]["uncertainty"][j, i]) #v*2pi*f=a
                            if ufexamp == 0:
                                ufexamp = np.NaN
                            ufmeasamp = ufloat(
                                self.data[sensor][dataset]["SinPOpt"][i][0],
                                2*np.sqrt(self.data[sensor][dataset]["SinPCov"][i][0, 0])*2)
                            mag = ufmeasamp / ufexamp
                            TC["Magnitude"]["value"][j, i] = mag.n
                            TC["Magnitude"]["uncertainty"][j, i] = mag.s

                            ufdutphase = ufloat(
                                self.data[sensor][dataset]["SinPOpt"][i][3],
                                2*np.sqrt(self.data[sensor][dataset]["SinPCov"][i][3, 3])
                            )

                            ufrefphase = ufloat(
                                self.data[refdatagroupname][refquantity]["SinPOpt"][j][3]+np.pi*0.5,#ad 90 deg due to velocity to acceleration conversion
                                2*np.sqrt(self.data[refdatagroupname][refquantity]["SinPCov"][j][3, 3])
                            )

                            phase = (
                                ufdutphase
                                - ufrefphase# to check this
                            )
                            if phase.n < -np.pi:
                                phase += ufloat(2 * np.pi, 0)
                            elif phase.n > np.pi:
                                phase -= ufloat(2 * np.pi, 0)
                            TC["Phase"]["value"][j, i] = phase.n
                            TC["Phase"]["uncertainty"][j, i] = phase.s
                print(TC["Magnitude"])

    def saveToHdf(self):
        if not self.flags["saved_to_disk"]:
            experimentGroup = self.createHDFGroup()
            experimentGroup.attrs["Start_time"] = self.timepoints[0]
            experimentGroup.attrs["End_time"] = self.timepoints[1]
            experimentGroup.attrs["ID"] = self.experiemntID
            self.datafile.flush()
            Path("tmp").mkdir(parents=True, exist_ok=True)
            dd.io.save("tmp/" + self.experiemntID + ".hdf5", self.data)
            h5df = h5py_plain.File("tmp/" + self.experiemntID + ".hdf5", "r")
            for key in h5df.keys():
                self.datafile.copy(h5df[key], experimentGroup)
                experimentGroup[key].attrs["Start_index"] = self.idxs[key][0]
                experimentGroup[key].attrs["Stop_index"] = self.idxs[key][1]
                self.datafile.flush()
            self.flags["saved_to_disk"] = True
        else:
            raise RuntimeWarning("Data already written to hdf file. Skipping")


#TODO move this functions to different place
def generateCEMrefIDXfromfreqs(freqs, removefreqs=np.array([2000.0])):
    refidx = np.empty(0)
    for i in np.arange(freqs.size):
        if not freqs[i] in removefreqs:
            refidx = np.append(refidx, i)
            i = i + 1
    return refidx

def collectAndSortAccelerationVeloAsRef(hdffile,RefPathName='0x00000200_OptoMet_Velocity_from_counts/Velocity',DUTPathName='0xf1030002_MPU_9250/Acceleration',experimentGroup='EXPERIMENTS/Sine excitation'):
    data={}
    for key in hdffile[experimentGroup].keys():
        if 0==np.std(hdffile[experimentGroup][key][RefPathName]['Sin_Fit_freq'][:]):
            freq=np.mean(hdffile[experimentGroup][key][RefPathName]['Sin_Fit_freq'][:])
            exdata={'REF':{
                'SinPOpt':hdffile[experimentGroup][key][RefPathName]['SinPOpt'][:],
                'SinPCov': hdffile[experimentGroup][key][RefPathName]['SinPCov'][:]},
            'DUT': {
            'SinPOpt': hdffile[experimentGroup][key][DUTPathName]['SinPOpt'][:],
            'SinPCov': hdffile[experimentGroup][key][DUTPathName]['SinPCov'][:]}}
            if freq in data.keys():
               data[freq].append(exdata)
            else:
                data[freq]=[exdata]
    #print(data)
    return data

def getSensorRotationFromAcellVectors(data,DUTGroupDelay,freqsToUse=[10.0,20.0,30.0,40.0]):            #
    freqs=np.zeros(len(data.keys()))
    i=0
    magvectors={}
    phasevectors={}
    rots={}
    scaledREF=np.zeros([0, 3])
    scaledDUT = np.zeros([0, 3])
    for freq in data.keys():
        freqs[i]=float(freq)
        numex=len(data[freq])
        magvectors[freq]={'DUT':np.zeros([numex,3]),'REF':np.zeros([numex,3])}
        phasevectors[freq] = {'DUT': np.zeros([numex, 3]),
                              'REF': np.zeros([numex, 3]),
                              'DELTA': np.zeros([numex, 3]),
                              'SIGN': np.zeros([numex, 3])}
        for exIdx in range(numex):

            phasevectors[freq]['DUT'][exIdx,:]  =PhiDUT= data[freq][exIdx]['DUT']['SinPOpt'][:,3]
            phasevectors[freq]['REF'][exIdx, :] =PhiREF= data[freq][exIdx]['REF']['SinPOpt'][:,3]+(0.5*np.pi)
            phaseDelay = (2*np.pi*freq*DUTGroupDelay)
            DELTA=PhiDUT-PhiREF-phaseDelay
            phasevectors[freq]['DELTA'][exIdx, :]=DELTA
            phasevectors[freq]['DELTA'][exIdx, :]=np.arctan2(np.sin(DELTA),
                                                  np.cos(DELTA))
            rawSIGN =abs(np.arctan2(np.sin(DELTA),np.cos(DELTA)))>np.pi/2#0=+ 1=-
            rawSIGN=np.where(rawSIGN == 1, -1, rawSIGN)
            rawSIGN = np.where(rawSIGN == 0, 1, rawSIGN)
            phasevectors[freq]['SIGN'][exIdx, :] =rawSIGN

            magvectors[freq]['DUT'][exIdx,:]  = data[freq][exIdx]['DUT']['SinPOpt'][:,0]*rawSIGN
            magvectors[freq]['REF'][exIdx, :] = data[freq][exIdx]['REF']['SinPOpt'][:, 0]*2*np.pi*float(freq)

        magDUT = np.linalg.norm(magvectors[freq]['DUT'], axis=1)
        magREF = np.linalg.norm(magvectors[freq]['REF'], axis=1)
        aplitudeScaleFactor=np.mean(magREF/magDUT)
        rots[freq],rmsd=scipy.spatial.transform.Rotation.align_vectors(magvectors[freq]['DUT']*aplitudeScaleFactor,magvectors[freq]['REF'])
        if freq in freqsToUse:
            scaledREF = np.concatenate((scaledREF, magvectors[freq]['REF']))
            scaledDUT = np.concatenate((scaledDUT, magvectors[freq]['DUT']*aplitudeScaleFactor))
        #print(str(freq)+' '+str(aplitudeScaleFactor)+' '+str(rots[freq].as_euler('zyx', degrees=True))+' '+str(rmsd))
        i = i + 1
    averageRrots, Averagermsd = scipy.spatial.transform.Rotation.align_vectors(scaledREF,scaledDUT)
    print('Average from Freqs'+str(freqsToUse) +' ' +str(averageRrots.as_euler('zyx', degrees=True)) + ' ' + str(Averagermsd))
    print('Rotations as Quaternion'+str(averageRrots.as_quat()))
    return averageRrots,magvectors,phasevectors


def plotRotations(Rotations,Names,linestyles):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    numRotatiosn=len(Rotations)
    for i in range(numRotatiosn):
        ax.quiver(0, 0, 0,1,0,0,color='red')
        xrot=Rotations[i].apply([1,0,0])
        ax.quiver(0, 0, 0, xrot[0],xrot[1],xrot[2], color='red',linestyle=linestyles[i])

        ax.quiver(0, 0, 0, 0, 1, 0, color='green')
        yrot=Rotations[i].apply([0,1,0])
        ax.quiver(0, 0, 0, yrot[0],yrot[1],yrot[2], color='green',linestyle=linestyles[i])

        ax.quiver(0, 0, 0, 0, 0, 1, color='blue')
        zrot=Rotations[i].apply([0,0,1])
        ax.quiver(0, 0, 0, zrot[0],zrot[1],zrot[2], color='blue',linestyle=linestyles[i])
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ax.set_zlim([-1.1, 1.1])
    plt.show()


"""
BMAxphase = []
BMAyphase = []
BMAzphase = []
BMAfreq = []
for freq in BMAPhaseVecs.keys():
    for experiment in BMAPhaseVecs[freq]['DELTA']:
        BMAxphase.append(experiment[0])
        BMAyphase.append(experiment[1])
        BMAzphase.append(experiment[2])
        BMAfreq.append(float(freq))
plt.plot(BMAfreq, BMAzphase, 'x')
"""


def copyHFDatrrs(source, dest):
    for key in list(source.attrs.keys()):
        dest.attrs[key] = source.attrs[key]

def processdata(i):
    sys.stdout.flush()
    times = mpdata["movementtimes"][i]
    #refidx = int(mpdata["refidx"][i])
    #print("DONE i=" + str(i) + "refidx=" + str(refidx))
    times[0] += 12e9
    times[1] -= 2e9
    experiment = sineexcitation(
        mpdata["hdfinstance"],
        times,
        "{:05d}".format(i) + "Sine_Excitation"
        ,namePrefix='ROTATED_'
    )
    sys.stdout.flush()
    # print(experiment)
    sys.stdout.flush()

    start = time.time()
    experiment.dofft()
    #axisfreqs=mpdata['hdfinstance'].hdffile['REFERENCEDATA/Acceleration_refference']['Frequency']['value'][:, refidx]
    #axisfreqs=axisfreqs[axisfreqs != 0]#remove zero elements
    axisfreqs = mpdata["uniquexfreqs"]
    experiment.do3paramsinefits(axisfreqs, periods=10)
    end = time.time()
    # print("Sin Fit Time "+str(end - start))
    sys.stdout.flush()
    #experiment.calculateGPSRef1freqFromVelocity()
    #experiment.calculatetanloguephaseref1freq(
    #    "REFERENCEDATA/Acceleration_refference",
    #    refidx,
    #    "RAWDATA/0x1fe40a00_STM32_Internal_ADC",
    #    0,
    #)
    #print("DONE i=" + str(i) + "refidx=" + str(refidx))
    return experiment

if __name__ == "__main__":
    is1DPrcoessing = False
    is3DPrcoessing = False
    start = time.time()
    #CEM Filename and sensor Name
    #sensorname = '0xbccb0000_MPU_9250'
    #hdffilename = r"/media/benedikt/nvme/data/IMUPTBCEM/Messungen_CEM/MPU9250CEM.hdf5"
    #1dPrcoessing=True
    #PTB Filename and sensor Name
    #sensorname = '0x1fe40000_MPU_9250'
    #hdffilename = r"/media/benedikt/nvme/data/IMUPTBCEM/WDH3/MPU9250PTB.hdf5"
    # is1DPrcoessing=True
    #ZEMA 3 Komponent
    hdffilename='/media/benedikt/nvme/data/zema_dynamic_cal/tmp/zyx_250_10_delta_10Hz_50ms2max_WROT.hdf5'
    leadSensorname='0xf1030002_MPU_9250'
    is3DPrcoessing=True


    try:
        os.remove(hdffilename)
    except FileNotFoundError:
        pass
    shutil.copyfile(hdffilename.replace(".hdf5","(copy).hdf5"), hdffilename)


    datafile = h5py.File(hdffilename, "r+")

    test = hdfmet4fofdatafile(datafile,sensornames=['0x00000200_OptoMet_Velocity_from_counts','0xf1030002_MPU_9250', '0xf1030100_BMA_280','0x00000000_Kistler_8712A5M1'],dataGroupName='ROTATED')#

    movementidx, movementtimes = test.detectmovment('RAWDATA/'+leadSensorname+'/Acceleration', 'RAWDATA/'+leadSensorname+'/Absolutetime', treshold=0.7,blocksinrow=10, blocksize=1000, plot=True)
    numofexperiemnts=movementtimes.shape[0]

    if is1DPrcoessing:
        manager = multiprocessing.Manager()
        mpdata = manager.dict()
        mpdata['hdfinstance'] = test
        mpdata['movementtimes'] = movementtimes
        mpdata['lock'] = manager.Lock()

        # PTB Data CALCULATE REFERENCE data index skipping one data set at the end of evry loop

        mpdata['refidx'] = np.zeros([16 * 10])
        refidx = np.zeros([17 * 10])
        for i in np.arange(10):
            refidx[i * 17:(i + 1) * 17] = np.arange(17) + i * 18
        mpdata['refidx'] = refidx


        freqs = test.hdffile['REFERENCEDATA/Acceleration_refference/Frequency']['value'][2, :]
        # CEM Data
        #refidx = generateCEMrefIDXfromfreqs(freqs)
        mpdata['refidx'] = refidx

        unicefreqs = np.unique(freqs, axis=0)
        mpdata['uniquexfreqs'] = unicefreqs

        i = np.arange(numofexperiemnts)
        results=process_map(processdata, i, max_workers=15)

        freqs = np.zeros(numofexperiemnts)
        mag = np.zeros(numofexperiemnts)
        maguncer = np.zeros(numofexperiemnts)
        examp = np.zeros(numofexperiemnts)
        rawamp = np.zeros(numofexperiemnts)
        phase = np.zeros(numofexperiemnts)
        phaseuncer = np.zeros(numofexperiemnts)
        output = {'freqs': freqs,'mag': mag, 'maguncer': maguncer, 'examp': examp,  'phase': phase,
                 'phaseuncer': phaseuncer}
        df = pd.DataFrame(output)
        for i in range(len(results)):
            ex=results[i]
            ex.saveToHdf()
            mag[i] = ex.data[leadSensorname]['Acceleration']['Transfer_coefficients']['Acceleration']['Magnitude']['value'][2,2]
            maguncer[i] = ex.data[leadSensorname]['Acceleration']['Transfer_coefficients']['Acceleration']['Magnitude']['uncertainty'][2,2]
            examp[i] = ex.data[leadSensorname]['Acceleration']['Transfer_coefficients']['Acceleration']['Excitation_amplitude']['value'][2,2]
            freqs[i] = ex.data[leadSensorname]['Acceleration']['SinPOpt'][2][2]
            rawamp[i] = ex.data[leadSensorname]['Acceleration']['SinPOpt'][2][0]
            phase[i] = ex.data[leadSensorname]['Acceleration']['Transfer_coefficients']['Acceleration']['Phase']['value'][2,2]
            phaseuncer[i] = ex.data[leadSensorname]['Acceleration']['Transfer_coefficients']['Acceleration']['Phase']['uncertainty'][2,2]

        TF=getRAWTFFromExperiemnts(leadSensorname+["EXPERIMENTS/Sine excitation"],leadSensorname)
        test.addrawtftohdffromexpreiments(datafile["EXPERIMENTS/Sine excitation"], leadSensorname)
        test.hdffile.flush()
        test.hdffile.close()
    if is3DPrcoessing:
        manager = multiprocessing.Manager()
        mpdata = manager.dict()
        mpdata['hdfinstance'] = test
        mpdata['movementtimes'] = movementtimes
        mpdata['lock'] = manager.Lock()

        unicefreqs = np.array(
            [250, 240, 230, 220, 210, 200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30,
             20, 10])
        mpdata['uniquexfreqs'] = unicefreqs
        i = np.arange(numofexperiemnts)
        #i = np.arange(8)
        processdata(0)
        results = process_map(processdata, i, max_workers=15)
        for i in range(len(results)):
            ex = results[i]
            ex.saveToHdf()

        AccelvectorDictMPU9250 = collectAndSortAccelerationVeloAsRef(datafile,experimentGroup='EXPERIMENTS/ROTATED_Sine excitation')#
        MPU9250Rotation,MPUMagVecs,MPUPhaseVecs = getSensorRotationFromAcellVectors(AccelvectorDictMPU9250,DUTGroupDelay=-0.0015107382732839475)
        #MPU9250Rotation=scipy.spatial.transform.Rotation.from_quat([-0.70226073,0.71191207,-0.00244556, -0.002257  ])
        AccelvectorDictBMA280 = collectAndSortAccelerationVeloAsRef(datafile,DUTPathName='0xf1030100_BMA_280/Acceleration',experimentGroup='EXPERIMENTS/ROTATED_Sine excitation')#,experimentGroup='EXPERIMENTS/ROTATED_Sine excitation'
        BMARotation,BMAMagVecs,BMAPhaseVecs = getSensorRotationFromAcellVectors(AccelvectorDictBMA280,DUTGroupDelay=-0.00055)
        #BMARotation=scipy.spatial.transform.Rotation.from_quat([0.01361723, 0.01303785, 0.70243922, 0.71149401])
        LaserVibroRotation = scipy.spatial.transform.Rotation.from_quat([0, 0, 0, 1])# the laser interferrometer need no transformation since its the target coordinate frame
        KistlerRotation = scipy.spatial.transform.Rotation.from_quat([0, 0, 0, 1])  # we don't know any thing asuming sensor is not tilted
        #CDTF = datafile.create_group('COORDTRANSFORMED')
    """
        rotationsDict={'0x00000200_OptoMet_Velocity_from_counts':{'origin':'0x00000200_OptoMet_Velocity_from_counts',
                                                                  'target':'0x00000200_OptoMet_Velocity_from_counts',
                                                                  'axis':'xyz',
                                                                  'rotation':LaserVibroRotation},
                       '0xf1030002_MPU_9250': {'origin': '0xf1030002_MPU_9250',
                                                                   'target': '0x00000200_OptoMet_Velocity_from_counts',
                                                                    'axis': 'xyz',
                                                                   'rotation': MPU9250Rotation},
                       '0xf1030100_BMA_280': {'origin': '0xf1030100_BMA_280',
                                                                    'target': '0x00000200_OptoMet_Velocity_from_counts',
                                                                    'axis': 'xyz',
                                                                    'rotation': BMARotation},
                       '0x00000000_Kistler_8712A5M1':{'origin': '0x00000000_Kistler_8712A5M1',
                                                                    'target': '0x00000200_OptoMet_Velocity_from_counts',
                                                                    'axis': '00z',#sensor is One Dimensional along Z axis we will convert to 3D date with zeros along x and y
                                                                    'rotation': KistlerRotation}
                       }

        # create rotaded Data
        GPRROTDATA=datafile.create_group('ROTATED')
        timeAndSampleNumberKeys = [
            "Absolutetime",
            "Absolutetime_uncertainty",
            "Sample_number",
        ]
        for sensorName in rotationsDict.keys():
            DSETGROP=GPRROTDATA.create_group(sensorName)
            copyHFDatrrs(datafile['RAWDATA'][sensorName], DSETGROP)
            DSETGROP.attrs['rotation_origin']=rotationsDict[sensorName]['origin']
            DSETGROP.attrs['rotation_target']=rotationsDict[sensorName]['target']
            DSETGROP.attrs['rotation_axis']=rotationsDict[sensorName]['axis']
            DSETGROP.attrs['rotation_quaternios']=rotationsDict[sensorName]['rotation'].as_quat()
            DSETGROP.attrs['rotation_euler_zyx']=rotationsDict[sensorName]['rotation'].as_euler('zyx', degrees=True)
            desteKeys=list(datafile['RAWDATA'][sensorName].keys())
            measurmentDataNames=list(set(desteKeys).difference(set(timeAndSampleNumberKeys)))
            for timeAndSampleNumberKey in timeAndSampleNumberKeys:
                dset=DSETGROP.create_dataset(timeAndSampleNumberKey,data=datafile['RAWDATA'][sensorName][timeAndSampleNumberKey]         ,
                                                    dtype = datafile['RAWDATA'][sensorName][timeAndSampleNumberKey].dtype,
                                                    compression = "gzip",
                                                    shuffle = True,
                                                    chunks = True)
                copyHFDatrrs(datafile['RAWDATA'][sensorName][timeAndSampleNumberKey],dset)
            for measDataName in measurmentDataNames:
                dimensions=datafile['RAWDATA'][sensorName][measDataName].shape[0]
                if dimensions==3 and rotationsDict[sensorName]['axis']=='xyz':
                    dset = DSETGROP.create_dataset(measDataName ,
                                                   data=np.transpose(rotationsDict[sensorName]['rotation'].apply(np.transpose(datafile['RAWDATA'][sensorName][measDataName]))),                    #rotate data
                                                    maxshape = (3, None),
                                                    dtype = datafile['RAWDATA'][sensorName][measDataName].dtype,
                                                    compression = "gzip",
                                                    shuffle = True,
                                                    chunks=True)# we use auto chunking since we know the overall langth in advance
                    copyHFDatrrs(datafile['RAWDATA'][sensorName][measDataName], dset)
                if dimensions==1:
                    if rotationsDict[sensorName]['axis']== 'xyz':
                        #TODO IMPLEMENT axis handling for each dataset but this will be done in the future
                        #OK the data are 3D but this Dset is 1D asuming it's temeprature so we do nothing
                        dset = DSETGROP.create_dataset(measDataName ,
                                                       data=datafile['RAWDATA'][sensorName][measDataName],
                                                        maxshape = (1, None),
                                                        dtype = datafile['RAWDATA'][sensorName][measDataName],
                                                        compression = "gzip",
                                                        shuffle = True,
                                                        chunks = True)  # we use auto chunking since we know the overall langth in advance
                        copyHFDatrrs(datafile['RAWDATA'][sensorName][measDataName],dset)
                    else:
                        length=datafile['RAWDATA'][sensorName][measDataName].shape[1]
                        data=np.zeros([3,length])
                        if rotationsDict[sensorName]['axis']== 'x00':
                            data[0,:]=datafile['RAWDATA'][sensorName][measDataName]
                        if rotationsDict[sensorName]['axis'] == '0y0':
                            data[1, :] = datafile['RAWDATA'][sensorName][measDataName]
                        if rotationsDict[sensorName]['axis']== '00z':
                            data[2,:]=datafile['RAWDATA'][sensorName][measDataName][:]
                        dset = DSETGROP.create_dataset(measDataName ,
                                                       data=np.transpose(rotationsDict[sensorName]['rotation'].apply(np.transpose(data))),
                                                        maxshape = (3, None),
                                                        dtype = datafile['RAWDATA'][sensorName][measDataName],
                                                        compression = "gzip",
                                                        shuffle = True,
                                                        chunks = True)  # we use auto chunking since we know the overall langth in advance
                        copyHFDatrrs(datafile['RAWDATA'][sensorName][measDataName],dset)
                        physicalQuant=datafile['RAWDATA'][sensorName][measDataName].attrs["Physical_quantity"][0]
                        if rotationsDict[sensorName]['axis'] == 'x00':
                            dset.attrs["Physical_quantity"]=['X '+physicalQuant,
                                                             ' (Y not Measured)'+physicalQuant,
                                                             '(Z not Measured)'+physicalQuant]
                        if rotationsDict[sensorName]['axis'] == '0y0':
                            dset.attrs["Physical_quantity"] = ['(X not Measured) ' + physicalQuant ,
                                                               'Y ' +physicalQuant,
                                                               '(Z not Measured)'+ physicalQuant]
                        if rotationsDict[sensorName]['axis'] == '00z':
                            dset.attrs["Physical_quantity"]=['(X not Measured)'+physicalQuant,
                                                             ' (Y not Measured)'+physicalQuant,
                                                             'Z'+physicalQuant]
    """
    datafile.flush()
    datafile.close()

