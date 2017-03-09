#!/usr/bin/python
import sys
import os
import BLE_MQTT_GATEWAY as gateway
import bluepy
import threading
import binascii
import time
import logging
import logging.config
import multiprocessing

fullpath = os.path.abspath(sys.argv[0])
pathname = os.path.dirname(fullpath)
index = len(fullpath) - fullpath[::-1].index('/') -1 
log_file = fullpath[index+1:-3] + ".log"
log_dir = pathname[0:-4] + "/log/"
src_dir = str(pathname[0:-4] + "/src/")

try:
    f = open(log_dir + log_file, 'r')
except IOError:
    f = open(log_dir + log_file, 'w')
f.close()
    
logging.config.fileConfig(src_dir + 'logging.conf', defaults={'logfilename': log_dir + log_file})
logger = logging.getLogger("exampleApp")

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(1)

DEVICE_NAME = "Twin Led"
MAC_ADDRESS = "04:A3:16:9B:0E:DB"
DEVICE_TYPE = "NULL"
BLE_HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["bean/twinLed/1", "bean/twinLed/2"]
VERBOSE = 0
BLE_lock = threading.Lock()

class MQTT_delegate(object):
    def __init__(self):
        pass

    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        if(msg.topic == MQTT_SUBSCRIBING_TOPIC[0]):
            t1 = threading.Thread(target = ble_gateway.data_updater,args=(BLE_HANDLE[0],msg.payload)).start()
        elif(msg.topic == MQTT_SUBSCRIBING_TOPIC[1]):
            t1 = threading.Thread(target = ble_gateway.data_updater,args=(BLE_HANDLE[1],msg.payload)).start()

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        mqtt_gateway.add_diagnostic(ble_gateway)
        mqtt_delegate.addBLE(ble_gateway)
        multiprocessing.Process(target=mqtt_gateway.client.loop_forever).start()
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise
    

