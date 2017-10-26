#include "PinChangeInt.h"

#define pin0 4
#define pin1 3
#define pin2 2
#define pin3 1
#define pin4 0

int flag0 = 0, flag1 = 0, flag2 = 0, flag3 = 0, flag4 = 0;
long debouncing_time = 50; //Debouncing Time in Milliseconds
volatile unsigned long last_micros;

void setup() {
  // put your setup code here, to run once:
  pinMode(pin0, INPUT_PULLUP);
  pinMode(pin1, INPUT_PULLUP);
  pinMode(pin2, INPUT_PULLUP);
  pinMode(pin3, INPUT_PULLUP);
  pinMode(pin4, INPUT_PULLUP);
  attachPinChangeInterrupt(pin0, interrupt0, FALLING);  
  attachPinChangeInterrupt(pin1, interrupt1, FALLING);  
  attachPinChangeInterrupt(pin2, interrupt2, FALLING);  
  attachPinChangeInterrupt(pin3, interrupt3, FALLING);  
  attachPinChangeInterrupt(pin4, interrupt4, FALLING);  

Bean.enableWakeOnConnect(true);
}

void loop() {
  // put your main code here, to run repeatedly:
  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t dataD = (uint32_t)diagnostic.data[0]-48;
  if(dataD == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }  
    
  if(flag0 == 1){
    detachPinChangeInterrupt(pin0);
    flag0 = 0;
    Bean.setScratchData(1,(uint8_t*)"1,0,0,0,0", 9)  ;
    attachPinChangeInterrupt(pin0, interrupt0, FALLING); 
  }
  else if(flag1 == 1){
    detachPinChangeInterrupt(pin1);
    flag1 = 0;
    Bean.setScratchData(1,(uint8_t*)"0,1,0,0,0", 9)  ;
    attachPinChangeInterrupt(pin1, interrupt1, FALLING); 
  }
  else if(flag2 == 1){
    detachPinChangeInterrupt(pin2);
    flag2 = 0;
    Bean.setScratchData(1,(uint8_t*)"0,0,1,0,0", 9)  ;
    attachPinChangeInterrupt(pin2, interrupt2, FALLING); 
  }
  else if(flag3 == 1){
    detachPinChangeInterrupt(pin3);
    flag3 = 0;
    Bean.setScratchData(1,(uint8_t*)"0,0,0,1,0", 9)  ;
    attachPinChangeInterrupt(pin3, interrupt3, FALLING); 
  }
  else if(flag4 == 1){
    detachPinChangeInterrupt(pin4);
    flag4 = 0;
    Bean.setScratchData(1,(uint8_t*)"0,0,0,0,1", 9)  ;
    attachPinChangeInterrupt(pin4, interrupt4, FALLING); 
  }

  Bean.sleep(0xFFFFFFFF);
}

void interrupt0(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag0 = 1;
    last_micros = micros();
  }
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

void interrupt3(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag3 = 1;
    last_micros = micros();
  }
}

void interrupt4(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag4 = 1;
    last_micros = micros();
  }
}