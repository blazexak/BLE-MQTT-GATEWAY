#include <Wire.h>
#include <Adafruit_MLX90614.h>
#define power 3

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

void setup() {
  // configuring power pin for temperature sensor
  pinMode(power, OUTPUT);
  digitalWrite(power, HIGH);
  
  Bean.enableWakeOnConnect(true);
  delay(100);
  Serial.println("Adafruit MLX90614 test");
//  mlx.begin();
  Bean.setScratchData(5, (uint8_t *)"5", 1);
}

void loop() {
  ScratchData diagnostic = Bean.readScratchData(4);

  uint32_t dataD = (uint32_t)diagnostic.data[0]-48;
  if(dataD == 1){
    for(int i = 0; i < 10; i++){
      Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(255,0,0);delay(100);
    }
    Bean.setLed(0,0,0);
    Bean.setScratchNumber(4,0);
  }
    
  uint32_t delay1;
  ScratchData scratch5 = Bean.readScratchData(5);
  if(scratch5.length == 0){
    delay1 = 0;
    Serial.print("Value of null: "); Serial.println(delay1);
  }
  else if(scratch5.length == 1){
    delay1 = (uint32_t)scratch5.data[0]-48; // comment above line and uncomment this line for BLE app testing
    Serial.print("Value of 1 character: "); Serial.println(delay1);
  }
  else if(scratch5.length > 1){
    delay1 = (uint32_t)atoi((char*)scratch5.data);
    Serial.print("Value of string: "); Serial.println(delay1);
  }  
  
  uint8_t data[2];
  char buffer[3];

  digitalWrite(power, HIGH);
  delay(100);
  mlx.begin();
  delay(100);
  data[1] = (uint8_t)mlx.readAmbientTempC();
  data[0] = (uint8_t)mlx.readObjectTempC();
  digitalWrite(power, LOW);
  Serial.print("Ambient = "); Serial.println(data[1]);
  Serial.print("tObject = "); Serial.println(data[0]);

  Bean.setScratchNumber(1, data[0]);
  delay(100);
  Bean.setScratchNumber(2, data[1]);
  
  delay1 = (delay1) * 1000;
  Bean.sleep(delay1);
}
