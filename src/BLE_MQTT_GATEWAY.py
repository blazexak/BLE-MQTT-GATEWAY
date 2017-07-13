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
import logging
import logging.config
from collections import namedtuple
import yaml

# create module logger
module_logger = logging.getLogger("exampleApp."+__name__)
class BLE_GATEWAY(object):
    
    def __init__(self, BLE_DEVICE_NAME, BLE_MAC_ADDRESS, BLE_DEVICE_TYPE):
        module_logger.debug("Creating BLE GATEWAY object.")
        self.name = BLE_DEVICE_NAME
        self.mac = BLE_MAC_ADDRESS
        self.device_type = BLE_DEVICE_TYPE
        self.BLE_lock = threading.Lock()
        self.diagnostic_lock = threading.Lock()
        self.connected_event = threading.Event()
           
    def data_logger_thread(self, BTLE_DELEGATE_CLASS, BLE_HANDLE, EVENT_RUN=None):
        """
        1. CONNECT TO BLE Device
        2. CREATE BTLE DELEGATE CLASS & SET DELEGATE
        3. ENABLE Notification
        4. BLOCKING/POLLING
        5. PUBLISH TO MQTT topics
        """
        self.thread_type = "logger"
        self.delegate = BTLE_DELEGATE_CLASS
        self.delegate_handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.delegate_handle.insert(len(self.delegate_handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for delegate_handle in BLE_HANDLE:
                self.delegate_handle.insert(len(self.delegate_handle), delegate_handle)
        else:
            module_logger.warning("Invalid data type for BLE_HANDLE")
        
        module_logger.info("Connecting to BLE device.")
        connection = False  
        while EVENT_RUN.is_set() == False:
            try:
                if(connection == False):
                    self.device = bluepy.btle.Peripheral(self.mac)
                    self.connected_event.set()
                    module_logger.info("Connected.")
                    connection = True
                    self.set_delegate() # Set delegates assigned in self.handle list
                
                while EVENT_RUN.is_set() == False:
                    time.sleep(0.1)
                    with self.BLE_lock:
                        with self.diagnostic_lock:
                            self.notification = self.device.waitForNotifications(0.1)
                module_logger.debug("Exiting inner while loop.")
            except bluepy.btle.BTLEException as e:
                if(e.code == 1):
                    if(connection == True):
                        module_logger.info("BLE device disconnected.")
                        connection = False
                        self.connected_event.clear()
                    continue
                if(e.code == 3):
                    module_logger.debug("In data logger")
                    module_logger.debug("Unexpected response received. Retry without reconnecting.")                
                    continue
                else:
                    module_logger.debug("In else loop")
                    module_logger.error(e.message, e.code)
                    raise
            except AttributeError as e:
                module_logger.warning("Danger! Raised attributeError. Bluepy seems to raise attributeError exception when " 
                      "BLE disconnected while waitForNotification tried to poll. However, still unsure what "
                      "other cicumstances might raise this attribute error!")
                module_logger.exception("In data_logger: Attribute error caught.")
                time.sleep(3)
                continue
                        
            except:
                module_logger.exception("In data_logger: Unknown error caught.")
                raise
            module_logger.debug("Exitting outer while loop.")
            
    def data_updater(self, BLE_HANDLE, DATA):
        """
        1. CONNECT TO BLE DEVICE
        2. BLE.WRITE TO HANDLE
        3. TRIGGER BLE WAKE BY DISCONNECTING AND RECONNECTING
        """
        self.thread_type = "updater"
        self.data = []     
        if(isinstance(DATA, str) == True):
            self.data.insert(len(self.data), DATA)
        elif(isinstance(DATA, list) == True):
            for data in DATA:
                self.data.insert(len(self.data), data)
        else:
            module_logger.error("Invalid data type for DATA")
            raise        
        
        self.handle = []        
        if(isinstance(BLE_HANDLE, int) == True):
            self.handle.insert(len(self.handle), BLE_HANDLE)
        elif(isinstance(BLE_HANDLE, list) == True):
            for handle in BLE_HANDLE:
                self.handle.insert(len(self.handle), handle)
        else:
            module_logger.error("Invalid data type for BLE_HANDLE")
            raise
        
        if(len(self.data) != len(self.handle)):
            module_logger.error("Length of data and handle not equal.")
            raise
            
        connection = ""    
        while True:
            try:
                start_time = timeit.default_timer()
                self.device = bluepy.btle.Peripheral(self.mac)
                self.connected_event.set()
                module_logger.info("Connected.")
                connection = True
                print "Data type: ", type(self.data), "Length of data: ", len(self.data)
                for handle in self.handle:
                    self.device.writeCharacteristic(handle, self.data[self.handle.index(handle)], True)
                elapsed = timeit.default_timer() - start_time
                module_logger.debug("time: " + str(elapsed))
                self.device.disconnect()
                module_logger.info("Disconnected")
                self.connected_event.clear()
                time.sleep(3)
                module_logger.info("Exit data updater.")    
                return 0
                    
            except bluepy.btle.BTLEException as e:
                # print e.message, e.code
                if(e.code == 1):
                    if(connection == True):
                        module_logger.info("BLE device disconnected.")
                        connection = False
                        self.connected_event.clear()
                    continue
                else:
                    raise       
            except AttributeError as e:
                module_logger.warning("Danger! Raised attributeError. Bluepy seems to raise attributeError exception when" 
                      "BLE disconnected while waitForNotification tried to poll. However, still unsure what"
                      "other cicumstances might raise this attribute error!")
                module_logger.exception("In data_updater: Attribute error caught.")
                time.sleep(3)
                continue                
            except:
                module_logger.exception("In data_updater: Unknown error caught.")
                raise                                       
            
    def reset_connection(self):
        self.device.disconnect()
        self.connected_event.clear()
        time.sleep(3)
        self.reconnect_blocking()
        self.set_delegate()   
        
    def reconnect_blocking(self):
        while True:
            try:
                self.device.connect(self.mac)
                self.connected_event.set()
                break
            except BTLEException as e:
                # print e.code, e.message
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
                    module_logger.warning(e.code, e.message)  
                    if(e.code == 1):
                        continue
                    elif(e.message == "Helper not started (did you call connect()?)"):
                            self.reconnect_blocking()
                            continue
                    else:
                        raise       
                # except AttributeError as e:
                #     print "AttributeError: ", str(e)
                                   
            
    def set_polling_rate(self, handle, rate):
        if(type(rate) == str and rate.isdigit() == True):
            with self.BLE_lock:
                self.connected_event.wait()
                
                while True:
                    try:
                        self.device.writeCharacteristic(handle, rate, True)      
                        break
                    except BTLEException as e: 
                        module_logger.warning(e.code, e.message)  
                        if(e.code == 1):
                            continue
                        elif(e.message == "Helper not started (did you call connect()?)"):
                            self.reconnect_blocking()
                            continue 
                        else:
                            raise                    
                
                module_logger.info("Polling rate updated to ", rate)
                self.reset_connection()         
            
    def set_data(self, handle, data):
        with self.BLE_lock:
            self.connected_event.wait()
            try:
                self.device.writeCharacteristic(handle, data, True)
            except bluepy.btle.BTLEException as e:
                module_logger.warning(e.code, e.message)
                if(e.code == 1):
                    module_logger.info("BLE disconnected")
                    self.reconnect_blocking()
                    self.set_delegate()
                    module_logger.info("Reconnected")
            except:
                module_logger.exception("In set_data: Unknown error caught.")
                raise
                
            module_logger.info("Data set: " + data)    
        
    # def diagnostic_callback(self, client, userdata, msg):
    #     print "MQTT message received: ", msg.payload, "MQTT topic: ", msg.topic
    #     with self.diagnostic_lock:
    #         if(self.connected_event.is_set() == False):
    #             print "Loop 1"
    #             if(msg.payload == "test"):
    #                 while True:
    #                     try:
    #                         connection = False
    #                         self.device = bluepy.btle.Peripheral(self.mac)
    #                         break
    #                     except bluepy.btle.BTLEException as e:
    #                         print e.message, e.code
    #                         if(e.code == 1):
    #                             if(connection == True):
    #                                 print("BLE device disconnected.")
    #                                 connection = False
    #                                 self.connected_event.clear()
    #                             continue
    #                         else:
    #                             raise                 
    #                 self.connected_event.set()                
    #                 self.set_data(63, '1')
    #                 self.device.disconnect()
    #                 self.connected_event.clear()
    #                 time.sleep(3)                   
    #         else:
    #             print "loop 2"
    #             if(msg.payload == "test"):
    #                 self.set_data(63, '1')
    #             self.reset_connection()

    def diagnostic_callback(self, client, userdata, msg):
        module_logger.debug("MQTT message received: " + msg.payload + "MQTT topic: "+ msg.topic)
        module_logger.debug("hasattr(self, thread_type) : " + str(hasattr(self, 'thread_type')))
        module_logger.info("Diagnostic test initiated.")
        if(msg.payload == "test"):
            with self.diagnostic_lock:
                if(hasattr(self, 'thread_type') == True and self.thread_type == "logger"):
                    module_logger.debug("in logger")
                    if(self.connected_event.is_set() == True):
                        module_logger.debug("set data")
                        self.set_data(63,'1')
                        module_logger.debug("after set data")
                        self.reset_connection()
                        module_logger.debug("after reconnecting")
                    else:
                        module_logger.info("Device is not connected. Not running diagnostic.")
                        
                elif(hasattr(self, 'thread_type') == False or self.thread_type == "updater"):
                    module_logger.debug('in updater')
                    if(self.connected_event.is_set() == True):
                        module_logger.debug("is connected")
                        while(self.connected_event.is_set() == True):
                            pass
                        while True:
                            try:
                                connection = False
                                self.device = bluepy.btle.Peripheral(self.mac)
                                module_logger.info("Connected")
                                self.connected_event.set()
                                break
                            except bluepy.btle.BTLEException as e:
    #                             print e.message, e.code
                                if(e.code == 1):
                                    if(connection == True):
                                        module_logger.info("BLE device disconnected.")
                                        connection = False
                                        self.connected_event.clear()
                                    continue
                                else:
                                    raise                         
                        self.set_data(63, '1')
                        self.device.disconnect()
                        module_logger.info("Disconnected")
                        self.connected_event.clear()
                        time.sleep(3)                       
                    elif(self.connected_event.is_set() == False):
                        module_logger.info("Device not connected")
                        while True:
                            try:
                                connection = False
                                self.device = bluepy.btle.Peripheral(self.mac)
                                module_logger.info("Connected")
                                self.connected_event.set()
                                break
                            except bluepy.btle.BTLEException as e:
    #                             print e.message, e.code
                                if(e.code == 1):
                                    if(connection == True):
                                        module_logger.info("BLE device disconnected.")
                                        connection = False
                                        self.connected_event.clear()
                                    continue
                                else:
                                    raise                         
                        self.set_data(63, '1')
                        self.device.disconnect()
                        module_logger.info("Disconnected")
                        self.connected_event.clear()
                        time.sleep(3)                          
                                
class MQTT_GATEWAY(object):
    
    def __init__(self, MQTT_BROKER_ADDRESS, SUBSCRIBE_TOPIC, MQTT_DELEGATE=None):
        module_logger.debug("Creating MQTT GATEWAY object.")
        self.broker_address = MQTT_BROKER_ADDRESS
        self.subscribe_topic = []        
        if(isinstance(SUBSCRIBE_TOPIC, str) == True):
            self.subscribe_topic.insert(len(self.subscribe_topic), SUBSCRIBE_TOPIC)
        elif(isinstance(SUBSCRIBE_TOPIC, list) == True):
            for topic in SUBSCRIBE_TOPIC:
                self.subscribe_topic.insert(len(self.subscribe_topic), topic)
        else:
            module_logger.warning("Invalid data type for SUBSCRIBE_TOPIC")
            
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = MQTT_DELEGATE
        self.client.connect(self.broker_address, 1883,60)
        # self.client.loop_forever()    
    
    def on_connect(self, client, userdata, flags, rc):      
        module_logger.info("Connected to MQTT Broker with result code "+str(rc))
        for topic in self.subscribe_topic:
            self.client.subscribe(topic)
            
    def add_diagnostic(self, ble_gateway):
        self.client.subscribe("diagnostic")
        self.subscribe_topic.append("diagnostic")
        self.client.message_callback_add("diagnostic", ble_gateway.diagnostic_callback)

class Bluetooth_Multimedia_Gateway(object):
    
    def __init__(self, DEVICE_MAC_ADDRESS):
        self.bluetooth_lock = threading.Lock()
        self.mac = DEVICE_MAC_ADDRESS
	self.Device_Info = namedtuple('Device_Info', 'trusted paired connected')
	self.device_info = self.Device_Info(trusted=False, paired=False, connected=False)
	self.Sink_Source = namedtuple('Sink_Source', 'sink_set source_set')
	self.sink_source_status = self.Sink_Source(sink_set=False, source_set=False)
        
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
            traceback.print_exc()
            print(str(child))
    
    def set_default_sink(self):
	try:
            command = "pacmd"
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline("set-default-sink bluez_sink.00_00_03_04_28_04")
	    self.sink_source_status = self.sink_source_status._replace(sink_set=True)
	    child.close()
	except:
	    self.sink_source_status = self.sink_source_status._replace(sink_set=False)
	    print("Exception was thrown in set_default_sink().")
	    print("Debug information: ")
            traceback.print_exc()
	    
    def set_default_source(self):
	try:
            command = "pacmd"
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
	    child.sendline("set-default-source bluez_source.00_00_03_04_28_04")
	    self.sink_source_status = self.sink_source_status._replace(source_set=True)
	    child.close
	except:
	    self.sink_source_status = self.sink_source_status._replace(source_set=False)
	    print("Exception was thrown in set_default_source().")
	    print("Debug information: ")
            traceback.print_exc()
	    	
    def check_default_sink_source(self):
        try:
            command = "pacmd"
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline("stat")
	    
	    try:
		code1 = child.expect("Default sink name: bluez_sink.00_00_03_04_28_04")#\r\n", pexpect.TIMEOUT)
		self.sink_source_status = self.sink_source_status._replace(sink_set=True)
	    except:
		self.sink_source_status = self.sink_source_status._replace(sink_set=False)
		print("Check: Not default sink")		

	    try:
		code2 = child.expect("Default source name: bluez_sink.00_00_03_04_28_04.monitor")#, pexpect.TIMEOUT)
		self.sink_source_status = self.sink_source_status._replace(sink_set=True)
	    except:
		self.sink_source_status = self.sink_source_status._replace(sink_set=False)
		print("Check: Not default source")				
            
            child.close

        except:
            print("Exception was thrown in check_default_sink_source().")
            print("Debug information: ")
            traceback.print_exc()
	    
    def check_info(self):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('info ' + self.mac)
	    
	    try:
		code2 = child.expect("Paired: yes")
		self.device_info = self.device_info._replace(paired=True)
	    except pexpect.exceptions.TIMEOUT as e:
		print "Check: Paired: False"
		self.device_info = self.device_info._replace(paired=False)
						    
	    try:
		code1 = child.expect("Trusted: yes")
		self.device_info = self.device_info._replace(trusted=True)
	    except pexpect.exceptions.TIMEOUT as e:
		print "Check: Trusted: False"
		self.device_info = self.device_info._replace(trusted=False)

	    try:
		code3 = child.expect("Connected: yes")
		self.device_info = self.device_info._replace(connected=True)
	    except pexpect.exceptions.TIMEOUT as e:
		print "Connected: False"
		self.device_info = self.device_info._replace(connected=False)
	    
            child.close()
        except:
            print("Exception in check_info().")
            print("Debug")
	    traceback.print_exc()
		
    def trust(self):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('trust ' + self.mac)
            child.expect("trust succeeded")
            child.close()
	    self.device_info = self.device_info._replace(trusted=True)
        except:
            print("Exception was thrown in trust().")
            print("Debug information: ")
            traceback.print_exc()
	    self.device_info = self.device_info._replace(trusted=False)
	    
    def pair(self):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('pair ' + self.mac)
            child.expect("pair succeeded")
            child.close()
	    self.device_info = self.device_info._replace(paired=True)
        except:
            print("Exception was thrown in pair().")
            print("Debug information: ")
            traceback.print_exc()	 
	    self.device_info = self.device_info._replace(paired=False)   

    def connect(self):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('connect ' + self.mac)
            child.expect("Connection successful")
            child.close()
	    self.device_info = self.device_info._replace(connected=True)
        except:
	    self.device_info = self.device_info._replace(connected=False)
            print("Exception was thrown in connect().")
            print("Debug information: ")
            traceback.print_exc()
	    		
    def disconnect(self):
        try:
            command = 'bluetoothctl'
            child = pexpect.spawn(command)
            child.logfile = open("/tmp/mylog", "w")
            child.sendline('disconnect 00:00:03:04:28:04')
            child.expect("Successful disconnected")
            child.close()
        except:
            print("Exception in disconnect().")
            print("Debug information: ")
            traceback.print_exc()	
             
'''
 BLE Advertisement Gateway class
    - scan for nearby advertisement
    - filter out advertisement based on a log file
    - publish it through MQTT topics in the log file
'''
class BLE_ADVERTISEMENT_GATEWAY(object):


    def __init__(self):
        pass

    def minor(self, data):
        return str(int(data[-6:-2], 16))
    
    def minor_low(self,data):
        return str(int(data[-4:-2], 16))
    
    def minor_high(self,data):
        return str(int(data[-6:-4], 16))
    
    def rssi(self,data):
        return str(int(data[-2::], 16))

    '''
    params: yaml_file that consists of the iBeacon device information
    return: a dictionary with length equals to number of devices in the yaml file.
            Each device's name represents a key in the dictionary which consists of three
            mqtt topic, mac address and name.
    '''    
    def load_configuration_file(self, yaml_file):
        with  open(yaml_file, 'r') as stream:
            try:
                beacons = (yaml.load(stream))             
                return beacons
            except yaml.YAMLError as exc:
                print(exc)
        