import sys
sys.path(0,'/home/pi/git-repos/BLE-MQTT-GATEWAY/src')
import BLE_MQTT_GATEWAY as gateway
import bluepy
import threading
import binascii

import time

if(len(sys.argv) == 2 and sys.argv[1] == "test"):
    pass
elif(len(sys.argv) == 1):
    time.sleep(120)

DEVICE_NAME = "Infared Temperature Sensor"
MAC_ADDRESS = "04:A3:16:9B:0C:83"
DEVICE_TYPE = "NULL"
#BLE_HANDLE = [52,56]
BLE_HANDLE = [52]

MQTT_SERVER = "192.168.1.9"
MQTT_SUBSCRIBING_TOPIC = ["test"]
VERBOSE = 0

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
            
        payload = self.binasciiToString(data)
        self.client.publish("test: ", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + payload)
        
class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def handleNotification(self, client, uerdata, msg):
        print(msg.topic+" "+str(msg.payload)) 

if(__name__ == "__main__"):
    try:
        mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, MQTT_delegate().handleNotification)
        threading.Thread(target=mqtt_gateway.client.loop_forever).start()
        ble_delegate = BLE_delegate(mqtt_gateway.client)
        ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
        threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_HANDLE,)).start()
        if(len(sys.argv) == 2 and sys.argv[1].isdigit() == True):
            status = ble_gateway.data_updater(67, sys.argv[1])
            print "Sensor polling interval: ", sys.argv[1], "Status: ", status
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_gateway.client.disconnect()
        sys.exit()

    except:
        raise
    

