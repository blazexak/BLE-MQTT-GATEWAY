#!/usr/bin/python
import sys
import os
import BLE_MQTT_GATEWAY as gateway
import threading
import time
import logging
import logging.config
from DEVICE import Bluetooth_Speaker_Mic

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

DEVICE_NAME = "Bluetooth Speaker MPHBS01"
MAC_ADDRESS = "00:00:01:04:33:71"
DEVICE_TYPE = "NULL"
PLAYBACK_DIR = "/home/pi/git-repos/BLE-MQTT-GATEWAY/audio/"
RECORD_DIR = "/home/pi/git-repos/BLE-MQTT-GATEWAY/audio/"

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["multimedia/speaker", "multimedia/microphone"]
VERBOSE = 0
BLE_lock = threading.Lock()

class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def addMultimedia(self, MULTIMEDIA):
        self.multimedia = MULTIMEDIA
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        if(msg.topic == "multimedia/speaker"):
            with BLE_lock:
                self.multimedia.playback(DELETE = True)
        elif(msg.topic == "multimedia/microphone"):
            with BLE_lock:
                self.multimedia.record(COUNTDOWN=30)

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        multimedia = Bluetooth_Speaker_Mic(DEVICE_NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR)
        mqtt_delegate.addMultimedia(multimedia)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        print("Thread started.")
        
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise        
