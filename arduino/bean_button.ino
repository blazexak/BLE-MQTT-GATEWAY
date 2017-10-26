#include "FastLED.h"
#ifdef __AVR__
  #include <avr/power.h>
#endif
#include "PinChangeInt.h"

//int potPin = 1;    // select the input pin for the potentiometer
int button = 2;
int toggle = 0;
#define NEO_PIN 1
#define NUM_PIXEL 1
int flag = 0;
long debouncing_time = 300; //Debouncing Time in Milliseconds
volatile unsigned long last_micros;
CRGB leds[NUM_PIXEL];

void interrupt();

void setup() {
  pinMode(button, INPUT_PULLUP);
  attachPinChangeInterrupt(button, interrupt, FALLING);

  LEDS.addLeds<WS2812,NEO_PIN,RGB>(leds,NUM_PIXEL);
  LEDS.setBrightness(84);
  Bean.enableWakeOnConnect(true);
  delay(100);  
}

void fadeall() { for(int i = 0; i < NUM_PIXEL; i++) { leds[i].nscale8(250); } }

void loop() {
  if(flag == 1){
    detachPinChangeInterrupt(button);
    flag = 0;
    if(toggle == 0){
      toggle = 255;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(5, (uint8_t*)"11", 2);
    }
    else if(toggle == 255){
      toggle = 0;
      Bean.setLed(toggle,0,0);
      Bean.setScratchData(5, (uint8_t*)"00", 2);
    }    
    attachPinChangeInterrupt(button, interrupt, FALLING);
  }
  
  // Read Scratch Data from Bluetooth Module
  ScratchData scratch = Bean.readScratchData(1);
  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t data = (uint32_t)diagnostic.data[0]-48;
  if(data == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }
  
  
  uint8_t hue, saturation, brightness;
  char hueChar[4], saturationChar[4], brightnessChar[4];

  if(scratch.length == 0){
    hue = 0;
    saturation = 0;
    brightness = 0;
    Serial.print("Hue: ");Serial.println(hue);
    Serial.print("Saturation: ");Serial.println(saturation);
    Serial.print("Brightness: ");Serial.println(brightness);
  }
  else if(scratch.length > 1){
    strncpy(hueChar, (char*)scratch.data+0, 3);hueChar[3] = 0;
    strncpy(saturationChar, (char*)scratch.data+4, 3);saturationChar[3] = 0;
    strncpy(brightnessChar, (char*)scratch.data+8, 3);brightnessChar[3] = 0;
    
    hue = atoi(hueChar);
    saturation = atoi(saturationChar);
    brightness = atoi(brightnessChar);
    Serial.print("Hue: ");Serial.println(hue);
    Serial.print("Saturation: ");Serial.println(saturation);
    Serial.print("Brightness: ");Serial.println(brightness);
  }
  
  
    leds[0] = CHSV(hue, saturation, brightness);
    FastLED.show();
    fadeall();
    delay(10);
    
}

void interrupt(){
  if((long)(micros() - last_micros) >= debouncing_time * 1000) {
    flag = 1;
    last_micros = micros();
  }
}