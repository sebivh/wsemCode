#  _____                   _                   
# |  __ \                 (_)                  
# | |__) | ___   ___  ___  _ __   __ ___  _ __ 
# |  _  / / _ \ / __|/ _ \| |\ \ / // _ \| '__|
# | | \ \|  __/| (__|  __/| | \ V /|  __/| |   
# |_|  \_\\___| \___|\___||_|  \_/  \___||_|   
#                                              

from machine import Pin, ADC
import time
import network
import _thread
import Webserver
import socket

print("Booting Reciver")

#=============Preamble=================


# Consts
ADC_CONV_FACTOR = 3.3/65535
SENSOR_THRESHOLD = 1
DATA_FILE_PATH = "data.csv"

# Transmit Options
is_reading = False
dtr = 8 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
indicator_led = Pin(14, Pin.OUT, value=0)
onboard_led = Pin("LED", Pin.OUT, value=0)
button = Pin(2, Pin.IN, Pin.PULL_DOWN)
adc_pin = Pin(26, mode=Pin.IN)
adc = ADC(adc_pin)

# Network
SSID = "Receiver"
PASSWORD = "receiverAP"


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


# Function that safes all recived Data as a .csv file 
def saveData(byte_array):
    file = open(DATA_FILE_PATH, 'a')
    
    encoded_msg = byte_array.decode('ascii')
    msg_len = len(byte_array)
    
    # Escape msg
    encoded_msg = encoded_msg.replace('"', '""')
    encoded_msg = encoded_msg.replace('\n', '\\n')
    encoded_msg = encoded_msg.replace('\r', '\\r')
    
    out = '"' + encoded_msg + '",' + str(msg_len)

    # Append Bytes
    for b in byte_array:
        byte = ''
        for i in range(8):
            bit = (b & 1<<(7 - i)) != 0
            byte = byte + str(int(bit))
            
        out = out + ',' + byte
            
            
    file.write(out + '\r\n')
    

# Function that recives the Message and Listens to the End Byte
def reciveMessage(reciver_adc):
    global END_SYMBOLE, dtr, ADC_CONV_FACTOR, SENSOR_THRESHOLD, onboard_led, button
    
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
            # Check for Brake Button
            if button.value() == 1:
                print('\r\nInterupted by Button, returning the until now recived Message')
                return raw_message
                
            
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

    
    return raw_message
    
#
def start_reciving_message():
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
            
            # Save to File
            save_data(recived)
            
            # Decode Message
            msg = decodeRawMessage2String(recived)
            print('Recived Message:\n "{0}"'.format(msg))
            
            is_reading = False
            
            # Add Message to History
            msg_history.append(msg)
        
        time.sleep(1/(4*dtr))

#
def webResponseGenerator(header, path, properties):
    global index_html, dtr, SENSOR_THRESHOLD
    # Settings Page
    if path == '/settings':
          
        setSettings = properties.keys()
              
        if('dtr' in setSettings): # Data Transfer Rate
            value = int(properties['dtr'])
            # Data Transfer Rate must be grater than 0
            if value > 0:
                dtr = value
                print("Set Data Transfer Rate to {0}".format(dtr))
                
        if('threshold' in setSettings): # Threshold
            SENSOR_THRESHOLD = int(properties['threshold'])
            print("Set Threshold to {0}".format(SENSOR_THRESHOLD))
          
        # Read settings.html
        settings_file = open('settings.html')
        response = settings_file.read()
        settings_file.close()
        
        page_data = {
            "dtr":str(dtr),
            "threshold":str(SENSOR_THRESHOLD),
        }
        
        return Webserver.generateResponse(response, page_data)
    
    # csv File
    if path == '/history/csv':
        
        # Reading csv File as Body
        csv_file = open(DATA_FILE_PATH)
        body = csv_file.read()
        csv_file.close()
        
        header = 'HTTP/1.1 200 OK \r\nContent-Length: {0}\n\rContent-Type: text/csv\r\nContent-Disposition: attachment;filename=data.csv\r\n'.format(str(len(body)))
        
        # Empty Line
        response = header + "\r\n" + body
        
        return response
    
    # History
    if path == '/history':
        history_file = open("history.html")
        history_html = history_file.read()
        history_file.close()
        
        # Reading csv File
        csv_file = open(DATA_FILE_PATH)
        data = csv_file.read()
        csv_file.close()
        
        # Generate History
        lines = data.split("\r\n")[2:]
        
        histroy = ""
        
        for l in lines[:5]:
            rows = l.split(",")
            histroy = histroy + '<hr\r\n><p class="entry">{0}</p>'.format(rows[0])
        
        page_data = {
                "history":histroy
            }
        
        return Webserver.generateResponse(history_html, page_data)
        
    # Default
    page_data = {
            "is_reading":str(is_reading),
            "dtr":str(dtr),
        }
    
    index_html_file = open("index.html")
    index_html = index_html_file.read()
    index_html_file.close()
    
    return Webserver.generateResponse(index_html, page_data)

#================Start================

try:
    onboard_led.off()

    # Setup
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)

    # Start Listening to Messages on the Second Thread
    _thread.start_new_thread(start_reciving_message, [])

    # Waiting for AP to be ready
    while ap.active() == False:
      pass
    print ('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig () [0])

    autoSetThreshold()

    # Start Webserver on main Thread
    Webserver.start(webResponseGenerator)

except KeyboardInterrupt:
    ap.active(False)
