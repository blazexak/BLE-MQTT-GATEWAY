import socket

try:
    socket.inet_aton("092.168.1.1")
    print "valid ip"
except socket.error:
    # Not legal
    print "invalid ip"
    
    
    
    
class test(object):
    def __init__(self, name = None, status=None):
        self.name = name
        if(name != None):
            print name
            
        if(status == True):
            print "status is True"
            
test1 = test(status = True, name = "Zen")            