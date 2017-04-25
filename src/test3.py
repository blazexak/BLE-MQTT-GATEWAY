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
import re
import struct

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

if(len(sys.argv) == 1):
    print "Need at least two argument."
    sys.exit()
elif(len(sys.argv) == 2 and re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", sys.argv[1].lower())):
    print "Second input is valid MAC Address."
    MAC_ADDRESS = sys.argv[1]
else:
    print "Invalid arguments."
    sys.exit()
    
HANDLE = []
DEVICE_NAME = "Sensor Tag"
DEVICE_TYPE = ""
# DELEGATE LIST:
#     BUTTON: 96
BLE_DELEGATE_HANDLE = [38,96]
MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = []
MQTT_PUBLISHING_TOPIC = []
VERBOSE = 1
tosigned = lambda n: float(n-0x10000) if n>0x7fff else float(n)
tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)
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
#         payload = self.binasciiToString(data)
        print cHandle, data, self.binasciiToString(data)
        (objT, ambT) = struct.unpack('<hh', data)
        objT = tosigned(objT)
        ambT = tosigned(ambT)
        m_tmpAmb = ambT/128.0
        Vobj2 = objT * 0.00000015625
        Tdie2 = m_tmpAmb + 273.15
        S0 = 6.4E-14            # Calibration factor
        a1 = 1.75E-3
        a2 = -1.678E-5
        b0 = -2.94E-5
        b1 = -5.7E-7
        b2 = 4.63E-9
        c2 = 13.4
        Tref = 298.15
        S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
        Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
        fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
        tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
        tObj = (tObj - 273.15)
        print "Object temp: ", tObj        
#         if(cHandle == 95):
#             index = HANDLE.index(cHandle)
#             payload = self.binasciiToString(data)
#             (result, mid) = self.client.publish(MQTT_PUBLISHING_TOPIC[0] , DEVICE_CODE + payload)
#             print "Pubish result: ", result
#             
#         if(VERBOSE == 1):
#             logger.info("Data: " + self.binasciiToString(data))
#             logger.info("Handle: " + str(cHandle))
            
class MQTT_delegate(object):
    def __init__(self):
        pass

    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
            
    def handleNotification(self, client, uerdata, msg):
        logger.info(msg.topic+" "+str(msg.payload))
        
        if(msg.topic == MQTT_SUBSCRIBING_TOPIC[0]):
            self.ble_gateway.set_polling_rate(HANDLE[4], msg.payload)
                
def sensorTimer(ble_gateway, handle, polling_rate):
    #enable sensor
    # wait for x seconds
    # disable sensors
    # time.sleep(polling_rate)
    while True:
        print "sensor timer started"
        ble_gateway.set_data(handle, struct.pack("B", 0x01))
#         time.sleep(1.5)
#         ble_gateway.set_data(handle, struct.pack("B", 0x00))
#         print "going to sleep"
#         time.sleep(polling_rate)    
    

if(__name__ == "__main__"):
    try:
        mqtt_delegate = MQTT_delegate()
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, mqtt_delegate.handleNotification)
        ble_delegate = BLE_delegate(mqtt_gateway.client)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        mqtt_gateway.add_diagnostic(ble_gateway)
        threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_DELEGATE_HANDLE,)).start()
        ble_gateway.set_data(41, struct.pack("B", 0x01))
#         tmp006 = threading.Thread(target = sensorTimer, args=(ble_gateway, 41, 0.5,)).start()
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise