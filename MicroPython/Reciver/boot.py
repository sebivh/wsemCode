#  ____              _                   
# |  _ \  ___   ___ (_)__   __ ___  _ __ 
# | |_) |/ _ \ / __|| |\ \ / // _ \| '__|
# |  _ <|  __/| (__ | | \ V /|  __/| |   
# |_| \_\\___| \___||_|  \_/  \___||_|   
#                                        

from machine import Pin, ADC, Timer
import time

print("Booting Reciver")

#=============Preamble=================

msg_history = []

# Consts
ADC_CONV_FACTOR = 3.3/65535
SENSOR_THRESHOLD = 1

# Transmit Options
dtr = 1 # Data Transfer Rate in bit/s
END_SYMBOLE = int('00000100', 2) # 00000100

# Pins
indicator_led = Pin(14, Pin.OUT)
onboard_led = Pin("LED", Pin.OUT)
adc_pin = Pin(26, mode=Pin.IN)
#adc_pin = Pin(28, mode=Pin.IN)
adc = ADC(adc_pin)

# Timer
main = Timer()

#=============Functions=================

# Funktion to set the Thershold acording to the Enviorment, Overwritable by the overwrite value
def autoSetThreshold(overwrite=-1):
    global SENSOR_THRESHOLD, adc, indicator_led
    
    if(overwrite >= 0):
        SENSOR_THRESHOLD = overwrite
        
    else:
        reading_max = 0
        reading_resolution = 120
        
        print("Start reading threshold")
        
        
        # Messure Enviorment many times and find the highest reading
        for i in range(reading_resolution):
            indicator_led.on()
            
            reading = adc.read_u16()
            
            print("{0}:\t{1}V".format(i, round(reading * ADC_CONV_FACTOR, 3)))
            
            if(reading > reading_max):
                reading_max = reading
            
            indicator_led.off()
            time.sleep(0.5)
        
        print("Reading Stoped. Max reading of {0}V.".format(reading_max * ADC_CONV_FACTOR))
        
        # Sets Sensor to 110% of the max
        SENSOR_THRESHOLD = 1.1 * reading_max * ADC_CONV_FACTOR
    
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



# Funktion that watches for the first high bit of a new Message
def watchMessageInit(timer):
    global adc, SENSOR_THRESHOLD, indicator_led, dtr, time
    reading = adc.read_u16() * ADC_CONV_FACTOR
    
    #Set LED to Value
    indicator_led.value(reading >= SENSOR_THRESHOLD)
    
    if reading >= SENSOR_THRESHOLD:
        
        #==================Init Pin Recived=============
        print("Threshold of {0}V overcome with {1}V. Start reading".format(SENSOR_THRESHOLD, reading))
        # Waiting for init Bit
        time.sleep(1/dtr)
        
        recived = reciveMessage(adc)
        
        # Decode Message
        msg = decodeRawMessage2String(recived)
        
        print('Recived Message:\n "{0}"'.format(msg))
        
        # Add Message to History
        msg_history.aappend(msg)
    


#================Start================

# Setup
autoSetThreshold(0.35)

# Start
main.init(mode=Timer.PERIODIC, period=int(dtr/2 * 1000), callback=watchMessageInit)

while True:
    time.sleep(1)