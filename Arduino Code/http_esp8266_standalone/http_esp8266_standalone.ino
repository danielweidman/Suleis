#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define NUM_LEDS 100
#define FASTLED_ALLOW_INTERRUPTS 0
#include<FastLED.h>

CRGBArray<NUM_LEDS> leds;

const char* ssid = "HelloNet";
const char* password =  "suleisconnect";
const String ADDRESS = "http://192.168.137.1:5000";

HTTPClient http;
int httpCode; //represents the http code of the response
String payload; //represents the response from the server
StaticJsonBuffer<600> jsonBuffer; //represents jsobBuffer used to parse the JSON response
void setup() {
  FastLED.addLeds<WS2811,D8, BRG>(leds, NUM_LEDS);
  Serial.begin(115200);
  delay(100);
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(50);
    Serial.println("Connecting to WiFi..");
  }
 
  Serial.println("Connected to the WiFi network");
 
}
 
void loop() {
 
  if ((WiFi.status() == WL_CONNECTED)) { //Check the current connection status
 
 
    http.begin(ADDRESS + F("/get_strip_status/1233/")); //Specify the URL
    httpCode = http.GET();                                        //Make the request
    if (httpCode > 0) { //Check for the returning code
        payload = http.getString();
        Serial.println(httpCode);
        //Serial.println(payload);
        process_http_string(payload);
      }
 
    else {
      Serial.println("Error on HTTP request");
      Serial.println(httpCode);
      
      
    }
    //http.end(); //Free the resources
  }
 
  delay(10);
 
}


void process_http_string(String payload){

  char  payload_array[payload.length()+1];
  payload.toCharArray(payload_array, payload.length()+1);

  Serial.println(payload_array);
  jsonBuffer.clear();


  char * pch;
  pch = strtok (payload_array,"*");
  while (pch != NULL)
  {
    Serial.println(pch);

   JsonObject& root = jsonBuffer.parseObject(pch);
  
    // Test if parsing succeeds.
    if (!root.success()) {
      Serial.println("parseObject() failed");
      return;
    }
  
    int start_pixel = root["range_start"];
    int end_pixel = root["range_end"];
    int r = root["range_status"]["color"]["r"];
    int g = root["range_status"]["color"]["g"];
    int b = root["range_status"]["color"]["b"];
    
    // Print values.
    Serial.println(start_pixel);
    Serial.println(end_pixel);
    Serial.println(r);
    set_range(start_pixel, end_pixel, CRGB(r,g,b));
   
    jsonBuffer.clear();
    pch = strtok (NULL, "*");
  }



}


void set_range(int start_pixel, int end_pixel,CRGB color){
  Serial.println("hi");
  
  
  for (int i = start_pixel; i<=end_pixel; i++){
    leds[i] = color;
  }
  
  //leds(start_pixel, end_pixel) = color;
  
  //leds[start_pixel].b = 0;
  FastLED.delay(33);
}
