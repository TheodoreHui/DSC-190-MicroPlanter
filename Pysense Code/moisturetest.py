import machine
from machine import Pin
from machine import ADC
import time
from time import sleep


moisture = ADC(2)

while True:
    moisture_value = moisture.read_u16()
    print(moisture_value/16) #16: air, ~500 moist soil, ~2000 submerged in water
    sleep(1)
