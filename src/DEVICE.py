import os
import subprocess
import time
import socket
import sys
import threading
import pexpect


class Bluetooth_Speaker_Mic(object):
	
	def __init__(self, NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR):
		self.name = NAME
		self.mac = MAC_ADDRESS
		self.play_dir = PLAYBACK_DIR
		self.record_dir = RECORD_DIR
		self.recording_event = threading.Event()	
		self.recording_lock = threading.Lock()
		
		
		self.chime = "aplay /home/pi/Downloads/chime.wav"
		self.half_volume = "pacmd set-sink-volume 1 20000"
		self.full_volume = "pacmd set-sink-volume 1 60000"	
		
		d = os.path.dirname(self.play_dir)
		if not os.path.exists(d):
			os.makedirs(d)
			
		d = os.path.dirname(self.record_dir)
		if not os.path.exists(d):
			os.makedirs(d)			
		
	def playback(self, DELETE=None, CLIENT=None, TOPIC=None):
		aplay_status = self.subprocess_check_initiate("aplay", "NULL", CLIENT, TOPIC)
		if(aplay_status == 0):
			f = self.files_in_directory(self.play_dir)
			if (f != -1):
				#if(CLIENT!=None and TOPIC!=None):
				#	code = CLIENT.publish(TOPIC, '1')
				#	print code
				subprocess.call(self.half_volume.split())
				subprocess.call(self.chime.split())				
				subprocess.call(self.full_volume.split())
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
			#if(CLIENT!=None and TOPIC!=None):
			#	CLIENT.publish(TOPIC, '1')
				#CLIENT.publish("bean/button/hsb", "000,255,100")
			subprocess.call(self.half_volume.split())	
			subprocess.call(self.chime.split())
			subprocess.call(self.full_volume.split())
			subprocess.Popen(["arecord", "-f", "dat", self.record_dir+f])
			
			with self.recording_lock:
				threading.Thread(target = self.countdown_kill, args = ("arecord", COUNTDOWN, CLIENT, TOPIC,IP_ADDRESS,f)).start()
				print "out"
				self.recording_event.clear()
			#print("Lock released after countdown.")

		if(arecord_status == -1):
			self.recording_event.set()						  
						
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
		subprocess.call(["ssh", IP_ADDRESS, 'mkdir -p '+ self.record_dir])
		subprocess.call(["scp", self.record_dir+FILE, "pi@"+IP_ADDRESS+":"+self.record_dir])
		subprocess.call(["sudo", "rm", self.record_dir+FILE])	  

	# Check for existing process specified by "process_name"
	# Return 0: If no process was found
	# Return -1: Processes were found and terminate all processes		
	def subprocess_check_initiate(self,PROCESS_NAME, DEVICE_NAME, CLIENT, TOPIC):
		try:
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			#CLIENT.publish(TOPIC, '0')
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
				print x, self.recording_event.is_set()
				if(self.recording_event.is_set() == True):
					print "External event signal received. ", PROCESS_NAME, " killed"
					break
			#if(self.recording_event.is_set() != True):
			#	CLIENT.publish(TOPIC, "1")
			pidID = subprocess.check_output(["pidof", PROCESS_NAME]).split()
			x = 0
			for x in range(len(pidID)):
				subprocess.call(["kill", pidID[x]])	
			#print PROCESS_NAME + " killed"
		
		except subprocess.CalledProcessError:
			print "Sending audio file to ", IP_ADDRESS
			if(IP_ADDRESS != None):
				try:
					socket.inet_aton(IP_ADDRESS)
					with self.recording_lock:
						self.file_transfer(f, IP_ADDRESS) 
				except socket.error:
					raise TypeError				
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

class SensorTag(object):
	
	def __init__(self, bluetooth_adr):
		self.con = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive')
		self.con.expect('\[LE\]>', timeout=600)
		print "Preparing to connect. You might need to press the side button..."
		self.con.sendline('connect')
		self.con.expect('Connection successful.*\[LE\]>')
		self.cb = {}
		return
	
	def char_write_cmd(self, handle, value):
		# The 0%x for value is VERY naughty!  Fix this!
		cmd = 'char-write-cmd 0x%02x 0%x' % (handle, value)
		print cmd
		self.con.sendline(cmd)
		return

	def char_read_hnd(self, handle):
		self.con.sendline('char-read-hnd 0x%02x' % handle)
		self.con.expect('descriptor: .*? \r')
		after = self.con.after
		rval = after.split()[1:]
		return [long(float.fromhex(n)) for n in rval]
	
	def notification_loop(self):
		while True:
			try:
				pnum = self.con.expect(['Notification handle = .*? \r', "GLib-WARNING"], timeout=4)
			except:
				continue
			
			if(pnum == 0):
				after = self.con.after
				hxstr = after.split()[3:]
				handle = long(float.fromhex(hxstr[0]))
				
				if True:
					self.cb[handle]([long(float.fromhex(n)) for n in hxstr[2:]])
				pass
			
			elif(pnum == 1):
				print "Sensor tag resetted."
				raise
			else:
				print "TIMEOUT!!"
		pass
	
	def register_cb( self, handle, fn ):
		self.cb[handle]=fn;
		return
					
