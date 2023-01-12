import time
from machine import Pin, ADC

# Sensor Pin Setup
relay = Pin(21, Pin.OUT)
uv = ADC(27)
soil = ADC(26)

RELAY_ON = 0
RELAY_OFF = 1

# Soil Constants
MOIST_SOIL = 500
DRY_SOIL = 200


def check_light():
    # Publish sensor data to MQTT
    # How long to take sensor data to average (1 min?)
    data = []
    bits = 65535
    volt = 3.3

    start_time = time.time_ns()
    interval = 5000  # in ms

    while (time.time_ns() - start_time) < interval:
        val = uv.read_u16()
        sen_volt = val/bits*volt
        data.append(sen_volt)
        time.sleep(1)

    avg_data = round(sum(data)/len(data), 2)

    print('Light level: {avg_data}')
    return avg_data


def check_soil():
    # 1. Publish sensor data to MQTT
    # Read for 5 seconds
    data = []

    start_time = time.time_ns()
    interval = 5000  # in ms

    while (time.time_ns() - start_time) < interval:
        sen_val = soil.read_u16() / 16
        data.append(sen_val)
        time.sleep(1)

    avg_data = round(sum(data)/len(data), 2)
    print(f'Soil: {avg_data}')

    # 2. If sensor data below threshold, water
    if avg_data < DRY_SOIL:
        print('Too Dry! Watering Up!')
        water_start_time = time.time_ns()
        water_for = 5000
        while time.time_ns() - water_start_time <= water_for:
            # Pump Circuit ON
            relay.value(RELAY_ON)
        # Pump Circuit OFF
        relay.value(RELAY_OFF)
        after = soil.read_u16() / 16
        print(f'After Watering: {after}')
        return after

    return avg_data
