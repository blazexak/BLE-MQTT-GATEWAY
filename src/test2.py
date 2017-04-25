import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):      
    client.subscribe("diagnostic")

def custom(client, userdata, msg):
    print client, userdata, msg.payload

print "start"                
client = mqtt.Client()
client.on_connect = on_connect
print "Connecting"
client.connect("192.168.1.9", 1883,60)
print "Connected"

client.message_callback_add("diagnostic", custom)

client.loop_forever()