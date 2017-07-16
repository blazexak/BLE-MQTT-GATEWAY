#!/usr/bin/python

import sys
import os
import threading
import BLE_MQTT_GATEWAY as gateway
import bluepy
import time
import binascii
import logging
import logging.config

fullpath = os.path.abspath(sys.argv[0])
pathname = os.path.dirname(fullpath)
index = len(fullpath) - fullpath[::-1].index('/') -1 
log_file = fullpath[index+1:-3] + ".log"
log_dir = str(pathname[0:-4] + "/log/")
src_dir = str(pathname[0:-4] + "/src/")
print log_dir
print log_file
try:
    f = open(log_dir + log_file, 'r')
except IOError:
    f = open(log_dir + log_file, 'w')
f.close()
    
logging.config.fileConfig(src_dir + '/logging.conf', defaults={'logfilename': log_dir + log_file})
logger = logging.getLogger("exampleApp")

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(120)

DEVICE_NAME = "Bean Twin Button"
DEVICE_CODE = "button_bean/"
MAC_ADDRESS = "50:65:83:6d:b2:2e"
DEVICE_TYPE = "NULL"
BLE_DELEGATE_HANDLE = [52, 56]
HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "127.0.0.1"
MQTT_SUBSCRIBING_TOPIC = []
MQTT_PUBLISHING_TOPIC = ["bean/button1", "bean/button2"]
VERBOSE = 1

class BLE_delegate(bluepy.btle.DefaultDelegate):
    def __init__(self, mqtt_client):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.client = mqtt_client
        
    def binasciiToString(self, data):
        data = binascii.b2a_hex(data)
        data = data[0:2]
        data = str(int(data,16))
        return data
        
    def handleNotification(self, cHandle, data):
        if(VERBOSE == 1):
            logger.info("Data: " + data)
            logger.info("Handle: " + str(cHandle))
        
        if(cHandle == 51):
            logger.info("Button 1 pressed.")
            self.client.publish(MQTT_PUBLISHING_TOPIC[0], data[0])
        elif(cHandle == 55):
            logger.info("Button 2 pressed.")
            self.client.publish(MQTT_PUBLISHING_TOPIC[1], data[0])            
        # if(cHandle)
        # self.client.publish(MQTT_PUBLISHING_TOPIC[0], data[0])
        
class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
    
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload)) 

    
if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_delegate = BLE_delegate(mqtt_gateway.client)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        event_stop = threading.Event()
        mqtt_gateway.add_diagnostic(ble_gateway)
        t1 = threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_DELEGATE_HANDLE,event_stop))
        t1.start()
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        
        while True:
            time.sleep(0.001)

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupted")
        event_stop.set()
        t1.join()
        mqtt_gateway.client.disconnect()
        logger.info("Exiting script.")
        sys.exit()

    except:
#         sys.exit()
        raise        
