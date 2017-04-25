import pexpect
import sys
import traceback
import sys
import subprocess
import time

mac = "00:00:01:04:33:71"
mac_id = mac.replace(':', '_')
print mac_id

def multimedia_connection_status():
    try:
        command = 'bluetoothctl'
        child = pexpect.spawn(command)
        child.logfile = open("/tmp/mylog", "w")
        child.sendline('info ' + mac, timeout=1)
        child.expect("Connected: yes")
        return True
    except:
        print("Exception was thrown. Multimedia connection status.")
        print("Debug information: ")
        #traceback.print_exception()
        print(str(child))
        return False
        
def multimedia_connect():
    try:
        command = 'bluetoothctl'
        child = pexpect.spawn(command)
        child.logfile = open("/tmp/mylog", "w")
        child.sendline('power on')
        child.expect("Changing power on succeeded")
        child.sendline('agent on')
        child.sendline('default-agent')
        child.sendline('scan on')
        child.sendline("pair 00:00:03:04:28:04")
        child.sendline("trust 00:00:03:04:28:04")
        child.expect("trust succeeded")
        pidID = subprocess.check_output(["pidof", "pulseaudio"]).split()
        x = 0
        for x in range(len(pidID)):
           subprocess.call(["kill", pidID[x]])
        time.sleep(1)
        child.sendline("connect 00:00:03:04:28:04")
        child.expect("Connection successful")
        child.sendline('scan off')
        child.close()
    except:
        print("Exception was thrown. Multimedia connecting.")
        print("Debug information: ")
        print sys.exc_info()
        traceback.print_exception()
        print(str(child))
    
def check_default_sink_source():
    try:
        command = "pacmd"
        child = pexpect.spawn(command)
        child.logfile = open("/tmp/mylog", "w")
        child.sendline("stat")
        code1 = child.expect("Default sink name: bluez_sink." + mac_id, timeout=1)  # \r\n", pexpect.TIMEOUT)
        code2 = child.expect("Default source name: bluez_source." + mac_id, timeout=1)  # , pexpect.TIMEOUT)
        child.close
        
        if(code1 == 0 and code2 == 0):
            return True
        else:
            return False
    except:
        print("Exception was thrown. Checking default sink source.")
        print("Debug information: ")
#         traceback.print_exc()
        print(str(child))
        return False
    
def set_default_sink_source():
    try:
        command = "pacmd"
        child = pexpect.spawn(command)
        child.logfile = open("/tmp/mylog", "w")
        child.sendline("set-default-sink bluez_sink." + mac_id)
        child.sendline("set-default-source bluez_source." + mac_id)   
        return True 
    except:
        print("Exception was thrown. Setting default sink source")
        print("Debug information: ")
#         traceback.print_exc()
        print(str(child))
        return False        
# command = 'bluetoothctl'
# child = pexpect.spawn(command)
# child.logfile = open("/tmp/mylog", "w")
# child.sendline('power on')
# # child.sendline("pair 00:00:01:04:33:71")
# # child.sendline("trust 00:00:01:04:33:71")
# child.sendline("connect 00:00:01:04:33:71")
# results = child.expect(["Connection successful"])
# print results

# command = "pacmd set-default-sink"
try:
    connected = multimedia_connection_status()
    print(connected)
    if(connected == False):
        multimedia_connect()
    check_status = check_default_sink_source()
    print check_status
    if(check_status == False):
        status = set_default_sink_source()
        print status
except:
    print("Exception was thrown.")
    print("Debug information: ")
#     print(str(child))
