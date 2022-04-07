import network
import BME280
import json
from machine import SoftI2C, Pin, I2C
import machine
import ubinascii
from umqttsimple import MQTTClient

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

# while True:
#     # read bme280
#     temperature = bme.temperature
#     humidity = bme.humidity
#     pressure = bme.pressure
#     print('Temperature is: ', temperature)
#     print('Humidity is: ', humidity)
#     print('Pressure is: ', pressure)

#     json = "{\"temperature\": " + str(temperature) + ", \"humidity\": " + str(humidity) + ", \"pressure\": " + str(pressure) + "}"

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

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

counter = 0
while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1
    except OSError as e:
        restart_and_reconnect()

# # # connect to mqtt broker
# # client = MQTTClient('<client_id>', '<broker_ip>')
# # client.connect()

# # # a function that publishes a message to the broker
# # def publish_message(topic, message):
# #     client.publish(topic, message)

# # def subscribe_topic(topic):
# #     client.subscribe(topic)

# while True:
#     temperature = read_temperature_bme()
#     print(temperature)
#     # publish_message('<topic>', str(temperature))
#     # client.wait_msg()
#     time.sleep(1)

