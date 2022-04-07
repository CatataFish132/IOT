import network, esp, gc, BME280, ujson, time, ntptime, urequests, utime
import socket
from time import sleep
from machine import Pin, I2C, ADC, Timer, RTC
import machine
import ubinascii
import micropython

esp.osdebug(None)
gc.collect()

# read config file
with open("settings.json", "r") as f:
  config = ujson.loads(f.read())

# setup i2c
i2c = I2C(0)

# get client id
client_id = ubinascii.hexlify(machine.unique_id())

# connect to the wlan
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(config["ssid"], config["password"])


while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
