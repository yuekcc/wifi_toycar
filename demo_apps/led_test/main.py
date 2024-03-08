from machine import Pin
import time

led1 = Pin(12, Pin.OUT)
led2 = Pin(13, Pin.OUT)

while True:
    led1.on()
    time.sleep(0.5)
    led1.off()
    led2.on()
    time.sleep(0.5)
    led2.off()
