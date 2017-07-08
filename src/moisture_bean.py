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
    
logging.config.fileConfig(src_dir + 'logging.conf', defaults={'logfilename': log_dir + log_file}, disable_existing_loggers=False)
logger = logging.getLogger("exampleApp")

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(120)

DEVICE_NAME = "Moisture Sensor"
MAC_ADDRESS = "04:A3:16:9A:F3:37"
DEVICE_TYPE = "NULL"
BLE_DELEGATE_HANDLE = [52,56]
HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["bean/moisture/rate"]
MQTT_PUBLISHING_TOPIC = ["bean/moisture", "bean/moisture/temperature"]
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
        index = HANDLE.index(cHandle)
        payload = self.binasciiToString(data)
        self.client.publish(MQTT_PUBLISHING_TOPIC[index], payload)
        
        if(VERBOSE == 1):
            logger.info("Data: " + payload)
            logger.info("Handle: " + str(cHandle))        
        
class MQTT_delegate(object):
    def __init__(self):
        pass

    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        
        if(msg.topic == MQTT_SUBSCRIBING_TOPIC[0]):
            self.ble_gateway.set_polling_rate(HANDLE[4], msg.payload)
            
    def diagnostic(self):
        self.ble_gateway.set_data(HANDLE[3], 1) 

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_delegate = BLE_delegate(mqtt_gateway.client)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        
        mqtt_gateway.add_diagnostic(ble_gateway)
        event_stop = threading.Event()
        t1 = threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_DELEGATE_HANDLE, event_stop))
        t1.start()
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupted")
        event_stop.set()
        t1.join()
        mqtt_gateway.client.disconnect()
        logger.info("Exiting script.")
        sys.exit()
    except:
        raise
    

