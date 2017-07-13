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

DEVICE_NAME = "E-Ink Display"
MAC_ADDRESS = "04:A3:16:9B:0D:0D"
DEVICE_TYPE = "NULL"
BLE_HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "127.0.0.1"
MQTT_SUBSCRIBING_TOPIC = ["bean/eink"]
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
            eink_msg = splitMsg(msg.payload)
            with BLE_lock:
                writer = threading.Thread(target = ble_gateway.data_updater,args=(BLE_HANDLE,eink_msg))
                writer.start()
                while( writer.is_alive() == True):
			time.sleep(1)
                print "Exit thread"

# Function for splitting message into substring to fit eink's screen size
# Return: A list which contains the number of strings to print to each line of the screen    
def splitMsg(msg):
    space = 18
    i = 0
    wordSplit = msg.split()
    wordCount = len(msg.split())
    
    eink_msg = list()
    for x in range(5):
        eink_msg.append('')
        
    for n in range(wordCount):
        if(len(wordSplit[n]) <= space):
            if(len(eink_msg[i]) == 0):
                eink_msg[i] = wordSplit[n]
                space = space - (len(wordSplit[n])+1)
            else:
                eink_msg[i] = eink_msg[i] + " " + wordSplit[n]
                space = space - (len(wordSplit[n])+1)
        else:
            space = 18
            i = i + 1
            eink_msg[i] = wordSplit[n]
            space = space - len(wordSplit[n])
            
    for y in range(5):
        if(eink_msg[y] == ''):
            eink_msg[y] = " "
            
    return eink_msg 

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            time.sleep(0.001)

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise
    

