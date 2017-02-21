import bluepy
import struct
import sys
import paho.mqtt.client as mqtt
import threading
import time
import pexpect
import traceback
from bluepy.btle import BTLEException
import timeit

class BLE_GATEWAY(object):
    
    def __init__(self, BLE_DEVICE_NAME, BLE_MAC_ADDRESS, BLE_DEVICE_TYPE):
        self.name = BLE_DEVICE_NAME
        self.mac = BLE_MAC_ADDRESS
        self.device_type = BLE_DEVICE_TYPE
        self.BLE_lock = threading.Lock()
        self.connected_event = threading.Event()
           
    def data_logger_thread(self, BTLE_DELEGATE_CLASS, BLE_HANDLE):
        """
        1. CONNECT TO BLE Device
        2. CREATE BTLE DELEGATE CLASS & SET DELEGATE
        3. ENABLE Notification
        4. BLOCKING/POLLING
        5. PUBLISH TO MQTT topics
        """
        self.delegate = BTLE_DELEGATE_CLASS
        self.delegate_handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.delegate_handle.insert(len(self.delegate_handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for delegate_handle in BLE_HANDLE:
                self.delegate_handle.insert(len(self.delegate_handle), delegate_handle)
        else:
            print("Invalid data type for BLE_HANDLE")
        
        print("Connecting to BLE device.")
        connection = False  
        while True:
            try:
                if(connection == False):
                    self.device = bluepy.btle.Peripheral(self.mac)
                    self.connected_event.set()
                    print("Connected.")
                    connection = True
                    self.set_delegate() # Set delegates assigned in self.handle list
                
                while True:
                    time.sleep(1)
                    with self.BLE_lock:
                        self.notification = self.device.waitForNotifications(1)
                print "Exiting inner while loop."
            except bluepy.btle.BTLEException as e:
                if(e.code == 1):
                    if(connection == True):
                        print("BLE device disconnected.")
                        connection = False
                        self.connected_event.clear()
                    continue
                if(e.code == 3):
                    print "Unexpected response received. Retry without reconnecting."                
                    continue
                else:
                    print e.message, e.code
                    raise        
            except:
                print sys.exc_info()[0]
                raise
            print "Exitting outer while loop."
            
    def reset_connection(self):
        self.device.disconnect()
        time.sleep(3)
        self.reconnect_blocking()
        self.set_delegate()   
        
    def reconnect_blocking(self):
        while True:
            try:
                self.device.connect(self.mac)
                break
            except BTLEException as e:
                print e.code, e.message
                if(e.code == 1):
                    continue
                else:
                    raise            
                    
    def set_delegate(self):
        self.device.setDelegate(self.delegate)
        for delegate_handle in self.delegate_handle:
            
            while True:
                try:
                    self.device.writeCharacteristic(delegate_handle, struct.pack('<bb',0x01,0x00), True)      
                    break
                except BTLEException as e: 
                    print e.code, e.message  
                    if(e.code == 1):
                        continue
                    elif(e.message == "Helper not started (did you call connect()?)"):
                            self.reconnect_blocking()
                            continue
                    else:
                        raise                     
            
    def set_polling_rate(self, handle, rate):
        if(type(rate) == str and rate.isdigit() == True):
            with self.BLE_lock:
                self.connected_event.wait()
                
                while True:
                    try:
                        self.device.writeCharacteristic(handle, rate, True)      
                        break
                    except BTLEException as e: 
                        print e.code, e.message  
                        if(e.code == 1):
                            continue
                        elif(e.message == "Helper not started (did you call connect()?)"):
                            self.reconnect_blocking()
                            continue 
                        else:
                            raise                    
                
                print "Polling rate updated to ", rate
                self.reset_connection()         
            
    def set_data(self, handle, data):
        with self.BLE_lock:
            self.connected_event.wait()
            try:
                self.device.writeCharacteristic(handle, data, True)
            except bluepy.btle.BTLEException as e:
                print e.code, e.message
                if(e.code == 1):
                    print "BLE disconnected"
                    self.reconnect_blocking()
                    self.set_delegate()
                    print "Reconnected"
            except:
                print sys.exc_info()[0]
                raise
                
            print "Data set: ", data    
        
    def data_updater(self, BLE_HANDLE, DATA):
        """
        1. CONNECT TO BLE DEVICE
        2. BLE.WRITE TO HANDLE
        3. TRIGGER BLE WAKE BY DISCONNECTING AND RECONNECTING
        """
        self.data = []     
        if(isinstance(DATA, str) == True):
            self.data.insert(len(self.data), DATA)
        elif(isinstance(DATA, list) == True):
            for data in DATA:
                self.data.insert(len(self.data), data)
        else:
            print("Invalid data type for DATA")
            raise        
        
        self.handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.handle.insert(len(self.handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for handle in BLE_HANDLE:
                self.handle.insert(len(self.handle), handle)
        else:
            print("Invalid data type for BLE_HANDLE")
            raise
        
        if(len(self.data) != len(self.handle)):
            print("Length of data and handle not equal.")
            raise
            
        connection = ""    
        while True:
            try:
                start_time = timeit.default_timer()
                self.device = bluepy.btle.Peripheral(self.mac)
                print("Connected.")
                connection = True
                for handle in self.handle:
                    self.device.writeCharacteristic(handle, self.data[self.handle.index(handle)], True)
                elapsed = timeit.default_timer() - start_time
                print "time: ", elapsed
                self.device.disconnect()
                time.sleep(3)
                print "Exit data updater."    
                return 0
                    
            except bluepy.btle.BTLEException as e:
                print e.message, e.code
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

class Bluetooth_Multimedia_Gateway(object):
    
    def __init__(self, DEVICE_MAC_ADDRESS):
        self.bluetooth_lock = threading.Lock()
        self.mac = DEVICE_MAC_ADDRESS
        
    def multimedia_connect(self, ):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('power on')
            child.expect("Changing power on succeeded")
            child.sendline("trust 00:00:03:04:28:04")
            child.expect("trust succeeded")
            child.sendline("connect 00:00:03:04:28:04")
            child.expect("Connection successful")
            child.close()
        except:
            print("Exception 1 was thrown.")
            print("Debug information: ")
            traceback.print_exception()
            print(str(child))
    
    def check_default_sink_source(self):
        try:
            command = "pacmd"
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline("stat")
            code1 = child.expect("Default sink name: bluez_sink.00_00_03_04_28_04")#\r\n", pexpect.TIMEOUT)
            code2 = child.expect("Default source name: bluez_source.00_00_03_04_28_04")#, pexpect.TIMEOUT)
            child.close
            
            if(code1 == 0 and code2 == 0):
                return True
            else:
                return False
        except:
            print("Exception 2 was thrown.")
            print("Debug information: ")
            traceback.print_exc()
            print(str(child))    
             
