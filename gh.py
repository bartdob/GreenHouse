#  /usr/bin/python
#  -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import serial   #odczytywanie danych po usb
import time
import datetime
from func import *
from conn import ConnectDB, CloseDB # database method

print('Start program')
time.sleep(5)
zerowanieDB()
print("po zerowaniu")
print("data arduino")

reset=0


while True:
    Counter = Counter +1	
    print("Counter: ", Counter)
    dataFromArduino()
    DetectionFrontType()
    Lamp()
    time.sleep(1)
    now = time.strftime("%H:%M")
    if Counter == 2:
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        dataFromArduino()
        DetectionFrontType()
        Counter = 0
    if now == "00:00" and reset==0:
        ser.write('CPRESET')
        reset=1
    if  now == "00:01" and reset==1:   
        reset=0
    time.sleep(5)