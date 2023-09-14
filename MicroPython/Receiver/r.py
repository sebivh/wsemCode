from machine import Pin, Timer

led = Pin(14, Pin.OUT)
LED_state = True
tim = Timer()

def tick(timer):
    global led, LED_state
    LED_state = not LED_state
    led.value(LED_state)
    print("Blink")

print("Hallo")

tim.init(freq=1, mode=Timer.PERIODIC, callback=tick)