#include "FastLED.h"
#ifdef __AVR__
  #include <avr/power.h>
#endif
#include "PinChangeInt.h"

#define NEO_PIN 0
#define NUM_PIXEL 2
CRGB leds[NUM_PIXEL];

void setup() {
  // put your setup code here, to run once:
  LEDS.addLeds<WS2812,NEO_PIN,RGB>(leds,NUM_PIXEL);
  LEDS.setBrightness(84);
  leds[0] = CHSV(0, 0, 0);
  leds[1] = CHSV(0, 0, 0);
  Bean.enableWakeOnConnect(true);
  delay(100);  
}

void loop() {
  // put your main code here, to run repeatedly:
  
  // Read scratch2 Data from Bluetooth Module
  ScratchData scratch = Bean.readscratchData(1);
  ScratchData scratch2 = Bean.readscratchData(2);
  delay(20);  
  
  uint8_t hue, saturation, brightness;
  uint8_t hue2, saturation2, brightness2;
  char hueChar[4], saturationChar[4], brightnessChar[4];
  char hueChar2[4], saturationChar2[4], brightnessChar2[4];
  
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

  if(scratch2.length == 0){
    hue2 = 0;
    saturation2 = 0;
    brightness2 = 0;
    Serial.print("Hue: ");Serial.println(hue2);
    Serial.print("Saturation: ");Serial.println(saturation2);
    Serial.print("Brightness: ");Serial.println(brightness2);
  }
  else if(scratch2.length > 1){
    strncpy(hueChar2, (char*)scratch2.data+0, 3);hueChar2[3] = 0;
    strncpy(saturationChar2, (char*)scratch2.data+4, 3);saturationChar2[3] = 0;
    strncpy(brightnessChar2, (char*)scratch2.data+8, 3);brightnessChar2[3] = 0;
    
    hue2 = atoi(hueChar2);
    saturation2 = atoi(saturationChar2);
    brightness2 = atoi(brightnessChar2);
    Serial.print("Hue: ");Serial.println(hue2);
    Serial.print("Saturation: ");Serial.println(saturation2);
    Serial.print("Brightness: ");Serial.println(brightness2);
  }
  
  
    leds[0] = CHSV(hue, saturation, brightness);
    leds[1] = CHSV(hue2, saturation2, brightness2);
    FastLED.show();
    fadeall();
    delay(10);
}
