/*
 * PIR sensor tester
 */

#include "PinChangeInt.h"
 
int inputPin = 9;               // choose the input pin (for PIR sensor)
int pirState = LOW;             // we start, assuming no motion detected
int val = 0;                    // variable for reading the pin status
int flag = 0;
 
void setup() {
  pinMode(inputPin, INPUT_PULLUP);     // declare sensor as input
  attachPinChangeInterrupt(inputPin, interrupt, CHANGE);
  Bean.enableWakeOnConnect(true);
  
}
 
void loop(){

  if (flag == 1){
    // Check if Falling or Rising Interrupt
    val = digitalRead(inputPin);
    if(val == HIGH){
      Bean.setLed(255,0,0);
      if(pirState ==  LOW){
        Serial.println("Motion detected!");
        Bean.setScratchNumber(1, 1);
        Bean.setScratchNumber(2, (uint8_t)Bean.getTemperature());
        pirState = HIGH;
      }
    }

    else{
      Bean.setLed(0,0,0);
      if (pirState == HIGH){
        Serial.println("Motion ended!");
        Bean.setScratchNumber(1,0);
        Bean.setScratchNumber(2, (uint8_t)Bean.getTemperature());
        pirState = LOW;
      }
    }
  }

  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t dataD = (uint32_t)diagnostic.data[0]-48;
  if(dataD == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }  

  Bean.sleep(0xFFFFFFFF);
}

void interrupt(){
  flag = 1;
}
