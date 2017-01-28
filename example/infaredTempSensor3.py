import BLE_MQTT_GATEWAY as gateway
import paho.mqtt.client as mqtt
import bluepy
import threading
import binascii

DEVICE_NAME = "Infared Temperature Sensor"
MAC_ADDRESS = "04:A3:16:9B:0C:83"
DEVICE_TYPE = "NULL"
BLE_HANDLE = [52,56]
MQTT_SERVER = "192.168.42.1"
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
        self.client.publish("test", payload)
        
class MQTT_delegate(object):
    def __init__(self):
        pass
    
    def handleNotification(self, client, uerdata, msg):
        print(msg.topic+" "+str(msg.payload)) 
        
mqtt_gateway = gateway.MQTT_GATEWAY(MQTT_SERVER, MQTT_SUBSCRIBING_TOPIC, MQTT_delegate().handleNotification)
threading.Thread(target=mqtt_gateway.client.loop_forever).start()
ble_delegate = BLE_delegate(mqtt_gateway.client)
ble_gateway = gateway.BLE_GATEWAY(DEVICE_NAME, MAC_ADDRESS, DEVICE_TYPE,)
threading.Thread(target = ble_gateway.data_logger_thread,args=(ble_delegate, BLE_HANDLE,)).start()
status = ble_gateway.data_updater(67, "60")
print(status)

    

