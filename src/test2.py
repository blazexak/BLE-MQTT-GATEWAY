import bluepy
import struct
from bluepy.btle import BTLEException
import timeit
import binascii

mac = "04:A3:16:9B:0C:83"
delegate_handles = [52,56]

class BLE_delegate(bluepy.btle.DefaultDelegate):
    def __init__(self):
        bluepy.btle.DefaultDelegate.__init__(self)
        
    def binasciiToString(self, data):
        data = binascii.b2a_hex(data)
        data = data[0:2]
        data = str(int(data,16))
        return data
        
    def handleNotification(self, cHandle, data):
        data = self.binasciiToString(data)
        print "Data: ", data
        print "Handle: ", cHandle
        
def main():
    delegate = BLE_delegate()
    print "Connecting"
    device = bluepy.btle.Peripheral(mac)
    print "Connected"
    device.setDelegate(delegate)
    
    for delegate_handle in delegate_handles:    
        while True:
            try:
                device.writeCharacteristic(delegate_handle, struct.pack('<bb',0x01,0x00), True)      
                break
            except BTLEException as e: 
                print e.code, e.message  
                if(e.code == 1):
                    continue
                elif(e.message == "Helper not started (did you call connect()?)"):
                    while True:
                        try:
                            device = bluepy.btle.Peripheral(mac)
                            break
                        except BTLEException as e:
                            print e.code, e.message
                            if(e.code == 1):
                                continue
                            else:
                                raise 
                    continue
                else:
                    raise         
                
    while True:
        device.waitForNotifications(1)
    print "Exit main()"        
    
if (__name__ == "__main__"):
    main()








          