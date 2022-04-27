import network
import BME280
import json
from machine import SoftI2C, Pin, I2C, RTC
import machine
import ubinascii
from umqttsimple import MQTTClient
import time
import urequests

# init bme280
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
bme = BME280.BME280(i2c=i2c)

# read json file
with open("settings.json") as json_file:
    data = json.load(json_file)
ssid = data["ssid"]
password = data["password"]
topic_pub = data["topic"]
topic_sub = data["topic"]
last_message = time.time()
message_interval = 1

# setup i2c esp32
# i2c = SoftI2C(0)

# connect esp32 to wifi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)
while not sta_if.isconnected():
    pass
print('network config:', sta_if.ifconfig())


def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')

def connect_and_subscribe():
    client_id = ubinascii.hexlify(machine.unique_id())
    mqtt_server, topic_sub = (data["mqtt_server"], data["topic"])
    client = MQTTClient(client_id, mqtt_server, user="luni", password="12345")
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

# Get datetime from site
url = "https://worldtimeapi.org/api/timezone/Europe/Amsterdam"

response = urequests.get(url)

if response.status_code == 200:
  parsed = response.json()
  datetime_str = str(parsed["datetime"])
  year = int(datetime_str[0:4])
  month = int(datetime_str[5:7])
  day = int(datetime_str[8:10])
  hour = int(datetime_str[11:13])
  minute = int(datetime_str[14:16])
  second = int(datetime_str[17:19])
  subsecond = int(round(int(datetime_str[20:26]) / 10000))
  rtc = RTC()
        
  # update internal RTC
  rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        # read bme280
        temperature = float(str(bme.temperature).strip("C"))
        humidity = float(str(bme.humidity).strip("%"))
        pressure = float(str(bme.pressure).strip("hPa"))
        json_string = f'{{"temperature": {temperature}, "humidity": {humidity}, "pressure": {pressure}, "timestamp": "{str(time.localtime())}"}}'
        print(json_string)
        client.publish(topic_pub, json_string)
        time.sleep(1)
    except OSError as e:
        print(e)
        restart_and_reconnect()
