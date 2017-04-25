#!/usr/bin/env python
# Michael Saunby. April 2013
#
# Notes.
# pexpect uses regular expression so characters that have special meaning
# in regular expressions, e.g. [ and ] must be escaped with a backslash.
#
#   Copyright 2013 Michael Saunby
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pexpect
import sys
import time
import os
import logging
import logging.config
from sensor_calcs import *
import json
import select
import BLE_MQTT_GATEWAY as gateway
import threading
import traceback
from DEVICE import SensorTag

fullpath = os.path.abspath(sys.argv[0])
pathname = os.path.dirname(fullpath)
index = len(fullpath) - fullpath[::-1].index('/') -1 
log_file = fullpath[index+1:-3] + ".log"
log_dir = pathname[0:-4] + "/log/"

try:
    f = open(log_dir + log_file, 'r')
except IOError:
    f = open(log_dir + log_file, 'w')
f.close()
    
logging.config.fileConfig('logging.conf', defaults={'logfilename': log_dir + log_file})
logger = logging.getLogger("exampleApp")

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(120)
    
DEVICE_NAME = "TI Sensor Tag C2541"
MAC_ADDRESS = "78:C5:E5:6E:58:D1"
DEVICE_TYPE = "NULL"

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["sensorTag/temperature/rate"]
MQTT_PUBLISHING_TOPIC = ["sensorTag/temperature"]
SENSORTAG_POLLING_RATE = {"temperature": 5}
event = threading.Event()
VERBOSE = 0
barometer = None
datalog = sys.stdout

class MQTT_delegate(object):
    def __init__(self):
        pass

    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
            
    def handleNotification(self, client, uerdata, msg):
        #logger.info(msg.topic+" "+str(msg.payload))
        pass

def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

def TMP006_thread(client, tag):
    while True:
        tag.char_write_cmd(0x29,0x01)
        time.sleep(SENSORTAG_POLLING_RATE['temperature'])
    
class SensorCallbacks:

    data = {}

    def __init__(self,addr, MQTT_CLIENT, tag):
        self.data['addr'] = addr
        self.client = MQTT_CLIENT
        self.tag = tag

    def tmp006(self,v):
        self.tag.char_write_cmd(0x29,0x00)
        objT = (v[1]<<8)+v[0]
        ambT = (v[3]<<8)+v[2]
        print "v: ", v
        print objT
        print ambT
#         time.sleep(100)  
        targetT = calcTmpTarget(objT, ambT)
        self.data['t006'] = int(targetT)
        print "T006 %.1f" % int(targetT)
        if(int(targetT) > 3):
            self.client.publish(MQTT_PUBLISHING_TOPIC[0], int(targetT))

    def accel(self,v):
        (xyz,mag) = calcAccel(v[0],v[1],v[2])
        self.data['accl'] = xyz
        print "ACCL", xyz

    def humidity(self, v):
        rawT = (v[1]<<8)+v[0]
        rawH = (v[3]<<8)+v[2]
        (t, rh) = calcHum(rawT, rawH)
        self.data['humd'] = [t, rh]
        print "HUMD %.1f" % rh

    def baro(self,v):
        global barometer
        global datalog
        rawT = (v[1]<<8)+v[0]
        rawP = (v[3]<<8)+v[2]
        (temp, pres) =  self.data['baro'] = barometer.calc(rawT, rawP)
        print "BARO", temp, pres
        self.data['time'] = long(time.time() * 1000);
        # The socket or output file might not be writeable
        # check with select so we don't block.
        (re,wr,ex) = select.select([],[datalog],[],0)
        if len(wr) > 0:
            datalog.write(json.dumps(self.data) + "\n")
            datalog.flush()
            pass

    def magnet(self,v):
        x = (v[1]<<8)+v[0]
        y = (v[3]<<8)+v[2]
        z = (v[5]<<8)+v[4]
        xyz = calcMagn(x, y, z)
        self.data['magn'] = xyz
        print "MAGN", xyz

    def gyro(self,v):
        print "GYRO", v
        
    def keyPress(self, v):
        button = str(v[0]<<8)
        if(button == "512"):
            logger.infl("Button 1 pressed.")
            self.client.publish("sensorTag/button", '1')
        elif(button == "256"):
            logger.info("Button 2 pressed.")
            self.client.publish("sensorTag/button", '2')       

def main():
    global datalog
    global barometer

    bluetooth_adr = sys.argv[1]
    #data['addr'] = bluetooth_adr
    if len(sys.argv) > 2:
        datalog = open(sys.argv[2], 'w+')
        
    mqtt_delegate = MQTT_delegate()
    mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
    threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        
    while True:
     try:   
      print "[re]starting.."

      tag = SensorTag(bluetooth_adr)
      cbs = SensorCallbacks(bluetooth_adr, mqtt_gateway.client, tag)

#     enable TMP006 sensor
#       tag.register_cb(0x25,cbs.tmp006)
#       tag.char_write_cmd(0x26,0x0100) 
#       threading.Thread(target=TMP006_thread,args=(mqtt_gateway.client,tag,)).start()
# 
#       # enable accelerometer
#       tag.register_cb(0x2d,cbs.accel)
#       tag.char_write_cmd(0x31,0x01)
#       tag.char_write_cmd(0x2e,0x0100)
# 
#       # enable humidity
#       tag.register_cb(0x38, cbs.humidity)
#       tag.char_write_cmd(0x3c,0x01)
#       tag.char_write_cmd(0x39,0x0100)
# 
#       # enable magnetometer
#       tag.register_cb(0x40,cbs.magnet)
#       tag.char_write_cmd(0x44,0x01)
#       tag.char_write_cmd(0x41,0x0100)
# 
#       # enable gyroscope
#       tag.register_cb(0x57,cbs.gyro)
#       tag.char_write_cmd(0x5b,0x07)
#       tag.char_write_cmd(0x58,0x0100)
# 
#       # fetch barometer calibration
#       tag.char_write_cmd(0x4f,0x02)
#       rawcal = tag.char_read_hnd(0x52)
#       barometer = Barometer( rawcal )
#       # enable barometer
#     tag.register_cb(0x4b,cbs.baro)
#     tag.char_write_cmd(0x4f,0x01)
#     tag.char_write_cmd(0x4c,0x0100)

         # enable key press notification
      tag.register_cb(0x5f, cbs.keyPress)
      tag.char_write_cmd(0x60, 0x0100)
      tag.notification_loop()
     except:
#       pass
      print traceback.format_exc()  

if __name__ == "__main__":
    main()

