from network import Bluetooth

from umqttsimple import MQTTClient_lib

import time
import ubinascii
import math
import machine
import pycom
from pycoproc_2 import Pycoproc

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

bt = Bluetooth()
try:
    bt.start_scan(-1)
except OSError:
    pass




def twoscmp(value):
    if value > 128:
        value = value - 256
    return value

def byte_to_info(uuid):
    gas_res_d = 0
    name = uuid[0:3]
    name_text = ''.join(chr(t) for t in name)
    if name_text == "PyN":
        sensor_id = uuid[7]
        mac = ubinascii.hexlify(uuid[10:16])
        press = ubinascii.hexlify(uuid[8:10])
        press_d = int(press, 16)
        gas_res = ubinascii.hexlify(uuid[3:7])
        gas_res_d = int(gas_res, 16)
        print("{} {} BLE_MAC: {}, Pressure: {} hPa, Gas resistance: {} ohm".format(name_text, sensor_id, mac, press_d, gas_res_d), end=", ")
    return (name_text,gas_res_d)

def air_quality_score(hum, gas_res):
    gas_reference = 250000
    hum_reference = 40
    gas_lower_limit = 5000
    gas_upper_limit = 50000
    if (hum >= 38 and hum <= 42):
        hum_score = 0.25*100
    else:
        if (hum < 38):
            hum_score = 0.25/hum_reference*hum*100
        else:
            hum_score = ((-0.25/(100-hum_reference)*hum)+0.416666)*100
    if (gas_reference > gas_upper_limit):
        gas_reference = gas_upper_limit
    if (gas_reference < gas_lower_limit):
        gas_reference = gas_lower_limit
    gas_score = (0.75/(gas_upper_limit-gas_lower_limit)*gas_reference -(gas_lower_limit*(0.75/(gas_upper_limit-gas_lower_limit))))*100
    air_quality_score = hum_score + gas_score

    return air_quality_score

def poll_PyN():
    advs = bt.get_advertisements()
    if advs:
        for adv in advs:
            read_adv = bt.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)
            name = bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL)
            if read_adv:
                manuf = ubinascii.hexlify(read_adv)
                manuf_data = ubinascii.hexlify(read_adv[0:4])
                if (manuf_data == b'4c000215') :#or (manuf_data == b'd2000215')):# company id=d2 is Dialog, b'4c000215' is Apple's id and it implies ibeacon
                    uuid_raw = read_adv[4:20]
                    uuid = ubinascii.hexlify(uuid_raw)
                    name, air=byte_to_info(uuid_raw)
                    if name == "PyN":
                        print("rssi:",adv.rssi)
                        major = ubinascii.hexlify(read_adv[20:22])
                        minor = ubinascii.hexlify(read_adv[22:24])
                        tx_power = ubinascii.hexlify(read_adv[24:25])
                        tx_power_real = twoscmp(int(tx_power, 16))
                        major_int = int(major, 16)
                        major_f = major_int/100 # bme688
                        minor_int = int(minor,16)
                        minor_f = minor_int/100 # bme688, it is divided by 10 initially in the dialog's firmware.
                        return major_f, minor_f, air
    return -1,-1,-1

def poll_pysense():
    mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
    #print("MPL3115A2 temperature: " + str(mp.temperature()))
    #print("Altitude: " + str(mp.altitude()))
    mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    #print("Pressure: " + str(mpp.pressure()))

    #pysense air quality
    si = SI7006A20(py)

    #pysense light sensor
    lt = LTR329ALS01(py)

    #pysense movement
    li = LIS2HH12(py)
    return mp, mpp, si, lt, li



def sub_cb(topic, msg):
   msg = msg.decode("utf-8")
   print(msg)
   split = msg.split(':')
   head = split[0]
   data = float(split[1].strip())
   if (head == 'Soil Moisture'):
       pybytes.send_signal(7, data)
   if (head == 'UV Light'):
       pybytes.send_signal(8, data)

def mqtt_connect():
    mqtt_server = 'mqtt.eclipseprojects.io'
    client_id = 'Pysense'

    client = MQTTClient_lib(client_id, mqtt_server, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

#reconnect & reset
def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    mqtt_connect()




pybytes.connect()

pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

py = Pycoproc()
if py.read_product_id() != Pycoproc.USB_PID_PYSENSE:
    raise Exception('Not a Pysense')

pybytes_enabled = False
if 'pybytes' in globals():
    if(pybytes.isconnected()):
        print('Pybytes is connected, sending signals to Pybytes')
        pybytes_enabled = True

try:
    client = mqtt_connect()
    client.set_callback(sub_cb)
except OSError as e:
    machine.reset()
topic_pub = 'microplanter'
client.subscribe(topic_pub)
print('subscribed')

while True:
    try:
        #polling pynode
        major_f, minor_f, air = -1,-1,-1
        while (major_f == -1):
            major_f, minor_f, air = poll_PyN()
            time.sleep(.05)

        #polling pysense
        mp, mpp, si, lt, li = poll_pysense()

        #polling pico
        try:
            client.subscribe(topic_pub)
            print('subscribed')
        except OSError as e:
            machine.reset()
        #sending to pybytes


        if(pybytes_enabled):
            pybytes.send_signal(1, mpp.pressure()/100)
            pybytes.send_signal(2, si.temperature())
            pybytes.send_signal(3, lt.lux())
            pybytes.send_signal(4, air_quality_score(minor_f, air))
            pybytes.send_signal(5, major_f)
            pybytes.send_signal(6, minor_f)
            print("Sent data to pybytes")
            #print(major_f, minor_f)
        time.sleep(2.5)
    except OSError as e:
        machine.reset()
