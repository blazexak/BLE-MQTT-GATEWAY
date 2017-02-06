import os
import subprocess
import time
import socket
import sys
import threading


class Bluetooth_Speaker_Mic(object):
	
	def __init__(self, NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR):
		self.name = NAME
		self.mac = MAC_ADDRESS
		self.play_dir = PLAYBACK_DIR
		self.record_dir = RECORD_DIR
		self.recording_event = threading.Event()		
		
		d = os.path.dirname(self.play_dir)
		if not os.path.exists(d):
			os.makedirs(d)
			
		d = os.path.dirname(self.record_dir)
		if not os.path.exists(d):
			os.makedirs(d)			
		
	def playback(self, DELETE=None, CLIENT=None, TOPIC=None):
		aplay_status = self.subprocess_check_initiate("aplay", "NULL")
		if(aplay_status == 0):
			f = self.files_in_directory(self.play_dir)
			if (f != -1):
				if(CLIENT!=None and TOPIC!=None):
					CLIENT.publish(TOPIC, '1')
				subprocess.call(["aplay", self.play_dir+f[0]])
				if(CLIENT!=None and TOPIC!=None):
					CLIENT.publish(TOPIC, '0')
				if(DELETE == True):
					subprocess.call(["sudo", "rm", self.play_dir+f[0]])
			else:
				print "No audio available."
		
	def record(self, COUNTDOWN, IP_ADDRESS=None, CLIENT=None, TOPIC=None):
		self.recording_lock = threading.Lock()
		arecord_status = self.subprocess_check_initiate("arecord", "NULL")
		if(arecord_status == -1):
			self.recording_event.set()
			print "Recording stopped."
		if(arecord_status == 0): 
			f = time.strftime("%Y%m%d%H%M%S") + ".wav"
			if(CLIENT!=None and TOPIC!=None):
				CLIENT.publish(TOPIC, '1')
			subprocess.call(["aplay", os.path.dirname("beep-08b.wav")])
			subprocess.Popen(["arecord", "-f", "dat", self.record_dir+f])
			
			with self.recording_lock:
				threading.Thread(target = self.countdown_kill, args = ("arecord", COUNTDOWN, self.recording_event)).start()
				if(CLIENT!=None and TOPIC!=None):
					CLIENT.publish(TOPIC, '0')				 
				self.recording_event.clear()
			print("Lock released after countdown.")
			if(IP_ADDRESS != None):
				try:
					socket.inet_aton(IP_ADDRESS)
					with self.recording_lock:
						self.file_transfer(f, IP_ADDRESS) 
				except socket.error:
					raise TypeError	  
						
	def set_directory(self, DIR):
		d = os.path.dirname(DIR)
		if not os.path.exists(d):
			os.makedirs(d)
	
	def files_in_directory(self, DIRECTORY):
		files = os.listdir(DIRECTORY)
		files.sort()	
		num = (len(files))
		
		if (num > 0):
			return files
		else:
			return -1	
			
	def file_available(self, DIRECTORY):
		try:
			f = os.listdir(DIRECTORY)
			length = len(f)
			if(length > 0):
				return True
			else:
				return False
		except:
			print(sys.exc_info()[0])

	def file_transfer(self, FILE, IP_ADDRESS):
		subprocess.call(["ssh", IP_ADDRESS, 'mkdir -p '+ self.record])
		subprocess.call(["scp", self.record_dir+FILE, "pi@"+IP_ADDRESS+":"+self.record_dir])
		subprocess.call(["sudo", "rm", self.record_dir+FILE])	  

	# Check for existing process specified by "process_name"
	# Return 0: If no process was found
	# Return -1: Processes were found and terminate all processes		
	def subprocess_check_initiate(self,PROCESS_NAME, DEVICE_NAME):
		try:
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			x = 0
			for x in range(len(pidID)):
				subprocess.call(["kill", pidID[x]]) 
			print "Pre-existing process killed by user."
			return 1
		except subprocess.CalledProcessError:
			print "No process " + PROCESS_NAME + " exists."
			return 0
		except:
			print "Unknown error caught! Exit!"
			raise		

	# Thread to kill a process after COUNTDOWN seconds
	def countdown_kill(self,PROCESS_NAME, COUNTDOWN, EVENT):
		try:
			print "Countdown thread started."
			for x in range(COUNTDOWN):
				time.sleep(1)
				if(EVENT.is_set() == True):
					print "External event signal received. ", PROCESS_NAME, " killed"
					break
			
#			 client.publish(MQTT_TOPIC_HSB, "000,255,000")
#			 time.sleep(1)
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			x = 0
			for x in range(len(pidID)):
				subprocess.call(["kill", pidID[x]])	
			print PROCESS_NAME + " killed"
			subprocess.call(["aplay", os.path.dirname("beep-07.wav")])
		except subprocess.CalledProcessError:
			print "Error caught: ", sys.exc_info()[0]
		except:
			print "Unknown error caught! Exit!"
			raise
		
class Button_Bean(object):		
	def __init__(self, MAC_ADDRESS):
		self.mac = MAC_ADDRESS
		
	def check_HSV(self, msg):
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
		
	def playback(self, DELETE=None):
		aplay_status = self.subprocess_check_initiate("aplay", "NULL")
		if(aplay_status == 0):
			f = self.files_in_directory(self.play_dir)
			if (f != -1):
				subprocess.call(["aplay", self.play_dir+f[0]])
				if(DELETE == True):
					subprocess.call(["sudo", "rm", self.play_dir+f[0]])
			else:
				print "No audio available."
		
	def record(self, COUNTDOWN, IP_ADDRESS=None):
		self.recording_lock = threading.Lock()
		arecord_status = self.subprocess_check_initiate("arecord", "NULL")
		if(arecord_status == -1):
			self.recording_event.set()
			print "Recording stopped."
		if(arecord_status == 0): 
			f = time.strftime("%Y%m%d%H%M%S") + ".wav"
			subprocess.Popen(["arecord", "-f", "dat", self.record_dir+f])
			with self.recording_lock:
				threading.Thread(target = self.countdown_kill, args = ("arecord", COUNTDOWN, self.recording_event)).start()
				self.recording_event.clear()
			print("Lock released after countdown.")
			if(IP_ADDRESS != None):
				try:
					socket.inet_aton(IP_ADDRESS)
					with self.recording_lock:
						self.file_transfer(f, IP_ADDRESS) 
				except socket.error:
					raise TypeError		   
