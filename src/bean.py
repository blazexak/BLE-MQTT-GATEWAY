import bluepy
import binascii
import struct

MAC_ADDRESS = "04:A3:16:9B:0C:83"
handle = 52
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
            
        #payload = self.binasciiToString(data)
        #self.client.publish("test: ", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + payload)
        
d = bluepy.btle.Peripheral(MAC_ADDRESS)
delegate = BLE_delegate(1)
d.setDelegate(delegate)
d.writeCharacteristic(handle, struct.pack('<bb',0x01,0x00), True)
while True:
    notification = d.waitForNotifications(1)
    if(notification == True):
        print("Data received.")
