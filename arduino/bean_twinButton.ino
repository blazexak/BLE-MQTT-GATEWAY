#include "PinChangeInt.h"

#define button1 0 
#define button2 3

int toggle = 0;
int flag1 = 0;
int flag2 = 0;
long debouncing_time = 50; //Debouncing Time in Milliseconds
volatile unsigned long last_micros;

void interrupt1();
void interrupt2();

void setup() {
  pinMode(button1, INPUT_PULLUP);
  attachPinChangeInterrupt(button1, interrupt1, FALLING);
//  
  pinMode(button2, INPUT_PULLUP);    
  attachPinChangeInterrupt(button2, interrupt2, FALLING);

  Bean.enableWakeOnConnect(true);
  delay(100);  
}

void loop() {
  if(flag1 == 1){
    detachPinChangeInterrupt(button1);
    flag1 = 0;
    if(toggle == 0){
      toggle = 255;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(1, (uint8_t*)"11", 2);
    }
    else if(toggle == 255){
      toggle = 0;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(1, (uint8_t*)"00", 2);
    }    
    attachPinChangeInterrupt(button1, interrupt1, FALLING);
  }


  if(flag2 == 1){
    detachPinChangeInterrupt(button2);
    flag2 = 0;
    if(toggle == 0){
      toggle = 255;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(2, (uint8_t*)"11", 2);
    }
    else if(toggle == 255){
      toggle = 0;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(2, (uint8_t*)"00", 2);
    }    
    attachPinChangeInterrupt(button2, interrupt2, FALLING);
  }  
  
  // Read Scratch Data from Bluetooth Module
  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t data = (uint32_t)diagnostic.data[0]-48;
  if(data == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }
  
     
    Bean.sleep(0xFFFFFFFF); 
//    Bean.setLed(0,0,255); delay(1000);Bean.setLed(0,0,0);
}

void interrupt1(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag1 = 1;
    last_micros = micros();
  }
}

void interrupt2(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag2 = 1;
    last_micros = micros();
  }
}
