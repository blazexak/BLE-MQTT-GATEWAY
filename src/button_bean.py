#!/usr/bin/python

import sys
import threading
import BLE_MQTT_GATEWAY as gateway
import bluepy
import time
import binascii

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(120)

DEVICE_NAME = "Bean Button with LED"
MAC_ADDRESS = "D0:39:72:C9:9A:0B"
DEVICE_TYPE = "NULL"
BLE_DELEGATE_HANDLE = [68]
HANDLE = [51, 55, 59, 63, 67]

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["bean/button/hsb"]
MQTT_PUBLISHING_TOPIC = ["bean/button"]
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
            print("Data: ", data)
            print("Handle: ", cHandle)
            
        self.client.publish(MQTT_PUBLISHING_TOPIC[0], time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + data)
        
class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def addBLE(self, BLE_GATEWAY):
        self.ble_gateway = BLE_GATEWAY
    
    def handleNotification(self, client, uerdata, msg):
        print(msg.topic+" "+str(msg.payload)) 
        
        if(msg.topic == MQTT_SUBSCRIBING_TOPIC[0]):
            state, hsb = check_HSV(msg.payload)
            if state == True:
                self.ble_gateway.set_data(HANDLE[0], msg.payload)            

# Function for checking HSV string format: "HHH,SSS,BBB"
# All H,S,B must be integer between 0-255, otherwise invalid
def check_HSV(msg):
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
        ble_delegate = BLE_delegate(mqtt_gateway.client)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_DELEGATE_HANDLE,)).start()
        mqtt_delegate.addBLE(ble_gateway)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
#         sys.exit()
        raise        