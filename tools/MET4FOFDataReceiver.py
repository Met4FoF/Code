#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 09:20:12 2019

Data receiver for Met4FoF Protobuff Data
@author: seeger01
"""

import sys
import traceback
import os
import socket
import threading
import messages_pb2
import google.protobuf as pb
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
from datetime import datetime
import threading
import time
from multiprocessing import Queue
import copy

class DataReceiver:
    def __init__(self, IP, Port):
        self.flags = {"Networtinited": False}
        self.params = {"IP": IP, "Port": Port, "PacketrateUpdateCount": 10000}
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM  # Internet
        )  # UDP
        try:
            self.socket.bind((IP, Port))
        except OSError as err:
            print("OS error: {0}".format(err))
            if err.errno == 99:
                print(
                    "most likely no network card of the system has the ip address"
                    + str(IP)
                    + " check this with >>> ifconfig on linux or with >>> ipconfig on Windows"
                )
            if err.errno == 98:
                print(
                    "an other task is blocking the connection on linux use >>> sudo netstat -ltnp | grep -w ':"
                    + str(Port)
                    + "' on windows use in PowerShell >>> Get-Process -Id (Get-NetTCPConnection -LocalPort "
                    + str(Port)
                    + ").OwningProcess"
                )
            raise (err)
            # we need to raise an exception to prevent __init__ from returning
            # otherwise a broken class instance will be created
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise ("Unexpected error:", sys.exc_info()[0])
        self.flags["Networtinited"] = True
        self.AllSensors = {}
        self.ActiveSensors = {}
        self.msgcount = 0
        self.lastTimestamp = 0
        self.Datarate = 0
        self._stop_event = threading.Event()
        thread = threading.Thread(target=self.run, args=())
        thread.start()

    def stop(self):
        print("Stopping DataReceiver")
        self._stop_event.set()
        # wait 1 second to ensure that all ques are empty before closing them
        # other wise SIGPIPE is raised by os
        # IMPORVEMNT use signals for this
        time.sleep(1)
        for key in self.AllSensors:
            self.AllSensors[key].stop()
        self.socket.close()

    def run(self):
        # implement stop routine
        while not self._stop_event.is_set():
            data, addr = self.socket.recvfrom(1500)  # buffer size is 1024 bytes
            wasValidData = False
            wasValidDescription = False
            ProtoData = messages_pb2.DataMessage()
            ProtoDescription = messages_pb2.DescriptionMessage()
            SensorID = 0
            BytesProcessed = 4  # we need an offset of 4 sice
            if data[:4] == b"DATA":
                while BytesProcessed < len(data):
                    msg_len, new_pos = _DecodeVarint32(data, BytesProcessed)
                    BytesProcessed = new_pos

                    try:
                        msg_buf = data[new_pos : new_pos + msg_len]
                        ProtoData.ParseFromString(msg_buf)
                        wasValidData = True
                        SensorID = ProtoData.id
                        message = {'ProtMsg':copy.deepcopy(ProtoData),'Type':'Data'}
                        BytesProcessed += msg_len
                    except:
                        pass  # ? no exception for wrong data type !!
                    if not (wasValidData or wasValidDescription):
                        print("INVALID PROTODATA")
                        pass  # invalid data leave parsing routine

                    if SensorID in self.AllSensors:
                        try:
                            self.AllSensors[SensorID].buffer.put_nowait(message)
                        except:
                            print("packet lost for sensor ID:" + str(SensorID))
                    else:
                        self.AllSensors[SensorID] = Sensor(SensorID)
                        print("FOUND NEW SENSOR WITH ID=hex" + hex(SensorID)+'==>dec:'+str(SensorID))
                    self.msgcount = self.msgcount + 1

                    if self.msgcount % self.params["PacketrateUpdateCount"] == 0:
                        print(
                            "received "
                            + str(self.params["PacketrateUpdateCount"])
                            + " packets"
                        )
                        if self.lastTimestamp != 0:
                            timeDIFF = datetime.now() - self.lastTimestamp
                            timeDIFF = timeDIFF.seconds + timeDIFF.microseconds * 1e-6
                            self.Datarate = (
                                self.params["PacketrateUpdateCount"] / timeDIFF
                            )
                            print("Update rate is " + str(self.Datarate) + " Hz")
                            self.lastTimestamp = datetime.now()
                        else:
                            self.lastTimestamp = datetime.now()
            elif data[:4] == b"DSCP":
                while BytesProcessed < len(data):
                    msg_len, new_pos = _DecodeVarint32(data, BytesProcessed)
                    BytesProcessed = new_pos
                    try:
                        msg_buf = data[new_pos : new_pos + msg_len]
                        ProtoDescription.ParseFromString(msg_buf)
                        print(msg_buf)
                        wasValidData = True
                        SensorID = ProtoDescription.id
                        message = {'ProtMsg':ProtoDescription,'Type':'Description'}
                        BytesProcessed += msg_len
                    except:
                        pass  # ? no exception for wrong data type !!
                    if not (wasValidData or wasValidDescription):
                        print("INVALID PROTODATA")
                        pass  # invalid data leave parsing routine

                    if SensorID in self.AllSensors:
                        try:
                            self.AllSensors[SensorID].buffer.put_nowait(message)
                        except:
                            print("packet lost for sensor ID:" + hex(SensorID))
                    else:
                        self.AllSensors[SensorID] = Sensor(SensorID)
                        print("FOUND NEW SENSOR WITH ID=hex" + hex(SensorID)+' dec==>:'+str(SensorID))
                    self.msgcount = self.msgcount + 1

                    if self.msgcount % self.params["PacketrateUpdateCount"] == 0:
                        print(
                            "received "
                            + str(self.params["PacketrateUpdateCount"])
                            + " packets"
                        )
                        if self.lastTimestamp != 0:
                            timeDIFF = datetime.now() - self.lastTimestamp
                            timeDIFF = timeDIFF.seconds + timeDIFF.microseconds * 1e-6
                            self.Datarate = (
                                self.params["PacketrateUpdateCount"] / timeDIFF
                            )
                            print("Update rate is " + str(self.Datarate) + " Hz")
                            self.lastTimestamp = datetime.now()
                        else:
                            self.lastTimestamp = datetime.now()
            else:
                print("unrecognized packed preamble"+str(data[:5]))

    def getsenorIDs(self):
        return [*self.AllSensors]

    def __del__(self):
        self.socket.close()


### classes to proces sensor descriptions
class AliasDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.aliases = {}

    def __getitem__(self, key):
        return dict.__getitem__(self, self.aliases.get(key, key))

    def __setitem__(self, key, value):
        return dict.__setitem__(self, self.aliases.get(key, key), value)

    def add_alias(self, key, alias):
        self.aliases[alias] = key

class ChannelDescription:
   def __init__(self,CHID):
       self.Description={"CHID":CHID,
                         "PHYSICAL_QUANTITY":'Not Set',
                         "UNIT":'Not Set',
                         "UNCERTAINTY_TYPE":'Not Set',
                         "RESOLUTION":'Not Set',
                         "MIN_SCALE":'Not Set',
                         "MAX_SCALE":'Not Set'}
   def __getitem__(self, key):
       #if key='SpecialKey':
       # self.Description['SpecialKey']
       return self.Description[key]

   def __str__(self):
         return 'Channel: '+str(self.Description["CHID"])+' ==>'+str(self.Description["PHYSICAL_QUANTITY"])+' in '+str(self.Description["UNIT"])
   #todo override set methode
   def setDescription(self,key,value):
       self.Description[key]=value

class SensorDescription:
    def __init__(self,ID,SensorName):
        self.ID=ID
        self.SensorName=SensorName
        self._complete=False
        self.Channels=AliasDict([])
    def setChannelParam(self,CHID,key,value):
        if CHID in self.Channels:
            self.Channels[CHID].setDescription(key,value)
            if(key=='PHYSICAL_QUANTITY'):
                self.Channels.add_alias(CHID,value)#make channels callable by their Quantity
        else:
            if(key=='PHYSICAL_QUANTITY'):
                self.Channels.add_alias(CHID,value)#make channels callable by their Quantity
            self.Channels[CHID]=ChannelDescription(CHID)
            self.Channels[CHID].setDescription(key,value)
            self.Channels.add_alias(CHID,'Data_'+'{:02d}'.format(CHID))#make channels callable by ther Data_xx name
    def __getitem__(self, key):
       #if key='SpecialKey':
       # self.Description['SpecialKey']
       return self.Channels[key]

class Sensor:
    StrFieldNames=['str_Data_01','str_Data_02','str_Data_03','str_Data_04','str_Data_05','str_Data_06','str_Data_07','str_Data_08','str_Data_09',
                                 'str_Data_10','str_Data_11','str_Data_12','str_Data_13','str_Data_14','str_Data_15','str_Data_16']
    FFieldNames=['f_Data_01','f_Data_02','f_Data_03','f_Data_04','f_Data_05','f_Data_06','f_Data_07','f_Data_08','f_Data_09',
                                 'f_Data_10','f_Data_11','f_Data_12','f_Data_13','f_Data_14','f_Data_15','f_Data_16']
    DescriptionTypNames={0:"PHYSICAL_QUANTITY",1:"UNIT",2:"UNCERTAINTY_TYPE",3:"RESOLUTION",4:"MIN_SCALE",5:"MAX_SCALE"}
    # TODO implement multi therading and callbacks
    def __init__(self, ID, BufferSize=1e4):
        self.Description=SensorDescription(ID,'Name not Set')
        self.buffer = Queue(int(BufferSize))
        self.flags = {
            "DumpToFile": False,
            "PrintProcessedCounts": True,
            "callbackSet": False,
        }
        self.params = {"ID": ID, "BufferSize": BufferSize, "DumpFileName": ""}
        self.DescriptionsProcessed=AliasDict({"PHYSICAL_QUANTITY":False,
                         "UINT":False,
                         "UNCERTAINTY_TYPE":False,
                         "RESOLUTION":False,
                         "MIN_SCALE":False,
                         "MAX_SCALE":False})
        for i in range(6):
            self.DescriptionsProcessed.add_alias(self.DescriptionTypNames[i],i)
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run, args=())
        # self.thread.daemon = True
        self.thread.start()
        self.ProcessedPacekts = 0
        self.lastPacketTimestamp = datetime.now()
        self.deltaT = (
            self.lastPacketTimestamp - datetime.now()
        )  # will b 0 but has deltaTime type witch is intended
        self.datarate = 0

    def StartDumpingToFile(self, filename):
        # check if the path is valid
        # if(os.path.exists(os.path.dirname(os.path.abspath('data/dump.csv')))):
        self.Dumpfile = open(filename, "a")
        self.params["DumpFileName"] = filename
        self.flags["DumpToFile"] = True

    def StopDumpingToFile(self):
        self.flags["DumpToFile"] = False
        self.params["DumpFileName"] = ""
        self.Dumpfile.close()

    def run(self):
        lastpackedId=0
        while not self._stop_event.is_set():
            # problem when we are closing the queue this function is waiting for data and raises EOF error if we delet the q
            # work around adding time out so self.buffer.get is returning after a time an thestop_event falg can be checked
            try:
                message = self.buffer.get(timeout=0.1)
                tmpTime = datetime.now()
                #self.deltaT = (
                #    tmpTime - self.lastPacketTimestamp
                #)  # will b 0 but has deltaTime type witch is intended
                #self.datarate = 1 / (self.deltaT.seconds + 1e-6 * self.deltaT.microseconds)
                #self.lastPacketTimestamp = datetime.now()
                self.ProcessedPacekts = self.ProcessedPacekts + 1
                if self.flags["PrintProcessedCounts"]:
                    if self.ProcessedPacekts % 10000 == 0:
                        print(
                            "processed 10000 packets in receiver for Sensor ID:"
                            + hex(self.params["ID"])
                        )
                if message['Type']=='Description':
                    Description=message['ProtMsg']
                    try:
                        if not any(self.DescriptionsProcessed.values())and Description.IsInitialized():
                            #run only if no description packed has been procesed ever
                            #self.Description.SensorName=message.Sensor_name
                            print('Found new '+Description.Sensor_name+' sensor with ID:'+str(self.params['ID']))
                            print(str(Description.Description_Type))
                        if self.DescriptionsProcessed[Description.Description_Type]==False :
                            #we havent processed thiss message before now do that
                            if Description.Description_Type in [0,1,2]:#["PHYSICAL_QUANTITY","UINT","UNCERTAINTY_TYPE"]
                                #print(Description)
                                #string Processing

                                FieldNumber=1
                                for StrField in self.StrFieldNames:
                                    if Description.HasField(StrField):
                                        self.Description.setChannelParam(FieldNumber,self.DescriptionTypNames[Description.Description_Type],Description.__getattribute__(StrField))
                                        print(str(FieldNumber)+' '+Description.__getattribute__(StrField))
                                    FieldNumber=FieldNumber+1

                                self.DescriptionsProcessed[Description.Description_Type]=True
                                print(self.DescriptionsProcessed)
                            if Description.Description_Type in [3,4,5]:#["RESOLUTION","MIN_SCALE","MAX_SCALE"]
                                self.DescriptionsProcessed[Description.Description_Type]=True
                                FieldNumber=1
                                for FloatField in self.FFieldNames:
                                    if Description.HasField(FloatField):
                                        self.Description.setChannelParam(FieldNumber,self.DescriptionTypNames[Description.Description_Type],Description.__getattribute__(StrField))
                                        print(str(FieldNumber)+' '+str(Description.__getattribute__(FloatField)))

                                    FieldNumber=FieldNumber+1
                                print(self.DescriptionsProcessed)
                                #string Processing
                    except Exception:
                        print (" Sensor id:"+hex(self.params["ID"])+"Exception in user Description parsing:")
                        print('-'*60)
                        traceback.print_exc(file=sys.stdout)
                        print('-'*60)
                if self.flags["callbackSet"]:
                    if(message['Type']=='Data'):
                        try:
                            self.callback(message['ProtMsg'])
                        except Exception:
                            print (" Sensor id:"+hex(self.params["ID"])+"Exception in user callback:")
                            print('-'*60)
                            traceback.print_exc(file=sys.stdout)
                            print('-'*60)
                            pass
            except Exception:
                pass

    def SetCallback(self, callback):
        self.flags["callbackSet"] = True
        self.callback = callback

    def UnSetCallback(self,):
        self.flags["callbackSet"] = False
        self.callback = doNothingCb

    def stop(self):
        print("Stopping Sensor " + hex(self.params["ID"]))
        self._stop_event.set()
        # sleeping until run function is exiting due to timeout
        time.sleep(0.2)
        # thrash all data in queue
        while not self.buffer.empty():
            try:
                self.buffer.get(False)
            except:
                pass
        self.buffer.close()

    def join(self, *args, **kwargs):
        self.stop()

def DumpDataMPU9250(message):
    filename='data/DataDump.log'
    if not (os.path.exists(filename)):
        dumpfile = open(filename, "a+")
        dumpfile.write("id;sample_number;unix_time;unix_time_nsecs;time_uncertainty;ACC_x;ACC_y,;ACC_z,;GYR_x;GYR_y;GYR_z;MAG_x;MAG_y;MAG_z;TEMP;ADC_1;ADC_2;ADC_3\n")
    else:
        dumpfile = open(filename, "a")        
    PRINTDEVIDER=10000
    dumpfile.write(str(message.id)+';'+
                   str(message.sample_number)+';'+
                   str(message.unix_time)+';'+
                   str(message.unix_time_nsecs)+';'+
                   str(message.time_uncertainty)+';'+
                   str(message.Data_01)+';'+
                   str(message.Data_02)+';'+
                   str(message.Data_03)+';'+
                   str(message.Data_04)+';'+
                   str(message.Data_05)+';'+
                   str(message.Data_06)+';'+
                   str(message.Data_07)+';'+
                   str(message.Data_08)+';'+
                   str(message.Data_09)+';'+
                   str(message.Data_10)+';'+
                   str(message.Data_11)+';'+
                   str(message.Data_12)+';'+
                   str(message.Data_13)+';'+
                   "\n")
    # if(message.sample_number%PRINTDEVIDER==0):
    #     print('=====DATA PACKET====','\n',
    #       hex(message.id),message.sample_number,message.unix_time,message.unix_time_nsecs,message.time_uncertainty,
    #       '\n ACC:',message.Data_01,message.Data_02,message.Data_03,
    #       '\n GYR:',message.Data_04,message.Data_05,message.Data_06,
    #       '\n MAG:',message.Data_07,message.Data_08,message.Data_09,
    #       '\n TEMP:',message.Data_10,
    #       '\n ADC:',message.Data_11,message.Data_12,message.Data_13),

def DumpDataGPSDummySensor(message):
    if not (os.path.exists('data/GPSLog.log')):
        dumpfile = open('data/GPSLog.log', "a+")
        dumpfile.write("id;sample_number;unix_time;unix_time_nsecs;time_uncertainty;GPSCount\n")
    else:
        dumpfile = open('data/GPSLog', "a")
        #2^48=281474976710656 2^32=4294967296 2^16=65536
        gpscount=message.Data_01*281474976710656+message.Data_02*4294967296+message.Data_03*65536+message.Data_04
        print(hex(message.id),message.sample_number,message.unix_time,message.unix_time_nsecs,message.time_uncertainty,gpscount)
        dumpfile.write(str(message.id)+';'+
                       str(message.sample_number)+';'+
                       str(message.unix_time)+';'+
                       str(message.unix_time_nsecs)+';'+
                       str(message.time_uncertainty)+';'+
                       str(gpscount)+"\n")

def doNothingCb():
    pass

def openDumpFile():
    filename='data/DataDump.log'
    if not (os.path.exists(filename)):
        dumpfile = open(filename, "a+")
        dumpfile.write("id;sample_number;unix_time;unix_time_nsecs;time_uncertainty;ACC_x;ACC_y,;ACC_z,;GYR_x;GYR_y;GYR_z;MAG_x;MAG_y;MAG_z;TEMP;ADC_1;ADC_2;ADC_3\n")
    else:
        dumpfile = open(filename, "a")

#Example for DSCP Messages
# Quant b'\x08\x80\x80\xac\xe6\x0b\x12\x08MPU 9250\x18\x00"\x0eX Acceleration*\x0eY Acceleration2\x0eZ Acceleration:\x12X Angular velocityB\x12Y Angular velocityJ\x12Z Angular velocityR\x17X Magnetic flux densityZ\x17Y Magnetic flux densityb\x17Z Magnetic flux densityj\x0bTemperature'
# Unit  b'\x08\x80\x80\xac\xe6\x0b\x12\x08MPU 9250\x18\x01"\x17\\metre\\second\\tothe{-2}*\x17\\metre\\second\\tothe{-2}2\x17\\metre\\second\\tothe{-2}:\x18\\radian\\second\\tothe{-1}B\x18\\radian\\second\\tothe{-1}J\x18\\radian\\second\\tothe{-1}R\x0c\\micro\\teslaZ\x0c\\micro\\teslab\x0c\\micro\\teslaj\rdegreecelsius'
# Res   b'\x08\x80\x80\xac\xe6\x0b\x12\x08MPU 9250\x18\x03\xa5\x01\x00\x00\x80G\xad\x01\x00\x00\x80G\xb5\x01\x00\x00\x80G\xbd\x01\x00\x00\x80G\xc5\x01\x00\x00\x80G\xcd\x01\x00\x00\x80G\xd5\x01\x00\xf0\x7fG\xdd\x01\x00\xf0\x7fG\xe5\x01\x00\xf0\x7fG\xed\x01\x00\x00\x80G'
# Min   b'\x08\x80\x80\xac\xe6\x0b\x12\x08MPU 9250\x18\x04\xa5\x01\x16\xea\x1c\xc3\xad\x01\x16\xea\x1c\xc3\xb5\x01\x16\xea\x1c\xc3\xbd\x01\xe3\xa0\x0b\xc2\xc5\x01\xe3\xa0\x0b\xc2\xcd\x01\xe3\xa0\x0b\xc2\xd5\x01\x00\x00\x00\x80\xdd\x01\x00\x00\x00\x80\xe5\x01\x00\x00\x00\x80\xed\x01\xf3j\x9a\xc2'
# Max   b'\x08\x80\x80\xac\xe6\x0b\x12\x08MPU 9250\x18\x05\xa5\x01\xdc\xe8\x1cC\xad\x01\xdc\xe8\x1cC\xb5\x01\xdc\xe8\x1cC\xbd\x01\xcc\x9f\x0bB\xc5\x01\xcc\x9f\x0bB\xcd\x01\xcc\x9f\x0bB\xd5\x01\x00\x00\x00\x00\xdd\x01\x00\x00\x00\x00\xe5\x01\x00\x00\x00\x00\xed\x01\x02)\xeeB'