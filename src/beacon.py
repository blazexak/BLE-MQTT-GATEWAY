import yaml
import sys
import os
import time
import logging
import threading
import logging.config
import BLE_MQTT_GATEWAY as gateway
from bluepy.btle import Scanner, DefaultDelegate
from BLE_MQTT_GATEWAY import BLE_ADVERTISEMENT_GATEWAY

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = []

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
    
beacon_gateway = BLE_ADVERTISEMENT_GATEWAY()
beacons = beacon_gateway.load_configuration_file("config.yaml")

print "Type: ", type(beacons), "Length: ", len(beacons), "Payload: ", beacons

class ScanDelegate(DefaultDelegate):
    def __init__(self, mqtt_client):
        DefaultDelegate.__init__(self)
        self.client = mqtt_client
        
    def handleDiscovery(self, dev, isNewDev, isNewData):
        for key in beacons.keys():
            if beacons[key]['mac_add'].lower() == dev.addr and isNewData:
                data = dev.getScanData()
                if(len(data) == 3 and len(data[2][2]) == 50):
                    # print "New Data received from listed beacons."
                    # print "MAC_ADDRESS: ", dev.addr
                    # print "Raw Data: ", data
                    # print "Data type: ", type(data), "Length: ", len(data)
                    # print "Data: ", data[2][2], "Len: ", len(data[2][2])
                    # print ""
                    # print "Temp: ", beacon_gateway.minor_low(data[2][2])
                    # print "Moisture: ", beacon_gateway.minor_high(data[2][2])
                    # print " "
                    low_byte = beacon_gateway.minor_low(data[2][2])
                    high_byte = beacon_gateway.minor_high(data[2][2])
                    byte = [high_byte, low_byte]
                    # print "byte: ", byte
                    for topic, i in zip(beacons[key]['mqtt_topics'], range(2)):
                        if topic[1] == True:
                            mqtt_topic = beacons[key]['name']+'/'+ topic[0]
                            print "Published: " + mqtt_topic + "\tPayload: " + byte[i]
                            print ""
                            self.client.publish(mqtt_topic, byte[i])
                    break
      
def main():
    try:
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC)
        scanner = Scanner().withDelegate(ScanDelegate(mqtt_gateway.client))
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            devices = scanner.scan(5.0)

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        logger.info("Exiting script.")
        sys.exit()              

if __name__ == "__main__":
    main()      
