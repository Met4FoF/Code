import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# from termcolor import colored
scalefactor=4
SMALL_SIZE = 8*scalefactor
MEDIUM_SIZE = 10*scalefactor
BIGGER_SIZE = 12*scalefactor

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)
plt.rc('lines', linewidth=scalefactor)
#plt.rc("text", usetex=True)

DataSet1={'Name':'Sensor 1 X-Axis','fmt':'s','color':'darkblue','Data':pd.read_csv(r'D:\data\processed\200621_MPU_9250_X_Achse_5\200621_MPU_9250_X_Achse_5TF.csv')}
DataSet3={'Name':'Sensor 1 X-Axis','fmt':'s','color':'navy','Data':pd.read_csv(r'D:\data\processed\200622_MPU_9250_X_Achse_6\200622_MPU_9250_X_Achse_6TF.csv')}
DataSet2={'Name':'Sensor 2 X-Axis','fmt':'s','color':'orange','Data':pd.read_csv(r'D:\data\processed\200622_MPU_9250_SN_12_X_Achse_2\200622_MPU_9250_SN_12_X_Achse_2TF.csv')}
DataSet4={'Name':'Sensor 2 X-Axis','fmt':'s','color':'darkorange','Data':pd.read_csv(r'D:\data\processed\200623_MPU_9250_SN_12_X_Achse_3_COLAREF\200623_MPU_9250_SN_12_X_Achse_3_COLAREFTF.csv')}
DataSet5={'Name':'Sensor 2 X-Axis','fmt':'s','color':'gold','Data':pd.read_csv(r'D:\data\processed\200625_MPU_9250_SN_12_X_Achse_1_COLAREF\200625_MPU_9250_SN_12_X_Achse_1_COLAREFTF.csv')}
DataSet6={'Name':'Sensor 1 Y-Axis','fmt':'*','color':'mediumblue','Data':pd.read_csv(r'D:\data\processed\200620_MPU_9250_Y_Achse_5\200620_MPU_9250_Y_Achse_5TF.csv')}
DataSet7={'Name':'Sensor 2 Y-Axis','fmt':'*','color':'sandybrown','Data':pd.read_csv(r'D:\data\processed\200623_MPU_9250_SN_12_Y_Achse_1_COLAREF\200623_MPU_9250_SN_12_Y_Achse_1_COLAREFTF.csv')}
DataSetList=[DataSet1,DataSet2,DataSet3,DataSet4,DataSet5,DataSet6,DataSet7]
AMPMean=np.zeros(DataSet1['Data']['Frequencys'].size)
for DataSet in DataSetList:
    AMPMean+=DataSet['Data']['AmplitudeCoefficent']
AMPMean/=len(DataSetList)

fig, ax = plt.subplots()
ax.set_xscale("log", nonposx='clip')
ax.set(xlabel=r"Frequency $f$ in Hz", ylabel=r" $|S(f)|-\overline{|S(f)|}$" )#, title="Deviation of magnitudes Response from average value per frequency"
i=0
fScale=0.01
for DataSet in DataSetList:
    ax.errorbar(DataSet['Data']['Frequencys']*(1+(fScale*i)),DataSet['Data']['AmplitudeCoefficent']-AMPMean,yerr=DataSet['Data']['AmplitudeCoefficentUncer'],label=DataSet['Name'],fmt=DataSet['fmt'],color=DataSet['color'],markersize=scalefactor*5)
    i=i+1
ax.legend(ncol=2)
fig.show()


PhaseMean=np.zeros(DataSet1['Data']['PhaseDeg'].size)
for DataSet in DataSetList:
    AMPMean+=DataSet['Data']['PhaseDeg']
AMPMean/=len(DataSetList)

fig, ax = plt.subplots()
ax.set_xscale("log", nonposx='clip')
ax.set(xlabel=r"Frequency $f$ in Hz", ylabel=r"$\Delta\varphi(f)-\overline{\Delta\varphi(f)}$ in deg")#, title="Deviation of phase response from average value per frequency"
i=0
fScale=0.01
for DataSet in DataSetList:
    ax.errorbar(DataSet['Data']['Frequencys']*(1+(fScale*i)),DataSet['Data']['PhaseDeg']-AMPMean,yerr=DataSet['Data']['PhaseUncerDeg'],label=DataSet['Name'],fmt=DataSet['fmt'],color=DataSet['color'],markersize=scalefactor*5)
    i=i+1
ax.legend(ncol=2)
fig.show()