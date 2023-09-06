#  _____             _  _    _              
# | ____| _ __ ___  (_)| |_ | |_  ___  _ __ 
# |  _|  | '_ ` _ \ | || __|| __|/ _ \| '__|
# | |___ | | | | | || || |_ | |_|  __/| |   
# |_____||_| |_| |_||_| \__| \__|\___||_|   
#

from machine import Pin, Timer
import time
import network
import socket

print("Booting Emitter")

#=============Preamble=================

# Transmit Options
dtr = 2 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
onboard_led = Pin("LED", Pin.OUT)
laser = Pin(14, Pin.OUT)

# Network
SSID = 'Emitter'

#==============Functions==============
    

# Formats Properties into a Key-Value Mapping
def getProperties(request):
    raw = request.split('?', 1)
    
    # Check if there are Properties if not retrun empty String
    if(len(raw) < 2):
        return ''
    
    raw = raw[1].split(' ', 1)[0]
    
    # Format back to original String
    raw = raw.replace('+', ' ')
    
    raw_list = raw.split('&')
    
    properties = {}
    
    # Go through every Property still formatted "key=value"
    for e in raw_list:
        split = e.split("=", 1)
        properties[split[0]] = split[1]
        
    return properties
 
 
# Function that sends an Byte over the Laser Module
def send(recived_bytes):
    global laser, time, onboard_led
    print("Start sending Message over Laser. Aproximate Duration: {0}s".format(len(recived_bytes) * 8 /dtr))
    onboard_led.on()
    
    # Send activation bit to start reading on the Reciver
    laser.on()
    time.sleep(1/dtr)
    
    print("\n")
    # Cycle through bytes
    for byte in recived_bytes:
        print("Byte: '{1}' ({0})".format(byte, chr(byte)))
        
        filter = int('00000001', 2)
        
        # Cycle through byte
        for i in range(8):
            
            # Sees if bit i is set, returns true if set
            bit = byte & filter<<i != 0
            
            print("{0}".format(int(bit)), end='')
            
            # Sed Laser
            laser.value(bit)
            
            # 
            time.sleep(1/dtr)
        
        print('\n')

    print("\nFinished sending the Message.")
    onboard_led.off()


# Function that generates a Response Page for the User showing Data
def generateResponsePage(data, dtr):
    
    return ''

#================Start================

laser.off()
onboard_led.off()

# Setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password="emitterAP")
ap.active(True)

print("Reading index.html")
html_file = open('index.html')
html = html_file.read()
html_file.close()
print("Finished reading")

# Start

# Waiting for AP to be ready
while ap.active() == False:
  pass
print ('AP Mode Is Active, You can Now Connect')
print('IP Address To Connect to:: ' + ap.ifconfig () [0])

# Starting Web Service
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


print("Starting Webserver")

while True:
  print("Listening for connection on Port 80...")
  # Wait for a Connection
  conn, addr = s.accept()
  print('Got a connection from {0}'.format(str(addr)))
  request = conn.recv(1024)
  # Format Properties
  properties = getProperties(request.decode('ascii'))
  
  # Checks if Properties were send
  if(properties == ""):
      # Return HTML and close Connection
      conn.send(html)
      conn.close()
      # Continue waiting for next Conections
      continue
  
  print("Got properties: {0}".format(properties))
  
  # Send HTML with Answer
  responsePage = generateResponsePage(properties['data'], dtr)
  
  conn.send(html)
  conn.close()
  
  # Convert to byte Array
  msg_bytes = bytearray(properties['data'], 'ascii')
  
  # Append End Symbol
  msg_bytes.append(END_SYMBOLE)
  
  # Send Message via Laser
  send(msg_bytes)