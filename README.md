# BLE-MQTT-GATEWAY
BLE-MQTT PROJECT

The sensor network is made up of two core hardware components; a central gateway (Raspberry Pi) and bluetooth low energy (BLE) wireless devices. The BLE wireless devices are categorised to two groups; sensors and actuators. Refer below for the list of sensors and actuators that are currently supported. The aim of this project is to engineer a flexible platform that allows the user to quickly connect sensors and actuators together for rapid prototyping purposes. By routing all data streams from the BLE sensors to the central gateway, this approach allow us to easily manipulate the generated data and transform it to suitable form that can be consumed by the wireless BLE actuators. The diagram below gives a high level view of the network architecture used to contruct this sensor network.

![Alt text](/pictures/sensor_network.jpeg.jpg?raw=true "Optional Title")

A flow based graphical programming user interface, NodeRed is used to represent each sensors and actuators as a graphical "block" that can be quickly "rewired" to connect one sensor with another without having to change extensive amount of code. The example below demonstrated a rapid prototyped "Singing Plant" application that used two wireless sensors (motion sensor and moisture sensor) and two wireless actuators (eink display and speaker). Each device is represented as a virtual purple block and the sensor blocks are connected to a orange "logic" block which manipulate the data using Javascript to produce suitable form of data before sending it to the actuator blocks. In this application, the moisture sensor was sensing the moisture reading of a potted plant soil and the motion sensor was actively sensing human presence. If the plant needed to be watered and a person happened to be nearby, the speaker will play a bird chirping sound and a personalised message to engage with people to water the plants.

![Alt text](/pictures/flow_example.jpg?raw=true "Optional Title")

In the backend, the connection of each wireless BLE sensor and actuator are governed by their individual python program. One of the future work will be having only one python program that is responsible of handling multiple connections with sensors and actuators. As depicted in the first diagram, BLE channel is used for data transmission between sensor to the central gateway and the central gateway to the actuators. The MQTT protocol is used as a data transmission channel between the individual python program to the NodeRed, graphical user interface. The data originating from each wireless device is assigned a unique "topic" to keep track and manipulate the data at the front end. On the NodeRed's dashboard, a single MQTT block can be configured using the unique "topic" to receive the data from a specific sensor. In the second diagram, each sensor and actuator are represented using a purple block which in fact is a MQTT type block but was cosmetically renamed to keep track which sensor the block is connected to. Similarly, a MQTT block can also be configured using the unique "topic" of a wireless actuator to send data coming out from a "logic" block to the backend python program. The python program will transmit the data through the BLE channel to the physical wireless actuator.

The python module in this repository consists of a BLE and MQTT classess for working with BLE devices together with MQTT protocol.
Below are the dependencies required to set up the MQTT server and BLE on Raspberry Pi. NodeRed is a default package included in the official Raspberry Pi Pixel image.


## Install Denpendancies Library for MQTT and MQTT:
```
sudo apt-get install mosquitto mosquitto-clients libglib2.0-dev
sudo pip install paho-mqtt bluepy pexpect pyyaml
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
