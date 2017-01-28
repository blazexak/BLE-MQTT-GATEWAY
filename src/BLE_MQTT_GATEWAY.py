import bluepy
import struct
import sys
import paho.mqtt.client as mqtt

class BLE_GATEWAY(object):
    
    def __init__(self, BLE_DEVICE_NAME, BLE_MAC_ADDRESS, BLE_DEVICE_TYPE):
        self.name = BLE_DEVICE_NAME
        self.mac = BLE_MAC_ADDRESS
        self.device_type = BLE_DEVICE_TYPE
           
    def data_logger_thread(self, BTLE_DELEGATE_CLASS, BLE_HANDLE):
        """
        1. CONNECT TO BLE Device
        2. CREATE BTLE DELEGATE CLASS & SET DELEGATE
        3. ENABLE Notification
        4. BLOCKING/POLLING
        5. PUBLISH TO MQTT topics
        """
        self.handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.handle.insert(len(self.handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for handle in BLE_HANDLE:
                self.handle.insert(len(self.handle), handle)
        else:
            print("Invalid data type for BLE_HANDLE")
        
        print("Connecting to BLE device.")
        connection = ""    
        while True:
            try:
                self.device = bluepy.btle.Peripheral(self.mac)
                print("Connected.")
                connection = True
                self.delegate = BTLE_DELEGATE_CLASS
                self.device.setDelegate(self.delegate)
                for handle in self.handle:
                    self.device.writeCharacteristic(handle, struct.pack('<bb',0x01,0x00), True)
                
                while True:
                    self.notification = self.device.waitForNotifications(1)
                    if(self.notification == True):
                        pass
                        #print("Data received.")
            except bluepy.btle.BTLEException as e:
                #print e.message, e.code
                if(e.code == 1):
                    if(connection == True):
                        print("BLE device disconnected.")
                        connection = False
                    continue
                else:
                    raise       
            except:
                print sys.exc_info()[0]
                raise
        
    def data_updater(self, BLE_HANDLE, DATA):
        """
        1. CONNECT TO BLE DEVICE
        2. BLE.WRITE TO HANDLE
        3. TRIGGER BLE WAKE BY DISCONNECTING AND RECONNECTING
        """
        self.data = DATA
        self.handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.handle.insert(len(self.handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for handle in BLE_HANDLE:
                self.handle.insert(len(self.handle), handle)
        else:
            print("Invalid data type for BLE_HANDLE")
            
        connection = ""    
        while True:
            try:
                self.device = bluepy.btle.Peripheral(self.mac)
                print("Connected.")
                connection = True
                for handle in self.handle:
                    self.device.writeCharacteristic(handle, self.data, True)
                return 0
                    
            except bluepy.btle.BTLEException as e:
                if(e.code == 1):
                    if(connection == True):
                        print("BLE device disconnected.")
                        connection = False
                    continue
                else:
                    print e.message, e.code
                    raise       
            except:
                print sys.exc_info()[0]
                raise
                                
class MQTT_GATEWAY(object):
    
    def __init__(self, MQTT_BROKER_ADDRESS, SUBSCRIBE_TOPIC, MQTT_DELEGATE):
        self.broker_address = MQTT_BROKER_ADDRESS
        self.subscribe_topic = []        
        if(isinstance(SUBSCRIBE_TOPIC, str) == True):
            self.subscribe_topic.insert(len(self.subscribe_topic), SUBSCRIBE_TOPIC)
        elif(isinstance(SUBSCRIBE_TOPIC, list) == True):
            for topic in SUBSCRIBE_TOPIC:
                self.subscribe_topic.insert(len(self.subscribe_topic), topic)
        else:
            print "Invalid data type for SUBSCRIBE_TOPIC"
            
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = MQTT_DELEGATE
        self.client.connect(self.broker_address, 1883,60)
#         self.client.loop_forever()    
    
    def on_connect(self, client, userdata, flags, rc):      
        print("Connected to MQTT Broker with result code "+str(rc))
        for topic in self.subscribe_topic:
            self.client.subscribe(topic)
            
    def get_client(self):
        return self.client        