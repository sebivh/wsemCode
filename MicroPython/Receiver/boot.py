#  ____              _                   
# |  _ \  ___   ___ (_)__   __ ___  _ __ 
# | |_) |/ _ \ / __|| |\ \ / // _ \| '__|
# |  _ <|  __/| (__ | | \ V /|  __/| |   
# |_| \_\\___| \___||_|  \_/  \___||_|   
#                                        

from machine import Pin, ADC
import time
import network
import socket
import _thread

print("Booting Reciver")

#=============Preamble=================

msg_history = []

# Consts
ADC_CONV_FACTOR = 3.3/65535
SENSOR_THRESHOLD = 1

# Transmit Options
is_reading = False
dtr = 8 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
indicator_led = Pin(14, Pin.OUT, value=0)
onboard_led = Pin("LED", Pin.OUT, value=0)
adc_pin = Pin(26, mode=Pin.IN)
adc = ADC(adc_pin)

# Network
SSID = "Receiver"
PASSWORD = "receiverAP"
index_html_file = open("index.html")
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

#=============Functions=================

# Funktion to set the Thershold acording to the Enviorment, Overwritable by the overwrite value
def autoSetThreshold(overwrite=-1):
    global SENSOR_THRESHOLD, adc, indicator_led
    
    if(overwrite >= 0):
        SENSOR_THRESHOLD = overwrite
        
    else:
        reading_max = 0
        reading_resolution = 100
        
        print("Start reading threshold")
        
        
        # Messure Enviorment many times and find the highest reading
        for i in range(reading_resolution):
            indicator_led.on()
            
            reading = adc.read_u16()
            
            print("{0}:\t{1}V".format(i, round(reading * ADC_CONV_FACTOR, 3)))
            
            if(reading > reading_max):
                reading_max = reading
            
            indicator_led.off()
            time.sleep(1/dtr)
        
        print("Reading Stoped. Max reading of {0}V.".format(reading_max * ADC_CONV_FACTOR))
        
        # Sets Sensor to 110% of the max
        SENSOR_THRESHOLD = 1.5 * reading_max * ADC_CONV_FACTOR
    
    print("Set Threshold to {0}V".format(SENSOR_THRESHOLD))



# Function that recives the Message and Listens to the End Byte
def reciveMessage(reciver_adc):
    global END_SYMBOLE, dtr, ADC_CONV_FACTOR, SENSOR_THRESHOLD, onboard_led
    
    print("Recording Message")
    onboard_led.on()
    
    raw_message = bytearray()
    recived_byte = 0
    
    print("")
    
    # Only executes if the last Byte was not the End Symbole
    while recived_byte != END_SYMBOLE:
        
        # Resetting recived Byte
        recived_byte = 0
        
        # Start reading Byte
        for i in range(8):        
            volt_read = reciver_adc.read_u16() * ADC_CONV_FACTOR
            bit =  volt_read >= SENSOR_THRESHOLD
            
            #Set current Position of byte to read bit, starting with highest
            recived_byte += bit << (7 - i)
            print(int(bit), end='')
            
            # Wait for the next Bit acording to the Data Transfer Rate
            time.sleep(1/dtr)
        
        # End Reading Byte, pushing it to Byte Array
        raw_message.append(recived_byte)
        print("\nByte: '{1}' ({0})".format(recived_byte, chr(recived_byte)))
        
        print('\n')
    
    print("Finished Reading Message")
    onboard_led.off()
    
    # Slice the end Symbole of the Message
    raw_message = raw_message[:-1]
    
    # Save to File
    
    return raw_message
    
    
# Decodes Message to a String using Ascii
def decodeRawMessage2String(raw_message):
    return raw_message.decode('ascii')

# Formats Properties into a Key-Value Mapping
def getProperties(request):
    raw = request.split('?', 1)
    
    # Check if there are Properties if not retrun empty String
    if(len(raw) < 2):
        return {}
    
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
def generateResponse(body, page_data):
    
    # Replace all Data Points with Device Data
    for data_name in page_data:
        body = body.replace("{"+data_name+"}", page_data[data_name])
    
    # Generate Response Header (protocol_version Space status_code Space status_text)
    header = '{0} {1} {2}\r\nContent-Length: {3}\r\n'.format('HTTP/1.1', str(200), 'OK', str(len(body)))
    
    response = header + '\r\n' + body
    
    return response

# Start WebServer and Serve Connections
def startWebServer():
    global dtr
    
    #try:
    
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
          
          # Settings Page
          if path is '/settings':
              # Format Properties
              properties = getProperties(header['Request_target'])
              
              setSettings = properties.keys()
                  
              if('dtr' in setSettings): # Data Transfer Rate
                  value = int(properties['dtr'])
                  # Data Transfer Rate must be grater than 0
                  if value > 0:
                      dtr = value
                      print("Set Data Transfer Rate to {0}".format(dtr))
              
              # Read settings.html
              settings_file = open('settings.html')
              response = settings_file.read()
              settings_file.close()
              
              # Return Connection
              conn.send(response)
              conn.close()
              
              # Skip Default and Wait for next Connection
              continue
          
          # Default
          
          page_data = {
                  "is_reading":str(is_reading),
                  "dtr":str(dtr),
              }
          
          conn.send(generateResponse(index_html, page_data))
          conn.close()
        
    # In any case, espacily Keyboard Interupts, close the Socket
    #finally:
     #   s.close()

#================Start================

onboard_led.off()

# Setup
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Load neccesery HTML
index_html = index_html_file.read()

# Start Web Server
_thread.start_new_thread(startWebServer, ())

# Waiting for AP to be ready
while ap.active() == False:
  pass
print ('AP Mode Is Active, You can Now Connect')
print('IP Address To Connect to:: ' + ap.ifconfig () [0])

autoSetThreshold(0.5)

while True:
    reading = adc.read_u16() * ADC_CONV_FACTOR
    
    #Set LED to Value
    indicator_led.value(reading >= SENSOR_THRESHOLD)
    
    if reading >= SENSOR_THRESHOLD:
        #==================Init Pin Recived=============
        print("Threshold of {0}V overcome with {1}V. Start reading".format(SENSOR_THRESHOLD, reading))
        is_reading = True
        # Waiting for init Bit
        time.sleep(1/dtr)
        
        recived = reciveMessage(adc)
        
        # Decode Message
        msg = decodeRawMessage2String(recived)
        print('Recived Message:\n "{0}"'.format(msg))
        
        is_reading = False
        
        # Add Message to History
        msg_history.append(msg)
    
    time.sleep(1/(4*dtr))