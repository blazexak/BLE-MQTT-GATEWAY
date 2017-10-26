#define power 3

void setup() {
  // put your setup code here, to run once:
  pinMode(power, OUTPUT);
  digitalWrite(power, HIGH);
  
  Bean.enableWakeOnConnect(true);
  delay(100);
  Serial.println("Bean Soil Moisture Sensor");

  Bean.setScratchData(5, (uint8_t *)"300", 3);
  Bean.setScratchData(3, (uint8_t*)"560", 3);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  uint32_t delay1;
  ScratchData scratch5 = Bean.readScratchData(5);
  ScratchData diagnostic = Bean.readScratchData(4);

  if(diagnostic.length == 1){
    Bean.setLed(255,0,0);
    delay(1000);
    uint32_t data = (uint32_t)diagnostic.data[0]-48;
    if(data == 1){
      for(int i = 0; i < 10; i++){
        Bean.setLed(0,255,0); delay(100);Bean.setLed(0,0,255); delay(100);Bean.setLed(0,0,0);delay(100);
      }
      Bean.setLed(0,0,0);
      Bean.setScratchNumber(4,0);
    }
  }
  if(scratch5.length == 0){
    delay1 = 0;
  }
  else if(scratch5.length == 1){
    delay1 = (uint32_t)scratch5.data[0]-48; // comment above line and uncomment this line for BLE app testing
  }
  else if(scratch5.length > 1){
    delay1 = (uint32_t)atoi((char*)scratch5.data);
  }  
  
  uint16_t moisture = analogRead(A1);
  
  Serial.print("Moisture: ");Serial.println(moisture);Serial.println();
  char buffer1[20], raw[20];
  uint8_t percent = convert_percent(moisture);
  Serial.print("Percent: ");Serial.println(percent);Serial.println();
  int n = snprintf(buffer1, 20,"%d", percent);
  int rawN = snprintf(raw, 20,"%d", moisture);
  Bean.setScratchData(1,(uint8_t*)buffer1, n);
  Bean.setScratchData(2,(uint8_t*)raw, rawN);
  
  delay1 = (delay1) * 1000;
  Bean.sleep(delay1);
}

uint8_t convert_percent(uint16_t moisture){
  if(moisture > 560){
    moisture = 560;
  }
  
  ScratchData scratch3 = Bean.readScratchData(3);
  int calibrate;
  uint8_t percent;
  if(scratch3.length == 0){
    calibrate = 0;
  }
  else if(scratch3.length == 1){
    calibrate = (uint32_t)scratch3.data[0]-48; // comment above line and uncomment this line for BLE app testing
  }
  else if(scratch3.length > 1){
    calibrate = (uint32_t)atoi((char*)scratch3.data);
  }    
  percent = map(moisture, 0, calibrate, 0, 100);
  return percent;
}
