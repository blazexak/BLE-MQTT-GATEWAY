import os
import subprocess
import time
import socket

class Bluetooth_Speaker_Mic(object):
    
    def __init__(self, NAME, MAC_ADDRESS, PLAYBACK_DIR, RECORD_DIR):
        self.name = NAME
        self.mac = MAC_ADDRESS
        self.play_dir = PLAYBACK_DIR
        self.record_dir = RECORD_DIR
        
        d = os.path.dirname(self.play_dir)
        if not os.path.exists(d):
            os.makedirs(d)
            
        d = os.path.dirname(self.record_dir)
        if not os.path.exists(d):
            os.makedirs(d)            
        
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
            
    def playback(self, DELETE=None):
        f = self.files_in_directory(self.play_dir)
        if (f != -1):
            subprocess.call(["aplay", self.play_dir+f[0]])
            if(DELETE == True):
                subprocess.call(["sudo", "rm", self.play_dir+f[0]])
        else:
            print "No audio available."
        
    def record(self, IP_ADDRESS=None):
        f = time.strftime("%Y%m%d%H%M%S") + ".wav"
        subprocess.call(["arecord", "-D", "plughw:1", "--duration=10", "-f", "dat", self.record_dir+f])
        if(IP_ADDRESS != None):
            try:
                socket.inet_aton(IP_ADDRESS)
            except socket.error:
                raise TypeError 
            
        self.file_transfer(f, IP_ADDRESS)         
            
          
    def file_transfer(self, FILE, IP_ADDRESS):
        subprocess.call(["ssh", IP_ADDRESS, 'mkdir -p '+ self.record])
        subprocess.call(["scp", self.record_dir+FILE, "pi@"+IP_ADDRESS+":"+self.record_dir])
        subprocess.call(["sudo", "rm", self.record_dir+FILE])                    
            
        

        