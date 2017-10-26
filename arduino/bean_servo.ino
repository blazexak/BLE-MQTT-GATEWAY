/*
 Controlling a servo position using a potentiometer (variable resistor)
 by Michal Rinott <http://people.interaction-ivrea.it/m.rinott>

 modified on 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Knob
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int potpin = 0;  // analog pin used to connect the potentiometer
int val;    // variable to read the value from the analog pin

void setup() {
  myservo.attach(7);  // attaches the servo on pin 9 to the servo object
  Bean.enableWakeOnConnect(true);
}

void loop() {
  myservo.attach(7);
  ScratchData scratch5 = Bean.readScratchData(5);
  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t dataD = (uint32_t)diagnostic.data[0]-48;
  if(dataD == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }  
    
  if(scratch5.length == 0){
    val = 0;
    Serial.print("Value of null: "); Serial.println(val);
  }
  else if(scratch5.length == 1){
    val = (uint32_t)scratch5.data[0]-48; // comment above line and uncomment this line for BLE app testing
    Serial.print("Value of 1 character: "); Serial.println(val);
  }
  else if(scratch5.length > 1){
    val = (uint32_t)atoi((char*)scratch5.data);
    Serial.print("Value of string: "); Serial.println(val);
  }
  myservo.write(val);                  // sets the servo position according to the scaled value
  delay(500);
  Bean.sleep(0xFFFFFFFF);
//  delay(2000);
  Bean.setLed(0,255,0); delay(500);Bean.setLed(0,0,0); delay(500);
}
