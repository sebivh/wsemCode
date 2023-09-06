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
dtr = 10 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
onboard_led = Pin("LED", Pin.OUT)
laser = Pin(14, Pin.OUT)

# Network
SSID = 'Emitter'
urlEscapeCodes = {
        "%20":" ",
        "%3C":"<",
        "%3E":">",
        "%23":"#",
        "%25":"%",
        "%2B":"+",
        "%7B":"{",
        "%7D":"}",
        "%7C":"|",
        "%5C":"\\",
        "%5E":"^",
        "%7E":"~",
        "%5B":"[",
        "%5D":"]",
        "%60":"'",
        "%3B":";",
        "%2F":"/",
        "%3F":"?",
        "%3A":":",
        "%40":"@",
        "%3D":"=",
        "%26":"&",
        "%24":"$",
        "%0A":"\n",
        "%0D":"\r",
    }

#==============Functions==============

# Formats Properties into a Key-Value Mapping
def getProperties(request):
    raw = request.split('?', 1)
    
    # Check if there are Properties if not retrun empty String
    if(len(raw) < 2):
        return ''
    
    raw = raw[1].split(' ', 1)[0]
    
    raw_list = raw.split('&')
    
    properties = {}
    
    # Go through every Property still formatted "key=value"
    for e in raw_list:
        split = e.split("=", 1)
        
        # Unescape the Values
        value = decodeUrlEscapeCodes(split[1])
        
        properties[split[0]] = value
        
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

# Function that decodes the Header and puts all header-fields in a Dictionary
def decodeHeader(recived):
    recived = recived.decode('utf-8')
    # Splits the Header into its individaul Fields
    raw_fields = recived.split('\r\n')
    # Dictonary that contains all Values of the avalibile Http header
    fields = {}
    # Add Method (GET or POST) to the fields with the Key of 'method' and remove it form the Array
    fields['Method'] = raw_fields.pop(0)
    
    # Decode every Heder into Field Key and Value
    for f in raw_fields:
        # If the String is empty it was just a line feed without Header field
        if(f is '' or f is ' '):
            continue
        
        f = f.split(': ')
        fields[f[0]] = f[1]
    
    return fields

# Function that gets the requested Path from an Url stripping Propertues and the host address in the process
def getRequestedPath(url):
    # Only the Path
    path = url.split('/')[3]
    # Remove Properties
    path = path.split('?')[0]
    
    return path
    

# Function that decodes the escape Sequences used in URL
def decodeUrlEscapeCodes(string):
    global urlEscapeCodes
    # Replace all Plus with white Space
    string = string.replace('+', ' ')
    
    # iterate over String
    i = 0
    while i < len(string):
        # Detected a escape Code
        if(string[i] is '%'):
            # Gets the Code as a Substring from the input String
            code = string[i : i+3]
            print(code)
            # Replaces all Codes in case there are more
            string = string.replace(code, urlEscapeCodes[code])
            # Adjusts i further by one so the just replaced char dosnt have to be scaned
            i += 1
            
        i += 1
        
    # Retruns the unescaped String
    return string    
    

# Function that generates a Response Page for the User showing Data
def generateResponsePage(data, dtr):
    global response_html
    # Replace Placeholder with duration of transmission
    response_html = response_html.replace('{0}', str(len(data) * 8 / dtr) + ' Sekunden')
    # Replace Placeholder with Data
    response_html = response_html.replace('{1}', data)
    # Replace Placeholder with Data Transfer Rate
    response_html = response_html.replace('{2}', str(dtr) + ' bits/s')
    return response_html

#================Start================

laser.off()
onboard_led.off()

# Setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password="emitterAP")
ap.active(True)

# Reading index.html
print("Reading 'index.html'...")
form_html_file = open('index.html')
form_html = form_html_file.read()
form_html_file.close()
print("Finished reading")

# Reading response.html
print("Reading 'response.html'...")
response_html_file = open('response.html')
response_html = response_html_file.read()
response_html_file.close()
print("Finished reading")

print("\n")

# Waiting for AP to be ready
while ap.active() == False:
  pass
print ('AP Mode Is Active, You can Now Connect')
print('IP Address To Connect to:: ' + ap.ifconfig () [0])

# Starting Web Service
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print("Starting Webserver\n")
while True:
  print("Listening for connection on Port 80...")
  # Wait for a Connection
  conn, addr = s.accept()
  print('Got a connection from {0}'.format(str(addr)))
  request = conn.recv(1024)
  
  # Decode Header
  header = decodeHeader(request)
  
  print(header['Method'])
  
  # Gets the requested File Path if there is one
  if('Referer' in header.keys()):
      relPath = getRequestedPath(header['Referer'])
  else:
      relPath = ''
  
  if relPath is 'response':
      # Format Properties
      properties = getProperties(header['Referer'])

      # If there are no properties there is no response Page to be displayed and no data needs to be send
      if(len(properties) == 0):
          conn.close()
          # Continue waiting for next Conections
          continue
      
      print("Got properties: {0}".format(properties))

      # Send HTML with Answer
      responsePage = generateResponsePage(properties['data'], dtr)
      
      conn.send(responsePage)
      conn.close()
      
      # Convert to byte Array
      msg_bytes = bytearray(properties['data'], 'ascii')

      # Append End Symbol
      msg_bytes.append(END_SYMBOLE)
              
      # Send Message via Laser
      send(msg_bytes)
      
      continue
            
  # Default, just return index.html
  conn.send(form_html)
  conn.close()
  
  
# TODO
# Umbauen das nicht auf das Referer Feld geguckt wird sonder auf den Path aus der Method
# Dann da die Proberties raus
# Irgendwie diese favicon anfragen abblocken ODER favicon senden