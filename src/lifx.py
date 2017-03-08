
#!/usr/bin/python
from lifxlan import *
import BLE_MQTT_GATEWAY as gateway
import sys
import os
import threading
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

MAC_ADDRESS = "d0:73:d5:01:13:e1"
IP_ADDRESS = "192.168.1.8"
MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["lifx/power", "lifx/hsbk"]
VERBOSE = 0
BLE_lock = threading.Lock()
light = Light(MAC_ADDRESS, IP_ADDRESS)

class MQTT_delegate(object):
    def __init__(self):
        pass

    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        
        if(msg.topic == "lifx/power"):
            light.set_power(int(msg.payload),0,True)
        elif(msg.topic == "lifx/hsbk"):
            hsbk = msg.payload.split(",")
            hsbk = map(int, hsbk)
            print hsbk, type(hsbk), len(hsbk)
            light.set_color(hsbk)        
            
        

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise