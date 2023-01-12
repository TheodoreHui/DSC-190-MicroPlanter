# Libraries
import time
import ntptime
import network
from machine import idle, Timer, soft_reset
from umqttsimple import MQTTClient

# Custom files
import mqtt_setup
from sensors import check_light, check_soil

# Time Constants and Variables
LIGHT_INTERVAL = 3600000   # 1 hour
SOIL_INTERVAL = 86400000  # 24 hours
last_soil_check = None
last_temp_check = None

# Wifi Info
ssid = 'INSERT_SSID'
pw = 'INSERT_PW'

# MQTT Info
mqtt_server = 'mqtt.eclipseprojects.io'
port_t = 8000
client_id = 'PicoW'
user_t = 'pico'
password_t = 'picopassword'
topic_pub = 'hello'


def fetch_soil():
    data = check_soil()
    mqtt_client.publish(topic_pub, msg=str(data))


def fetch_light():
    data = check_light()
    mqtt_client.publish(topic_pub, msg=str(data))


def sync_time():
    try:
        ntptime.settime()
        print('Time sync success!')
        return True
    except:
        print('Failed, trying again')
        return False


# Connect to Wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
nets = wlan.scan()

nets_ssid = [net[0].decode("utf-8") for net in nets]
for net in nets_ssid:
    if net == ssid:
        wlan.connect(net, pw)
        while not wlan.isconnected():
            idle()
        print('WLAN connection succeeded to: ' + net)
        break

# Connect MQTT
mqtt_client = mqtt_setup.mqtt_connect(mqtt_server, client_id)

# Keep trying to sync time with NTP server
failed = 0
while not sync_time():
    failed += 1
    if failed > 10:
        soft_reset()


last_soil_fetch = time.time_ns()
fetch_soil()

last_light_fetch = time.time_ns()
fetch_light()

while True:
    curr_time = time.time_ns()
    if curr_time - last_soil_fetch > SOIL_INTERVAL:
        fetch_soil()
        fetch_light()
