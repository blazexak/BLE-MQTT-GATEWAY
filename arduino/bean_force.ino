
// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Bean.enableWakeOnConnect(true);
  delay(100);
}

// the loop routine runs over and over again forever:
void loop() {

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

  
  // read the input on analog pin 0:
  char buffer1[20];
  int sensorValue = analogRead(A0);
  int n = snprintf(buffer1, 20, "%d", sensorValue);
  Bean.setScratchData(1,(uint8_t*)buffer1, n);
  // print out the value you read:
  Serial.println(sensorValue);
  delay(250);        // delay in between reads for stability
}
