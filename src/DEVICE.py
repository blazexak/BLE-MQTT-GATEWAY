import os
import subprocess
import time
import socket
import sys
import threading
import pexpect
import logging
import logging.config

# create module logger
module_logger = logging.getLogger("exampleApp."+__name__)

class Bluetooth_Speaker_Mic(object):
	
	def __init__(self, NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR):
		self.name = NAME
		self.mac = MAC_ADDRESS
		self.play_dir = PLAYBACK_DIR
		self.record_dir = RECORD_DIR
		self.buffer_dir = "/home/pi/git-repos/BLE-MQTT-GATEWAY/audio/"
		self.recording_sigkill = threading.Event()	
		self.recording_event = threading.Event()
		
		
		self.chime = "aplay /home/pi/Downloads/chime.wav"
		self.half_volume = "pacmd set-sink-volume 1 20000"
		self.full_volume = "pacmd set-sink-volume 1 60000"	
		
		d = os.path.dirname(self.play_dir)
		if not os.path.exists(d):
			os.makedirs(d)
			
		d = os.path.dirname(self.record_dir)
		if not os.path.exists(d):
			os.makedirs(d)			

	'''
	params: 
	return:
	'''		
	def play(self, AUDIO_DIR):
		'''
		safe call as compared to default "aplay"
		it checks whether at time of execution any "aplay" is running, does not play
		audio if "aplay" has been executed prior
		'''
		aplay_status = self.subprocess_check_initiate("aplay")
		if(aplay_status == 0 and os.path.isfile(AUDIO_DIR)):
			print "playing " + AUDIO_DIR
			subprocess.call(self.half_volume.split())	
			subprocess.call(["aplay", AUDIO_DIR])					
			subprocess.call(self.full_volume.split())
		else:
			print "aplay status: " + aplay_status
			print "No audio available or Another speaker is busy."

	def playback(self, DELETE=None, CLIENT=None, TOPIC=None):
		aplay_status = self.subprocess_check_initiate("aplay", "NULL", CLIENT, TOPIC)
		if(aplay_status == 0):
			f = self.sort_files_in_directory(self.play_dir)
			if (f != -1):
				if(CLIENT!=None and TOPIC!=None):
					code = CLIENT.publish(TOPIC, '1')
					print code
				# subprocess.call(self.half_volume.split())
				# subprocess.call(self.chime.split())				
				# subprocess.call(self.full_volume.split())
				subprocess.call(["aplay", self.play_dir+f[0]])
				if(CLIENT!=None and TOPIC!=None):
					CLIENT.publish(TOPIC, '0')
				if(DELETE == True):
					subprocess.call(["sudo", "rm", self.play_dir+f[0]])
			else:
				print "No audio available."
		
	def record(self, COUNTDOWN, IP_ADDRESS=None, CLIENT=None, TOPIC=None):
		
		arecord_status = self.subprocess_check_initiate("arecord", "NULL", CLIENT, TOPIC)
		if(arecord_status == 0): 
			f = time.strftime("%Y%m%d%H%M%S") + ".wav"
			if(CLIENT!=None and TOPIC!=None):
				CLIENT.publish(TOPIC, '1')
# 				CLIENT.publish("bean/button/hsb", "000,255,100")
			# subprocess.call(self.half_volume.split())	
			# subprocess.call(self.chime.split())
			# subprocess.call(self.full_volume.split())
			# Uncomment for saving to buffer directory for application where recording is needed to be send remotely
			# subprocess.Popen(["arecord", "-f", "dat", self.buffer_dir+f])

			# New logic state
			# Start the countdown as a thread
			# Start aplay as a blocking call
			threading.Thread(target = self.countdown_kill,
				args = ("arecord", COUNTDOWN, CLIENT, TOPIC,IP_ADDRESS,f)).start()

			self.recording_event.set()
			subprocess.call(["arecord", "-f", "dat", self.buffer_dir+f])
			self.recording_event.clear()
			self.recording_sigkill.clear()
			print "out"
			# Recording is saved to local PLAYBACK_DIR for local record and playback application

			### Old Code (Commenting out to test new logic state)

			# subprocess.Popen(["arecord", "-f", "dat", self.play_dir+f])
			
			# with self.recording_lock:
			# 	threading.Thread(target = self.countdown_kill, args = ("arecord", COUNTDOWN, CLIENT, TOPIC,IP_ADDRESS,f)).start()
			# 	print "out"
			# 	self.recording_event.clear()



		# if(arecord_status == -1):
		# 	self.recording_event.set()						  
		### End of old code				
	def set_directory(self, DIR):
		d = os.path.dirname(DIR)
		if not os.path.exists(d):
			os.makedirs(d)
	
	def sort_files_in_directory(self, DIRECTORY):
		files = os.listdir(DIRECTORY)
		files.sort()	
		num = (len(files))
		
		if (num > 0):
			return files
		else:
			return -1	
			
	def directory_hasFile(self, DIRECTORY):
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
		subprocess.call(["ssh", IP_ADDRESS, 'mkdir -p '+ self.record_dir])
		subprocess.call(["scp", self.buffer_dir+FILE, "pi@"+IP_ADDRESS+":"+self.record_dir])
		subprocess.call(["sudo", "rm", self.buffer_dir+FILE])	  

	# Check for existing process specified by "process_name"
	# Return 0: If no process was found
	# Return -1: Processes were found and terminate all processes		
	def subprocess_check_initiate(self,PROCESS_NAME, DEVICE_NAME=None, CLIENT=None, TOPIC=None):
		try:
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			if(CLIENT != None and TOPIC != None):
				CLIENT.publish(TOPIC, '0')
			x = 0
			for x in range(len(pidID)):
				subprocess.call(["kill", pidID[x]]) 
			#print "Pre-existing process killed by user."
			return -1
		except subprocess.CalledProcessError:
			#print "No process " + PROCESS_NAME + " exists."
			return 0
		except:
			print "Unknown error caught! Exit!"
			raise		

	# Thread to kill a process after COUNTDOWN seconds
	def countdown_kill(self,PROCESS_NAME, COUNTDOWN, CLIENT, TOPIC, IP_ADDRESS=None, f=None):
		try:
			#print "Countdown thread started."
			for x in range(COUNTDOWN):
				time.sleep(1)
				print x, self.recording_sigkill.is_set()
				if(self.recording_sigkill.is_set() == True):
					print "External event signal received. ", PROCESS_NAME, " killed"
					break
			#if(self.recording_event.is_set() != True):
			#	CLIENT.publish(TOPIC, "1")
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			x = 0
			for x in range(len(pidID)):
				subprocess.call(["kill", pidID[x]])	
			#print PROCESS_NAME + " killed"
			
			
			if(IP_ADDRESS != None):
				try:
					print "Sending audio file to ", IP_ADDRESS
					socket.inet_aton(IP_ADDRESS)
					self.file_transfer(f, IP_ADDRESS) 
				except socket.error:
					raise TypeError	
		
		except subprocess.CalledProcessError:
			print "Sending audio file to ", IP_ADDRESS
			if(IP_ADDRESS != None):
				try:
					socket.inet_aton(IP_ADDRESS)
					# with self.recording_lock:
					self.file_transfer(f, IP_ADDRESS) 
				except socket.error:
					raise TypeError				
		except:
			print "Unknown error caught! Exit!"
			raise
		
