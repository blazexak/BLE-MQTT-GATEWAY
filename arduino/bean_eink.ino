// Holds the last data we read from scratch characteristic 1

#include <BeanSmartEinkOpt.h>
#include <SPI.h>
#define power 4
#define ss    2

E_ink Eink;

void setup() {
  // We don't need to set anything up here
  pinMode(ss, OUTPUT);
  digitalWrite(ss, LOW);
  pinMode(power, OUTPUT);
  digitalWrite(power, HIGH);
  
  // Configure Bean to wake up when a client connects
  Bean.enableWakeOnConnect(true);
  delay(1000);
  
  Eink.InitEink();
  
  Eink.ClearScreen();// clear the screen
  Eink.RefreshScreen();
  Eink.EinkP8x16Str(14,8,"QUT IOT LAB");
  Eink.EinkP8x16Str(10,8,"S1025");
  Eink.EinkP8x16Str(6,8,"EINK BOARD");
  Eink.EinkP8x16Str(2,8,"=============");
  Eink.RefreshScreen();
//  delay(1000);
//  digitalWrite(power, LOW);   
}

void loop() {
  
  uint8_t* previousData[4] = {0,0,0,0};
  uint8_t updateFlag1 = 1, updateFlag2 = 1;
  uint8_t previousDataLength[4] = {0,0,0,0};


  
  while(1){    
    ScratchData scratch = Bean.readScratchData(1);
    delay(10);
    ScratchData scratch2 = Bean.readScratchData(2);
    delay(10);
    ScratchData scratch3 = Bean.readScratchData(3);
    delay(10);
    ScratchData scratch4 = Bean.readScratchData(4);
    delay(10);
    uint8_t* data[4] = {scratch.data, scratch2.data, scratch3.data, scratch4.data};
    uint8_t dataLength[4] = {scratch.length, scratch2.length, scratch3.length, scratch4.length};

//    digitalWrite(power, HIGH);
    delay(100);
    Eink.InitEink();      
    Eink.InitEink();
    Eink.ClearScreen();
    Eink.EinkP8x16Str(14,8,(char*)scratch.data);
    Eink.EinkP8x16Str(10,8,(char*)scratch2.data);
    Eink.EinkP8x16Str(6,8,(char*)scratch3.data);
    Eink.EinkP8x16Str(2,8,(char*)scratch4.data);
    Eink.RefreshScreen();
    delay(100);
//    digitalWrite(power, LOW);
    
    updateFlag1 = 0;
    updateFlag2 = 0;
    for(int i = 0; i < 4; i++){
      previousData[i] = data[i];
      previousDataLength[i] = dataLength[i];
    }

    Serial.print("Previous data: "); Serial.println((char*)previousData[0]);
    Bean.sleep(0xFFFFFFFF); 
    
    Bean.setLed(0,255,0);
    delay(1000);
    Bean.setLed(0,0,0);
    delay(4000);
  }
}
