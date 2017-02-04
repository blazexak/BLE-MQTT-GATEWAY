import pexpect
import sys
import traceback

mac = "00:00:03:04:28:04"

def multimedia_connect():
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
	
def check_default_sink_source():
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

try:
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

	multimedia_connect()
	check_status = check_default_sink_source()
	print check_status
	
	
except:
	print("Exception was thrown.")
	print("Debug information: ")
#	print(str(child))
