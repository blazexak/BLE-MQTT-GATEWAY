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

DEVICE_NAME = "Neo Strip"
MAC_ADDRESS = "98:7B:F3:58:2E:78"
DEVICE_TYPE = "NULL"
BLE_HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["bean/neoStrip/hsb", "bean/neoStrip/mode"]
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
            state, hsb = check_HSB(msg.payload)
            if(state == True):
                with BLE_lock:
                    writer = threading.Thread(target = ble_gateway.data_updater,args=(BLE_HANDLE[0],msg.payload))
                    writer.start()
                    while( writer.is_alive() == True):
                        pass
                    print "Exit thread"
                    
        elif(msg.topic == MQTT_SUBSCRIBING_TOPIC[1]):
            with BLE_lock:
                writer = threading.Thread(target = ble_gateway.data_updater,args=(BLE_HANDLE[4],msg.payload))
                writer.start()
                while( writer.is_alive() == True):
                    pass
                print "Exit thread"            
 
# Function for checking HSV string format: "HHH,SSS,BBB"
# All H,S,B must be integer between 0-255, otherwise invalid
def check_HSB(msg):
    # Check if msg is in the format: device_name/payload
    if(msg.find('/') != -1):
        msg = msg.split('/')[1]
        # Check for position of comma in HSV string
        if(len(msg) == 11 and msg.count(',') == 2 and msg.index(',',1,4) == 3 and msg.index(',',5,11) == 7):
            # Check for H,S,B are all numeric
            hsv = msg.split(',')
            if(hsv[0].isdigit() and hsv[1].isdigit() and hsv[2].isdigit()):
                # Check if HSB are between 0-255
                if(int(hsv[0]) >= 0 and int(hsv[0]) < 256 and int(hsv[1]) >= 0 and int(hsv[1]) < 256 and int(hsv[2]) >= 0 and int(hsv[2]) < 256 ):
                    return True, msg
                else:
                    return False, -1
            else:
                return False, -2
        else:
            return False, -3
            
    elif(len(msg) == 11 and msg.count(',') == 2 and msg.index(',',1,4) == 3 and msg.index(',',5,11) == 7):
        # Check for H,S,B are all numeric
        hsv = msg.split(',')
        if(hsv[0].isdigit() and hsv[1].isdigit() and hsv[2].isdigit()):
            # Check if HSB are between 0-255
            if(int(hsv[0]) >= 0 and int(hsv[0]) < 256 and int(hsv[1]) >= 0 and int(hsv[1]) < 256 and int(hsv[2]) >= 0 and int(hsv[2]) < 256 ):
                return True, msg
            else:
                return False, -4
        else:
            return False, -5
    else:
        return False, -6

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise
    

