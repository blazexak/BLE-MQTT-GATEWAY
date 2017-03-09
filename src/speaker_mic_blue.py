#!/usr/bin/python
import sys
import os
import BLE_MQTT_GATEWAY as gateway
import threading
import time
import logging
import logging.config
import traceback
from DEVICE import Bluetooth_Speaker_Mic

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
    time.sleep(120)

DEVICE_NAME = "Bluetooth Speaker MPHBS01"
MAC_ADDRESS = "00:00:01:04:33:71"
DEVICE_TYPE = "NULL"
PLAYBACK_DIR = "/home/pi/git-repos/BLE-MQTT-GATEWAY/audio/dir1/"
RECORD_DIR = "/home/pi/git-repos/BLE-MQTT-GATEWAY/audio/dir2/"

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["multimedia/speaker", "multimedia/microphone"]
MQTT_PUBLISHING_TOPIC = ["multimedia/message_box", "multimedia/recording_event", "multimedia/playback_event"]
RECORDING_TIME = 30
VERBOSE = 0
multimedia_event = threading.Event()

class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def addMultimedia(self, MULTIMEDIA):
        self.multimedia = MULTIMEDIA
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        if(msg.topic == "multimedia/speaker"):
            if(multimedia_event.is_set() == False):
                multimedia_event.set()
                self.multimedia.playback(DELETE = True, CLIENT=client, TOPIC=MQTT_PUBLISHING_TOPIC[2])
                f = self.multimedia.file_available(PLAYBACK_DIR)
                if(f == False):
                    client.publish("multimedia/message_box", '0')
                multimedia_event.clear()
                print "End"
        elif(msg.topic == "multimedia/microphone"):
            if(multimedia_event.is_set() == False):
                multimedia_event.set()
                self.multimedia.record(COUNTDOWN=RECORDING_TIME, IP_ADDRESS = "192.168.1.17", CLIENT=client,TOPIC=MQTT_PUBLISHING_TOPIC[1])
                multimedia_event.clear()
                
def audio_check_thread(client, multimedia, delay):
    while True:
        try:
            f = multimedia.file_available(PLAYBACK_DIR)
            if(f == False):
				client.publish("multimedia/message_box", '0')
            elif(f == True):
                client.publish("multimedia/message_box", '1')
            time.sleep(delay)
        except:
            logger.info("Exception caught in audio check thread.")
            logger.info(sys.exc_info()[0])
            logger.info(traceback.format_exc())	
                            

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        multimedia = Bluetooth_Speaker_Mic(DEVICE_NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR	)
        mqtt_delegate.addMultimedia(multimedia)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        threading.Thread(target=audio_check_thread, name="Audio Check Thread",args=(mqtt_gateway.client, multimedia,10)).start()
        print("Thread started.")
        
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise        
