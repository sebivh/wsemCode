#  _____             _  _    _              
# | ____| _ __ ___  (_)| |_ | |_  ___  _ __ 
# |  _|  | '_ ` _ \ | || __|| __|/ _ \| '__|
# | |___ | | | | | || || |_ | |_|  __/| |   
# |_____||_| |_| |_||_| \__| \__|\___||_|   
#

from machine import Pin, Timer
import time
import network
import Webserver
import _thread

print("Booting Emitter")

#=============Preamble=================

# Transmit Options
dtr = 8 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100
is_emitting = False
adjust_mode = False
time_remaining = 0
transmitting_text = ""

# Pins
onboard_led = Pin("LED", Pin.OUT)
indicator_led = Pin(13, Pin.OUT)
laser = Pin(14, Pin.OUT)

# Network
SSID = 'Emitter'

#==============Functions==============
 
# Function that sends an Byte over the Laser Module
def send(recived_bytes):
    global laser, time, onboard_led, indicator_led, is_emitting, send_thread, time_remaining
    is_emitting = True
    print("Start sending Message over Laser. Aproximate Duration: {0}s".format(len(recived_bytes) * 8 /dtr))
    #onboard_led.on() // Cant Turn on the Onboard LED on becouse the Web Server would crash
    
    print("\n")
    # Cycle through bytes
    for byte in recived_bytes:
        
        # Send first Byte to indicate new Package containing one byte
        print("New Packadge:\t1")
        laser.value(1)
        indicator_led.value(1)
        time.sleep(1/dtr)
        
        print("Byte: '{1}' ({0})".format(byte, chr(byte)))
        
        # Cycle through byte, start by highest
        for i in range(8):
            
            # Sees if bit i is set, returns true if set
            bit = (byte & 1<<(7 - i)) != 0
            
            print("{0}".format(int(bit)), end='')
            
            # Sed Laser
            laser.value(bit)
            indicator_led.value(bit)
            
            #
            time_remaining = time_remaining - 1/dtr
            time.sleep(1/dtr)
            
        # Pull low to ensure Package bit is send
        laser.off()
        indicator_led.off()
        time.sleep(1/dtr)
        
        print('\n')

    is_emitting = False
    print("\nFinished sending the Message.")
    #onboard_led.off()
    return
    
def webResponseGenerator(header, path, properties):
    global dtr, is_emitting, send_thread, adjust_mode, time_remaining, transmitting_text
    
    # Response Page
    if path is '/response':
      
      if is_emitting:
          # Redirekt to Status Page
          print("Allready Transmitting, Redirektion to Status Page")
          return 'HTTP/1.1 303 Allready Transmitting\r\nLocation: /status\r\n\r\n'
      
      # If there is no Data to be Send there is no response Site to display, ignoring Request
      if('data' not in properties.keys()):
          print("No Data! Ignoring Request!")
          return ''
          
      print('Got following Data: "{0}"'.format(properties['data']))
      
      transmitting_text = properties['data']
      
      # Convert to byte Array
      msg_bytes = bytearray(properties['data'], 'ascii')

      # Append End Symbol
      msg_bytes.append(END_SYMBOLE)
              
      # Send Message via Laser
      _thread.start_new_thread(send, [msg_bytes])
      
      # Send HTML with Answer
      
      time_remaining = len(properties['data']) * 8 / dtr
      
      page_data = {
          "dtr":str(dtr),
          "time":str(time_remaining) + ' Sekunden',
          "text":properties['data'],
          }
      
      response_html_file = open("response.html")
      response_html = response_html_file.read()
      response_html_file.close()
      
      response = Webserver.generateResponse(response_html, page_data)
      
      return response

    # Settings Page
    if path is '/settings':
      
      setSettings = properties.keys()
      
      # Set all Settings
      if('adjust_mode' in setSettings): # Ajustier Modus
          state = properties['adjust_mode'] is 'on'
          adjust_mode = state
          laser.value(state)
          indicator_led.value(state)
          print("Setting Adjust Mode to {0}".format(state))
          
      if('dtr' in setSettings and properties['dtr'] != ''): # Data Transfer Rate
          
          value = float(properties['dtr'])
          # Data Transfer Rate must be grater than 0
          if value > 0:
              dtr = value
              print("Set Data Transfer Rate to {0}".format(dtr))
      
      # Read settings.html
      settings_file = open('settings.html')
      response = settings_file.read()
      settings_file.close()
      
      page_data = {
          "dtr":str(dtr),
          }
      
      # Return Connection
      return Webserver.generateResponse(response, page_data)
  
    # Status Page
    if path is '/status':
      page_data = {
          "is_emitting":str(is_emitting),
          "dtr":str(dtr),
          "text": transmitting_text,
          "time_remaining": str(time_remaining) + ' seconds',
          }
      
      status_file = open("status.html")
      status_html = status_file.read()
      status_file.close()
      
      return Webserver.generateResponse(status_html, page_data)
  
    # Default
    index_file = open("index.html")
    index_html = index_file.read()
    index_file.close()

    return Webserver.generateResponse(index_html)
    

#================Start================

laser.off()
onboard_led.off()

# Setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password="emitterAP")
ap.active(True)

print("\n")

# Waiting for AP to be ready
while ap.active() == False:
  pass
print ('AP Mode Is Active, You can Now Connect')
print('IP Address To Connect to:: ' + ap.ifconfig () [0])

Webserver.start(webResponseGenerator)
