//RFID uses Software Serial
#include <SoftwareSerial.h>
//iButton uses OneWire
#include <OneWire.h>

//iButton Variables
OneWire  ds(7);
byte addr[8];
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
  Serial.println("ready");
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
      int i;
      //For CSH iButtons there are 7 code segments in hexidecimal 
      for( i = 7; i >= 0; i--) {
        
        //Adds leading zeros to hex if only one character long
        if( addr[i] < 0x10){ 
        Serial.print("0");
        }
        
        //Prints rest of hex
       Serial.print(addr[i], HEX);
       
      }
      
       //Keep a delay so that it doesn't mistakenly read the same iButton more than once
      delay(1000);
      //Makes a new line
      Serial.println();
      
  }
  else if (keyStatus!="") {
    Serial.print(keyStatus);
  }
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

  keyStatus="ok";
  ds.reset();
}
