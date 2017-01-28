import bluepy
from bluepy.btle import BTLEException

MAC_ADDRESS = "04:A3:16:9B:0C:83"

ble_device = bluepy.btle.Peripheral(MAC_ADDRESS)
print(ble_device)

while True:
    pass
        
