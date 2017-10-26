#define power 4
int potPin = A0;    // select the input pin for the potentiometer
int val, previous, range = 3;
char buffer1[20];
void setup() {
  pinMode(power, OUTPUT);
  digitalWrite(power, HIGH);
  Serial.println("Testing pot.");
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
    
  val = analogRead(potPin);    // read the value from the sensor
  Serial.print("Val: ");Serial.println(val);//Serial.println();
  if((val <=( previous-range)) || (val >= (previous+range))){
    Serial.println("In");
    int n = snprintf(buffer1, 20, "%d", val);
    Bean.setScratchData(1,(uint8_t*)buffer1, n);
  }
  Serial.print("Buffer: ");Serial.println(buffer1);Serial.println();
  previous = val;
  
  delay(1000);
}
