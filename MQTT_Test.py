import paho.mqtt.client as mqtt
import time

# HiveMQ Test Server details
broker_address = "broker.hivemq.com"
port = 1883
topic = "your/topic"  # Replace with your desired topic

# Callback when the client connects to the broker
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

# Publish a sample message
message = "Hello, HiveMQ!"
client.publish(topic, message)

# Wait for a while to ensure the message is published
time.sleep(2)

# Disconnect from the broker
client.disconnect()
