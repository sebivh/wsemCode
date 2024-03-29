from machine import Pin, ADC
import time

ADC_CONV_FACTOR = 3.3/65536
adc = ADC(0)

while True:
    print(round(adc.read_u16() * ADC_CONV_FACTOR - 0.03, 3))
    time.sleep(1/64)