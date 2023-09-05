from machine import Pin, ADC, Timer
import time

print("Booting Reciver")

#=============Preamble=================

# Consts
ADC_CONV_FACTOR = 3.3/65535
SENSOR_THRESHOLD = 2

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
    

# Funktion that watches for the first high bit of a new Message
def watchMessageInit(timer):
    global adc, SENSOR_THRESHOLD, indicator_led
    reading = adc.read_u16() * ADC_CONV_FACTOR
    
    #Set LED to Value
    indicator_led.value(reading >= SENSOR_THRESHOLD)
    
    if reading >= SENSOR_THRESHOLD:
        #==================Init Pin Recived=============
        print("Threshold of {0}V overcome with {1}V".format(SENSOR_THRESHOLD, reading))


#================Start================

# Setup
autoSetThreshold()

# Start
onboard_led.on()
main.init(mode=Timer.PERIODIC, period=500, callback=watchMessageInit)

while True:
    time.sleep(1)