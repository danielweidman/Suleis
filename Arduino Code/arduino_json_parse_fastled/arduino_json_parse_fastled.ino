//#include <SoftwareSerial.h>

#include <ArduinoJson.h>
#include<FastLED.h>
#define MAX_SECTION_COUNT 6
#define NUM_LEDS 100
//#define FASTLED_ALLOW_INTERRUPTS 0

CRGBArray<NUM_LEDS> leds;



int starts[MAX_SECTION_COUNT];
int ends[MAX_SECTION_COUNT];
String mode_codes[MAX_SECTION_COUNT];
int reds[MAX_SECTION_COUNT];
int greens[MAX_SECTION_COUNT];
int blues[MAX_SECTION_COUNT];
uint8_t special_gHue[MAX_SECTION_COUNT]; // rotating "base color" used by many of the patterns
bool special_bools[MAX_SECTION_COUNT];
int special_ints[MAX_SECTION_COUNT];
int special_move_speed = 1; //currenntly used for 'sp' mode
CRGB *special_led_ptr;

int last_index = 0;

StaticJsonBuffer<300> jsonBuffer; //represents jsobBuffer used to parse the JSON response

void setup() {
  FastLED.addLeds<WS2811, 11, BRG>(leds, NUM_LEDS);
  //FastLED.setDither( 0 );
  //fromESP.begin(9600);
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:


  while (Serial.read() != '!') {
    //long millis_tracker = millis();
    process_lights();
    //Serial.println(millis()-millis_tracker);
    delay(35);

  }
  delay(10);


  Serial.println("avail");


  String json_in = "";
  json_in = Serial.readStringUntil('*');
  Serial.println(json_in);
  JsonObject& root = jsonBuffer.parseObject(json_in);
  if (root.success()) {
    int s = root["S"];
    int e = root["E"];
    int r = root["C"]["r"];
    int g = root["C"]["g"];
    int b = root["C"]["b"];
    int index = root["i"];
    String mode_code = root["M"];
    set_range_arrays(index, s, e, mode_code, r, g, b);
  }

  jsonBuffer.clear();


  //Serial.println(mode_codes_first[13]);


}


void set_range_arrays(int index, int start_led, int end_led, String mode_code, int r, int g, int b) {
  Serial.println(index);
  Serial.println(mode_code);

  starts[index] = start_led;
  ends[index] = end_led;
  mode_codes[index] = mode_code;
  if (mode_code == "so") {
    special_bools[index] = true;
  }
 
  reds[index] = r;
  greens[index] = g;
  blues[index] = b;

  last_index = index;

  for (int j = index; j < MAX_SECTION_COUNT; j++) {
    if (mode_codes[j] == "") {
      break;
    }
    last_index = j;
  }

}

