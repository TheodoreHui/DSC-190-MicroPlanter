from umqttsimple import MQTTClient
from network import WLAN
import machine
import time

def sub_cb(topic, msg):
   msg = msg.decode("utf-8")
   split = msg.split(':')
   head = split[0]
   data = float(split[1].strip())
   if (head == 'Soil Moisture'):
       print('sending ' + head + ": " + str(data) + " to channel 7")
   if (head == 'UV Light'):
       print('sending ' + head + ": " + str(data) + " to channel 8")

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)

nets = wlan.scan()
for net in nets:
    if net.ssid == 'Theo Hotspot':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'pokemongo'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

mqtt_server = 'mqtt.eclipseprojects.io'
port_t = 8000
client_id = 'Pysense'
user_t = 'pico'
password_t = 'picopassword'
topic_pub = 'hello'


last_message = 0
message_interval = 5
counter = 0

#MQTT connect
def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

#reconnect & reset
def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(10)
    mqtt_connect()

client = mqtt_connect()
client.set_callback(sub_cb)
while True:
    try:
        client.subscribe(topic_pub)
        print('subscribed')
        #client.set_callback(callback)
    except OSError as e:
        reconnect()
    time.sleep(1)

client.disconnect()
