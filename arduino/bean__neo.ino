#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN 0
#define NUM_PIXEL 16

// Parameter 1 = number of pixels in strip
// Parameter 2 = Arduino pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_PIXEL, PIN, NEO_GRB + NEO_KHZ800);

// IMPORTANT: To reduce NeoPixel burnout risk, add 1000 uF capacitor across
// pixel power leads, add 300 - 500 Ohm resistor on first pixel's data input
// and minimize distance between Arduino and first pixel.  Avoid connecting
// on a live circuit...if you must, connect GND first.

void setup() {
  strip.begin();
  strip.show();
  // Configure Bean to wake up when a client connects
  Bean.enableWakeOnConnect(true);
  delay(100);
}

void loop() {
    // Read Scratch Data from Bluetooth Module
    ScratchData scratch = Bean.readScratchData(1);
    delay(20);
    ScratchData scratch2 = Bean.readScratchData(2);
    delay(20);
    ScratchData scratch3 = Bean.readScratchData(3);
    delay(20);
    ScratchData scratch4 = Bean.readScratchData(4);
    delay(20);
    uint8_t* data[4] = {scratch.data, scratch2.data, scratch3.data, scratch4.data};
    uint8_t dataLength[4] = {scratch.length, scratch2.length, scratch3.length, scratch4.length};

    int NeoStates[5];
    for(int i = 0; i < 5; i++){
      if(dataLength[i] == 0){
        NeoStates[i] = 0;
      }
      else if(dataLength[i] == 1){
        NeoStates[i] = int(data[i]);
      }
      else if(dataLength[i] > 1){
        NeoStates[i] = atoi((char*)data[i]);
      }
    }

    // Convert RGB values to color value
    uint32_t colorValue = strip.Color(NeoStates[0], NeoStates[1], NeoStates[2]);

    // Apply RGB BRIGHTNESS Values to all pixels
    for(int i = 0; i < NUM_PIXEL; i++){
      strip.setPixelColor(i, colorValue, NeoStates[3]);
    }
    strip.show();
    delay(5);
}
