//RFID uses Software Serial
#include <SoftwareSerial.h>
//iButton uses OneWire
#include <OneWire.h>

//iButton Variables
OneWire  ds(7);
byte addr[7];
int but[6] = {0,149,107,48,13,0};
String keyStatus = "";

//RFID Variables
SoftwareSerial RFID(2, 3);
String msg;

void setup()  
{
  //Set up RFID
  Serial.begin(9600);
  RFID.begin(9600);
  //Set up iButton
  pinMode(13, OUTPUT);
  //Print a ready message
  Serial.println("Everything's Ready!");
}

//The char in iButton
char c;

void loop(){
  
  //Checks serial for RFID info
  checkRFID();
  //Checks OneWire for iButton info
  checkiButton();
  
}

void checkRFID() {
  
  //When there is RFID info available, read through each character
  while(RFID.available() > 0){
    c=RFID.read();
    msg += c;
  }
  //When the RFID info length is 14, print it and set message to null
  if (msg.length() == 14) {
    Serial.println(msg);
    //Keep a delay so that it doesn't mistakenly read the same iButton more than once
    delay(1000);
  }
  msg = "";
  delay(200);
  
}

void checkiButton() {
  
  //Get info on the key
  getKeyCode();
  //if the key is good go through this
  if(keyStatus=="ok"){
      byte i;
      //For CSH iButtons there are 7 code segments in hexidecimal 
      for( i = 7; i > 0; i--) {
        
        //Adds leading zeros to hex if only one character long
        if( addr[i] < 0x10){ 
        Serial.print("0");
        }
        
        //Prints rest of hex
       Serial.print(addr[i], HEX);
       
      }
      //Adds 01 at the end of iButton info since all CSHers have that at the end
      Serial.print("01");
       //Keep a delay so that it doesn't mistakenly read the same iButton more than once
      delay(1000);
      //Makes a new line
      Serial.println();
      
      //Makes LED on Arduino blink so we know iButton was read
      if(addr[1] == but[1] && addr[2] == but[2] && addr[3] == but[3] && addr[4] == but[4]){
      digitalWrite(13, HIGH);
      delay(500);
      digitalWrite(13, LOW);}
      else {digitalWrite(13, LOW);}
  }
  else if (keyStatus!="") { Serial.print(keyStatus);}
  
}

//This does a lot of weird stuff about seeing if the data in the iButton is worth getting
void getKeyCode(){
  byte present = 0;
  byte data[12];
  keyStatus="";
  
  if ( !ds.search(addr)) {
      ds.reset_search();
      return;
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
      keyStatus="CRC invalid";
      return;
  }
  
  if ( addr[0] != 0x01) {
      keyStatus="not DS1990A";
      return;
  }
  keyStatus="ok";
  ds.reset();
}
