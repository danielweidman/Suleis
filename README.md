# Suleis
## Intelligent IoT Lighting Controller (no longer maintained)


Suleis lets you control your addressable LED strips from an easy-to-use web interface. It supports lighting both solid and moving (dynamic) lighting patterns, and can show multiple patterns per LED strip. You can even set light alarms to make your lights flash at a certain time or have your lights vary their color based on sunrise and sunset times for your location.


## Quick-start guide (unfinished):
### While it is possible to use the Suleis platform with many different types of addressable LED strips, here is a tutorial to get your lights up and running quicky in our recomended configuration.
In order to build the hardware for Suleis, you will need the following:
- Wemos D1 Mini
-	Arduino Nano v3.0
-	WS2811 RGB LED Strip. This comes in many options for length and LED count.
-	Power supply for RGB LED Strip
-	12V power supply and appropriate jack (current should be determined by the requirements of your choice of light strip)
-	AMS1117-5V power regulator
-	Soldering tools

Optionally, you can use the Suleis printed circuit board to make the soldering process much easier. An Eagle CAD file is included with the design for the circuit board. We have also set up a URL with a company that offers easy PCB services where you can purchase our custom Suleis PCB: https://dirtypcbs.com/store/designer/details/23306/6211/suleis-intelligent-lights-control-system-pcb
For this board, you will specifically need the power supply to have a 2.1mm connector (most common), and the Sparkfun PRT-00119 power jack. 

Steps:
1.	Install the Arduino IDE and the FastLEDs and ArduinoJson libraries, if you haven’t done so already.
2.	Follow the tutorial at the following page to add the ESP8266 library to your Arduino IDE, if you haven’t done so already: https://github.com/esp8266/Arduino
3.	Use the Arduino IDE to upload the code from the “Suleis_Arduino_Component.ino” sketch to the Arduino Nano. You may need to modify the color order and ‘NUM_LEDS’ in the strip setup of the Arduino code (currently ‘BRG’) to reflect that of your strip hardware. Note that ‘NUM_LEDS’ refers to the number of Neopixels (usually the LED count of your strip divided by 3), not the raw number of LEDS.
4.	Use the Arduino IDE to upload the code from the “Suleis_ESP8266_Component.ino” sketch to the Wemos D1 Mini. Before you upload the code, edit the file in the locations marked with comments to add your WiFi network name and password, and strip ID.
5.	Solder together the components based on the following schematic (or just solder the components to the PCB if you have it): https://imgur.com/a/SF6mnXr. Ensure that, for the 12V lines connecting the power supply and the light strip, you use wire of a thick enough gauge for the power requirements of the light strip.
	 
	 

You may either solder the “to_lights_+”, “to_lights_data”, and “to_lights_-“ directly to the red, green, and white wires on the light strip, or you can use a 3-pin JST connector so it can be easily removed.
If all has been done properly, you should be able to plug in the power supply and the lights should turn on white briefly, then change to whatever color/mode you have set up via the Suleis website, or black if you have not set this up yet. 






## Acknowledgements
- FastLEDs library for Arduino
- Randall Degges and Okta for account management and some page layout elements