void process_lights() {
  //Serial.println(reds[0]);
  //Serial.println(last_index);

  for (int i = 0; i <= last_index; i++) {

    if (mode_codes[i] == "so") {
      int to_set_r = leds[starts[i]].r;
      int to_set_g = leds[starts[i]].g;
      int to_set_b = leds[starts[i]].b;
      if (special_bools[i]) { //indicates fade process still occuring


        to_set_r = round((1.8 * to_set_r + 0.2 * reds[i]) / 2);
        to_set_g = round((1.8 * to_set_g + 0.2 * greens[i]) / 2);
        to_set_b = round((1.8 * to_set_b + 0.2 * blues[i]) / 2);

        if (abs(to_set_r - reds[i]) < 80) {
          to_set_r = round((1.6 * to_set_r + 0.4 * reds[i]) / 2);
        }

        if (abs(to_set_g - greens[i]) < 80) {
          to_set_g = round((1.6 * to_set_g + 0.4 * greens[i]) / 2);
        }

        if (abs(to_set_b - blues[i]) < 80) {
          to_set_b = round((1.6 * to_set_b + 0.4 * blues[i]) / 2);
        }

        if ((greens[i]) < 30 ) {
          to_set_g = round((1.6 * to_set_g + 0.4 * greens[i]) / 2);
        }
        if ((reds[i]) < 30 ) {
          to_set_r = round((1.6 * to_set_r + 0.4 * reds[i]) / 2);
        }
        if ((blues[i]) < 30 ) {
          to_set_b = round((1.6 * to_set_b + 0.4 * blues[i]) / 2);
        }

        if (abs(to_set_r - reds[i]) < 7) {
          to_set_r = reds[i];
        }
        if (abs(to_set_g - greens[i]) < 7) {
          to_set_g = greens[i];
        }
        if (abs(to_set_b - blues[i]) < 7) {
          to_set_b = blues[i];
        }


        if ((to_set_b == blues[i]) and (to_set_r == reds[i]) and (to_set_g == greens[i])) {
          special_bools[i] = false;
        }

      }



      CRGB to_set = CRGB(to_set_r, to_set_g, to_set_b);
      for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
        leds[led_num] = to_set;

      }

    }
    else if (mode_codes[i] == "cc") {

      EVERY_N_MILLISECONDS( 51 ) {
        special_gHue[i]++; // slowly cycle the "base color" through the rainbow
      }

      CHSV to_set = CHSV(special_gHue[i], 255, 255);
      for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
        leds[led_num] = to_set;

      }

    }
    else if (mode_codes[i] == "rb") {
      EVERY_N_MILLISECONDS( 51 ) {
        special_gHue[i]++; // slowly cycle the "base color" through the rainbow
      }
      special_led_ptr = &leds[starts[i]];


      fill_rainbow( special_led_ptr, ends[i] - starts[i], special_gHue[i], 7);

    }
    else if (mode_codes[i] == "cs") {

      EVERY_N_MILLISECONDS( 16 ) {
        special_gHue[i]++; // slowly cycle the "base color" through the rainbow
      }
      EVERY_N_MILLISECONDS( 26 ) {
        special_bools[i] = !special_bools[i]; // slowly cycle the "base color" through the rainbow
      }
      //Serial.println(special_bools[i]);



      if (!special_bools[i]) {
        CRGB to_set = CRGB(0, 0, 0); //this was of setting it might be bad
        for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
          leds[led_num] = to_set;

        }
      }
      else {
        CHSV to_set = CHSV(special_gHue[i], 255, 255);
        for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
          leds[led_num] = to_set;

        }
      }

    }
    else if (mode_codes[i] == "ws") {


      EVERY_N_MILLISECONDS( 26 ) {
        special_bools[i] = !special_bools[i];
      }
      //Serial.println(special_bools[i]);
      if (!special_bools[i]) {
        CRGB to_set = CRGB(0, 0, 0);
        for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
          leds[led_num] = to_set;

        }
      }
      else {
        CRGB to_set = CRGB(255, 255, 255);
        for (int led_num = starts[i]; led_num <= ends[i]; led_num++) {
          leds[led_num] = to_set;

        }
      }
    }
    
    else if (mode_codes[i] == "pp"){
      EVERY_N_MILLISECONDS(20){
        special_gHue[i]+=4; // slowly cycle the "base color" through the rainbow
        
      
      if (special_ints[i]<starts[i] or special_ints[i]>ends[i]){ //memory-efficient way of dealing with first iteration
          special_ints[i] = starts[i];
      }
        
      if (special_bools[i]) { //moving up in numbers
        leds(starts[i], ends[i]).fadeToBlackBy(60);
        CHSV to_set = CHSV(special_gHue[i], 255, 255);
        
        leds[special_ints[i]] = to_set;
        if(special_ints[i]<ends[i]) { //still moving up
          special_ints[i]++;
        }
        else{ //reached the end
          //special_ints[i] = starts[i];
          special_bools[i] = false;
        }
        
      }
      else { //moving down in numbers
        leds(starts[i], ends[i]).fadeToBlackBy(60);
        CHSV to_set = CHSV(special_gHue[i], 255, 255);

        leds[special_ints[i]] = to_set;
        if(special_ints[i]>starts[i]) { //still moving up
          special_ints[i]--;
        }
        else{ //reached the end
          //special_ints[i] = ends[i];
          special_bools[i] = true;
        }
      }        
      }
    }
    else if (mode_codes[i] == "sp"){ //speed-variable ping-pong
      EVERY_N_MILLISECONDS(20){
        special_gHue[i]+=8; // slowly cycle the "base color" through the rainbow
        

      
      if (special_ints[i]<starts[i] or special_ints[i]>ends[i]){ //memory-efficient way of dealing with first iteration
          special_ints[i] = starts[i];
      }
      int new_move_speed = 3;
      //Serial.println(min(abs(special_ints[i]-starts[i]),abs(special_ints[i]-ends[i])));
      //Serial.println(round((ends[i]-starts[i]))/6);
      if (min(abs(special_ints[i]-starts[i]),abs(special_ints[i]-ends[i])) < round((ends[i]-starts[i]))/6){
        new_move_speed-=2;
      }
      else if(min(abs(special_ints[i]-starts[i]),abs(special_ints[i]-ends[i])) < round((ends[i]-starts[i]))/3){
        new_move_speed-=1;
      }
      
      if (special_bools[i]) { //moving up in numbers
        leds(starts[i], ends[i]).fadeToBlackBy(120);
        CHSV to_set = CHSV(special_gHue[i], 255, 255);
        
        leds[special_ints[i]] = to_set;
        if (special_move_speed > 1){
            leds[special_ints[i]-1] = to_set;
          }
          if (special_move_speed > 2){
            leds[special_ints[i]-2] = to_set;
          }
        if(special_ints[i]+new_move_speed <= ends[i]) { //still moving up
          special_ints[i]+=new_move_speed;
          special_move_speed = new_move_speed;
        }
        else{ //reached the end
          //special_ints[i] = starts[i];
          special_bools[i] = false;
        }
        
      }
      else { //moving down in numbers
        leds(starts[i], ends[i]).fadeToBlackBy(120);
        CHSV to_set = CHSV(special_gHue[i], 255, 255);

        leds[special_ints[i]] = to_set;
        if (special_move_speed > 1){
            leds[special_ints[i]+1] = to_set;
            
          }
          if (special_move_speed > 2){
            leds[special_ints[i]+2] = to_set;
          }
        if(special_ints[i]-new_move_speed >= starts[i]) { //still moving up
          special_ints[i]-=new_move_speed;
          special_move_speed = new_move_speed;
          
        }
        else{ //reached the end
          //special_ints[i] = ends[i];
          special_bools[i] = true;
        }
      }        
      }
    }
  }
  //ledStrip.write(colors, LED_COUNT);
  FastLED.show();

}
