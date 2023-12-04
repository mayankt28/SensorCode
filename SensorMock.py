import paho.mqtt.client as mqtt
import time

# HiveMQ Test Server details
broker_address = "broker.hivemq.com"
port = 1883
topic = "/ASPSensorData"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
    else:
        print("Failed to connect, return code %d\n", rc)

# Callback when a message is published
def on_publish(client, userdata, mid):
    print("Message Published")

# Create an MQTT client instance
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the broker
client.connect(broker_address, port, 60)

# Wait for the connection to establish
client.loop_start()

try:

    while True:
        message = "ID2023-ENTRY"
        client.publish(topic, message)
        time.sleep(4)

except KeyboardInterrupt:
    print("Exiting...: ")

finally:
    client.disconnect()