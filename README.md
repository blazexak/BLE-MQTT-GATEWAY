# BLE-MQTT-GATEWAY
BLE MQTT PROJECT
A python module with BLE and MQTT classess for working with BLE device together with MQTT protocol.

## Install Denpendancies Library:
```
sudo apt-get install mosquitto mosquitto-clients libglib2.0-dev
sudo pip install paho-mqtt bluepy pexpect
```

## Setup

### Enable Node-Red on Startup:
```
sudo systemctl enable nodered.service
```

### Run Hcitool without sudo

```
sudo apt-get install libcap2-bin
sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`
getcap !$
```
Check using:
```
hcitool -i hci0 lescan
```
