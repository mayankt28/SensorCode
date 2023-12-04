from hcsr04sensor import sensor
from statistics import median
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import logging
import queue
import threading

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

GPIO.setmode(GPIO.BCM)

# Trigger pins for both sensors
trigger_pin1 = 15
trigger_pin2 = 27

# Echo Pins for both sensors
echo_pin1 = 6
echo_pin2 = 23

window_size = 3
threshold = 50
last = None
current = None

message_queue = queue.Queue()
queue_lock = threading.Lock()

# Configure logging
logging.basicConfig(filename='sensor_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def publish_to_mqtt(message):
    with queue_lock:
        message_queue.put(message)

# Worker function to publish messages from the queue
def mqtt_publish_worker():
    topic = "/ASPSensorData"
    while True:
        with queue_lock:
            if not message_queue.empty():
                message = message_queue.get()
                client.publish(topic, message)
                print("Published:", message)
        time.sleep(2)  

def median_filter(data, window_size):
    filtered_data = []
    half_window = window_size // 2

    for i in range(len(data)):
        window = data[max(0, i - half_window): min(len(data), i + half_window + 1)]
        filtered_data.append(median(window))

    return filtered_data

value1 = sensor.Measurement(trigger_pin1, echo_pin1, temperature=68, unit="imperial")
value2 = sensor.Measurement(trigger_pin2, echo_pin2, temperature=68, unit="imperial")

# Driver Code Starts Here
try:
    mqtt_publish_worker_thread = threading.Thread(target=mqtt_publish_worker)
    mqtt_publish_worker_thread.start()

    while True:
        sensorOneDatas = [value1.distance(value1.raw_distance()) for _ in range(10)]
        sensorTwoDatas = [value2.distance(value2.raw_distance()) for _ in range(10)]

        sensorOne = median_filter(sensorOneDatas, window_size)
        sensorTwo = median_filter(sensorTwoDatas, window_size)

        if sensorOne < threshold:
            current = "S1"
            if last is not None and last != current:
                print("Entry")
                message = "ID2023-ENTRY"
                publish_to_mqtt(message)
                logging.info("Entry - Sensor 1")
            else:
                last = current

        if sensorTwo < threshold:
            current = "S2"
            if last is not None and last != current:
                print("Exit")
                message = "ID2023-EXIT"
                publish_to_mqtt(message)
                logging.info("Exit - Sensor 2")
            else:
                last = current

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopping...")

except Exception as e:
    logging.exception("An error occurred: %s", str(e))

finally:
    GPIO.cleanup()
    client.disconnect()
    mqtt_publish_worker_thread.join()
