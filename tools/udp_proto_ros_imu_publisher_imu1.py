#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 11:21:54 2019

@author: seeger01
"""

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Imu
from struct import *
import socket
import csv
import messages_pb2

LOGFILENAME = "log_files/k050HZTekAFG3101ext10MHz"
ACCLOGFILENAME = LOGFILENAME + "acc.csv"
GPSLOGFILENAME = LOGFILENAME + "gpst.csv"
SYNCLOGFILENAME = LOGFILENAME + "SYNC.csv"
LOGGINENABLED = True
UDP_IP = "192.168.2.100"
UDP_PORT = 7000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.bind((UDP_IP, UDP_PORT))

# TODO Add dict with Board IDs


def imu_publisher():
    """
    This function receives UDP Packages from the Met4FoF Board and Publisehs ROS-IMU Msg.

    Returns
    -------
    None.

    """
    pub_imu0 = rospy.Publisher("IMU0", Imu, queue_size=20)
    pub_imu1 = rospy.Publisher("IMU1", Imu, queue_size=20)
    pub_ref = rospy.Publisher("REF_sensor_z", Imu, queue_size=20)
    rospy.init_node("imu_publisher1", anonymous=True)
    while not rospy.is_shutdown():
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        ProtoData = messages_pb2.DataMessage()
        ProtoData.ParseFromString(data)
        # print(ProtoData)
        imu_msg = Imu()
        imu_msg.header.seq = ProtoData.sample_number
        imu_msg.header.stamp = rospy.Time(
            ProtoData.unix_time, ProtoData.unix_time_nsecs
        )
        imu_msg.linear_acceleration.x = ProtoData.Data_01
        imu_msg.linear_acceleration.y = ProtoData.Data_02
        imu_msg.linear_acceleration.z = ProtoData.Data_03
        imu_msg.angular_velocity.x = ProtoData.Data_04
        imu_msg.angular_velocity.y = ProtoData.Data_05
        imu_msg.angular_velocity.z = ProtoData.Data_06
        if int(ProtoData.id / 65536) == 13616:
            imu_msg.header.frame_id = "IMU0"
            pub_imu0.publish(imu_msg)
            imu_msg_ref = Imu()
            imu_msg_ref.header.frame_id = "REF"
            imu_msg_ref.header.seq = ProtoData.sample_number
            imu_msg_ref.header.stamp = rospy.Time(
                ProtoData.unix_time, ProtoData.unix_time_nsecs
            )
            imu_msg_ref.linear_acceleration.z = ProtoData.Data_11
            pub_ref.publish(imu_msg_ref)
        if int(ProtoData.id / 65536) == 14128:
            imu_msg.header.frame_id = "IMU1"
            pub_imu1.publish(imu_msg)


if __name__ == "__main__":
    try:
        imu_publisher()
    except rospy.ROSInterruptException:
        pass
