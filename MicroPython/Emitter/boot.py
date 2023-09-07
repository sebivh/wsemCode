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
dtr = 1 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
onboard_led = Pin("LED", Pin.OUT)
indicator_led = Pin(13, Pin.OUT)
laser = Pin(14, Pin.OUT)

# Network
SSID = 'Emitter'
urlEscapeCodes = {
        "%E2%82%AC":"€",
        "%E2%80%9A":"‚",
        "%E2%80%9E":"„",
        "%E2%80%A6":"…",
        "%E2%80%A0":"†",
        "%E2%80%A1":"‡",
        "%E2%80%B0":"‰",
        "%E2%80%B9":"‹",
        "%E2%80%98":"‘",
        "%E2%80%99":"’",
        "%E2%80%9C":"“",
        "%E2%80%9D":"”",
        "%E2%80%A2":"•",
        "%E2%80%93":"–",
        "%E2%80%94":"—",
        "%C6%92":"ƒ",
        "%CB%86":"ˆ",
        "%C5%A0":"Š",
        "%C5%92":"Œ",
        "%C5%8D":"",
        "%C5%BD":"Ž",
        "%C2%90":"",
        "%CB%9C":"˜",
        "%E2%84":"™",
        "%C5%A1":"š",
        "%E2%80":"›",
        "%C5%93":"œ",
        "%C5%BE":"ž",
        "%C5%B8":"Ÿ",
        "%C2%A0":"\"",
        "%C2%A1":"¡",
        "%C2%A2":"¢",
        "%C2%A3":"£",
        "%C2%A4":"¤",
        "%C2%A5":"¥",
        "%C2%A6":"¦",
        "%C2%A7":"§",
        "%C2%A8":"¨",
        "%C2%A9":"©",
        "%C2%AA":"ª",
        "%C2%AB":"«",
        "%C2%AC":"¬",
        "%C2%AD":"­",
        "%C2%AE":"®",
        "%C2%AF":"¯",
        "%C2%B0":"°",
        "%C2%B1":"±",
        "%C2%B2":"²",
        "%C2%B3":"³",
        "%C2%B4":"´",
        "%C2%B5":"µ",
        "%C2%B6":"¶",
        "%C2%B7":"·",
        "%C2%B8":"¸",
        "%C2%B9":"¹",
        "%C2%BA":"º",
        "%C2%BB":"»",
        "%C2%BC":"¼",
        "%C2%BD":"½",
        "%C2%BE":"¾",
        "%C2%BF":"¿",
        "%C3%80":"À",
        "%C3%81":"Á",
        "%C3%82":"Â",
        "%C3%83":"Ã",
        "%C3%84":"Ä",
        "%C3%85":"Å",
        "%C3%86":"Æ",
        "%C3%87":"Ç",
        "%C3%88":"È",
        "%C3%89":"É",
        "%C3%8A":"Ê",
        "%C3%8B":"Ë",
        "%C3%8C":"Ì",
        "%C3%8D":"Í",
        "%C3%8E":"Î",
        "%C3%8F":"Ï",
        "%C3%90":"Ð",
        "%C3%91":"Ñ",
        "%C3%92":"Ò",
        "%C3%93":"Ó",
        "%C3%94":"Ô",
        "%C3%95":"Õ",
        "%C3%96":"Ö",
        "%C3%97":"×",
        "%C3%98":"Ø",
        "%C3%99":"Ù",
        "%C3%9A":"Ú",
        "%C3%9B":"Û",
        "%C3%9C":"Ü",
        "%C3%9D":"Ý",
        "%C3%9E":"Þ",
        "%C3%9F":"ß",
        "%C3%A0":"à",
        "%C3%A1":"á",
        "%C3%A2":"â",
        "%C3%A3":"ã",
        "%C3%A4":"ä",
        "%C3%A5":"å",
        "%C3%A6":"æ",
        "%C3%A7":"ç",
        "%C3%A8":"è",
        "%C3%A9":"é",
        "%C3%AA":"ê",
        "%C3%AB":"ë",
        "%C3%AC":"ì",
        "%C3%AD":"í",
        "%C3%AE":"î",
        "%C3%AF":"ï",
        "%C3%B0":"ð",
        "%C3%B1":"ñ",
        "%C3%B2":"ò",
        "%C3%B3":"ó",
        "%C3%B4":"ô",
        "%C3%B5":"õ",
        "%C3%B6":"ö",
        "%C3%B7":"÷",
        "%C3%B8":"ø",
        "%C3%B9":"ù",
        "%C3%BA":"ú",
        "%C3%BB":"û",
        "%C3%BC":"ü",
        "%C3%BD":"ý",
        "%C3%BE":"þ",
        "%C3%BF":"ÿ",
        "%20":" ",
        "%21":"!",
        "%22":"\"",
        "%23":"#",
        "%24":"$",
        "%25":"%",
        "%26":"&",
        "%27":"'",
        "%28":"(",
        "%29":")",
        "%2A":"*",
        "%2B":"+",
        "%2C":",",
        "%2D":"-",
        "%2E":".",
        "%2F":"/",
        "%30":"0",
        "%31":"1",
        "%32":"2",
        "%33":"3",
        "%34":"4",
        "%35":"5",
        "%36":"6",
        "%37":"7",
        "%38":"8",
        "%39":"9",
        "%3A":":",
        "%3B":";",
        "%3C":"<",
        "%3D":"=",
        "%3E":">",
        "%3F":"?",
        "%40":"@",
        "%41":"A",
        "%42":"B",
        "%43":"C",
        "%44":"D",
        "%45":"E",
        "%46":"F",
        "%47":"G",
        "%48":"H",
        "%49":"I",
        "%4A":"J",
        "%4B":"K",
        "%4C":"L",
        "%4D":"M",
        "%4E":"N",
        "%4F":"O",
        "%50":"P",
        "%51":"Q",
        "%52":"R",
        "%53":"S",
        "%54":"T",
        "%55":"U",
        "%56":"V",
        "%57":"W",
        "%58":"X",
        "%59":"Y",
        "%5A":"Z",
        "%5B":"[",
        "%5C":"\\",
        "%5D":"]",
        "%5E":"^",
        "%5F":"_",
        "%60":"`",
        "%61":"a",
        "%62":"b",
        "%63":"c",
        "%64":"d",
        "%65":"e",
        "%66":"f",
        "%67":"g",
        "%68":"h",
        "%69":"i",
        "%6A":"j",
        "%6B":"k",
        "%6C":"l",
        "%6D":"m",
        "%6E":"n",
        "%6F":"o",
        "%70":"p",
        "%71":"q",
        "%72":"r",
        "%73":"s",
        "%74":"t",
        "%75":"u",
        "%76":"v",
        "%77":"w",
        "%78":"x",
        "%79":"y",
        "%7A":"z",
        "%7B":"{",
        "%7C":"|",
        "%7D":"}",
        "%7E":"~",
        "%7F":"\"",
        "%81":"",
        "%8F":"",
        "%9D":"",
        "%0D":"\r",
        "%09":"\t",
        "%0A":"\n",
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
    global laser, time, onboard_led, indicator_led
    print("Start sending Message over Laser. Aproximate Duration: {0}s".format(len(recived_bytes) * 8 /dtr))
    onboard_led.on()
    
    # Send activation bit to start reading on the Reciver
    laser.on()
    time.sleep(1/dtr)
    
    print("\n")
    # Cycle through bytes
    for byte in recived_bytes:
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
            time.sleep(1/dtr)
        
        print('\n')

    print("\nFinished sending the Message.")
    onboard_led.off()

# Function that decodes the Header and puts all header-fields in a Dictionary
def decodeHeader(recived):
    recived = recived.decode('utf-8')
    
    # Split into header and Content
    recived = recived.split('\r\n\r\n')
    header = recived[0]
    content = recived[1]
    
    # Splits the Header into its individaul Fields
    raw_fields = header.split('\r\n')
    # Dictonary that contains all Values of the avalibile Http header
    fields = {}
    # Set Content
    fields['Content'] = content
    # Decode Start Line (HTTP_method Space Request_target Space HTTP_version)
    start_line = raw_fields.pop(0).split(' ')
    fields['HTTP_method'] = start_line[0]
    fields['Request_target'] = start_line[1]
    fields['HTTP_version'] = start_line[2]
    
    # Decode every Heder into Field Key and Value
    for f in raw_fields:
        # If the String is empty it was just a line feed without Header field, this marks the begining of the Content
        if(f is ''):
            
            break
        
        f = f.split(': ')
        fields[f[0]] = f[1]
    
    return fields

# Function that gets the requested Path from an Url stripping Propertues and the host address in the process
def getRequestedPath(url):
    # Remove Properties
    path = url.split('?')[0]
    
    return path
    

# Function that decodes the escape Sequences used in URL
def decodeUrlEscapeCodes(string):
    global urlEscapeCodes
    # Replace all Plus with white Space
    string = string.replace('+', ' ')
    
    # iterate over String
    keys = urlEscapeCodes.keys()
    for c in keys:
        string = string.replace(c, urlEscapeCodes[c])
        
    # Retruns the unescaped String
    return string
    

# Function that generates a Response Page for the User showing Data
def generateResponse(data, dtr):
    global response_html
    # Replace Placeholder with duration of transmission
    response_html = response_html.replace('{0}', str(len(data) * 8 / dtr) + ' Sekunden')
    # Replace Placeholder with Data
    response_html = response_html.replace('{1}', data)
    # Replace Placeholder with Data Transfer Rate
    response_html = response_html.replace('{2}', str(dtr) + ' bits/s')
    body = response_html
    
    # Generate Response Header (protocol_version Space status_code Space status_text)
    header = '{0} {1} {2}\r\nContent-Length: {3}\r\n'.format('HTTP/1.1', str(200), 'OK', str(len(body)))
    
    response = header + '\r\n' + body
    
    return response

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
while True :
  print("Listening for connection on Port 80...")
  # Wait for a Connection
  conn, addr = s.accept()
  request = conn.recv(1024)
  
  # Decode Headers of request
  header = decodeHeader(request)
  
  # Get the Requested Path
  path = getRequestedPath(header['Request_target'])
  
  print('Got a connection from {0} requesting "{1}"'.format(addr[0], path))
  
  #=======Page Checks=========
  
  # Response Page
  if path is '/response':
      # Format Properties
      properties = getProperties(header['Request_target'])
      
      # If there is no Data to be Send there is no response Site to display, ignoring Request
      if('data' not in properties.keys()):
          print("No Data! Ignoring Request!")
          conn.close()
          # Continue waiting for next Connection
          
      print('Got following Data: "{0}"'.format(properties['data']))

      # Send HTML with Answer
      response = generateResponse(properties['data'], dtr)
      
      # Handle Connection
      conn.send(response)
      conn.close()
      
      # Convert to byte Array
      msg_bytes = bytearray(properties['data'], 'ascii')

      # Append End Symbol
      msg_bytes.append(END_SYMBOLE)
              
      # Send Message via Laser
      send(msg_bytes)
      
      # Skip Default and Wait for next Connection
      continue
            
  # Default
  conn.send(form_html)
  conn.close()
  
  
# TODO
# Umbauen das nicht auf das Referer Feld geguckt wird sonder auf den Path aus der Method
# Dann da die Proberties raus
# Irgendwie diese favicon anfragen abblocken ODER favicon senden