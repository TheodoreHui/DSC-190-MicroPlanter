import pycom
import machine
from network import WLAN
pycom.pybytes_on_boot(True)

def wlan_connect(net, password):
    for _ in range(5):
        try:
            print('Connecting to ' + net.ssid)
            wlan.connect(net.ssid, auth=(net.sec, password), timeout=5000)
            while not wlan.isconnected():
                machine.idle()
            print('WLAN connection succeeded!')
            return
        except Exception as e:
            print(e)
            print('Trying again...')

    print('Connecting to ' + net.ssid)
    wlan.connect(net.ssid, auth=(net.sec, password), timeout=5000)
    while not wlan.isconnected():
        machine.idle()
    print('WLAN connection succeeded!')
    return

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)

nets = wlan.scan()
nets_ssid = [net.ssid for net in nets]
for net in nets:
    if net.ssid == 'Theo Hotspot':
        wlan_connect(net, 'pokemongo')
        break

    if net.ssid == 'resnetlajollapalms':
        wlan_connect(net, 'j4m35ch4rl35')
        break

    if net.ssid == 'UCSDIoT':
        wlan_connect(net, 'UCSDiot2022!()')
        break
