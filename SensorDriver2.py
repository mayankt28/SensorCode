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

# Set trigger pins as output
GPIO.setup(trigger_pin1, GPIO.OUT)
GPIO.setup(trigger_pin2, GPIO.OUT)

# Set echo pins as input
GPIO.setup(echo_pin1, GPIO.IN)
GPIO.setup(echo_pin2, GPIO.IN)

window_size = 3
threshold = 80

sequence = ""


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

def get_distance (trig, echo):

    if GPIO.input (echo):                                               # If the 'Echo' pin is already high
        return (100)                                                    # then exit with 100 (sensor fault)

    distance = 0                                                        # Set initial distance to zero

    GPIO.output (trig,False)                                            # Ensure the 'Trig' pin is low for at
    time.sleep (0.05)                                                   # least 50mS (recommended re-sample time)

    GPIO.output (trig,True)                                             # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0                                                  # No need to use the 'time' module here,
    dummy_variable = 0                                                  # a couple of 'dummy' statements will do fine
    
    GPIO.output (trig,False)                                            # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()                             # Set inital time values to current time
    
    while not GPIO.input (echo):                                        # Wait for the start of the 'Echo' pulse
        time1 = time.time()                                             # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:                                        # If the 'Echo' pin doesn't go high after 20mS
            distance = 100                                              # then set 'distance' to 100
            break                                                       # and break out of the loop
        
    if distance == 100:                                                 # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
    
    while GPIO.input (echo):                                            # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()                                             # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:                                        # If the 'Echo' pin doesn't go low after 20mS
            distance = 100                                              # then ignore it and set 'distance' to 100
            break                                                       # and break out of the loop
        
    if distance == 100:                                                 # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
        
                                                                        # Sound travels at approximately 2.95uS per mm
                                                                        # and the reflected sound has travelled twice
                                                                        # the distance we need to measure (sound out,
                                                                        # bounced off object, sound returned)
                                                                        
    distance = (time2 - time1) / 0.00000295 / 2 / 10                    # Convert the timer values into centimetres
    return (distance)                                                   # Exit with the distance in centimetres
    


value1 = get_distance(trigger_pin1, echo_pin1)
value2 = get_distance(trigger_pin2, echo_pin2)

# Driver Code Starts Here
try:
    mqtt_publish_worker_thread = threading.Thread(target=mqtt_publish_worker)
    mqtt_publish_worker_thread.start()

    while True:
        sensorOneDatas = [get_distance(trigger_pin1, echo_pin1) for _ in range(5)]
        sensorTwoDatas = [get_distance(trigger_pin2, echo_pin2) for _ in range(5)]

        sensorOne = median_filter(sensorOneDatas, window_size)[0]
        sensorTwo = median_filter(sensorTwoDatas, window_size)[0]

        if sensorOne < threshold:
            if len(sequence) == 0 or (len(sequence) >= 1 and sequence[-1] != '1'):
                print("Sensor 1 Triggered: ", sensorOne)
                sequence += '1'
                print("Seq: ", sequence)

        if sensorTwo < threshold:
            if len(sequence) == 0 or (len(sequence) >=1 and sequence[-1] != '2'):
                print("Sensor 2 Triggered: ", sensorTwo)
                sequence += '2'
                print("Seq: ", sequence)

        if len(sequence) == 2:

            if sequence == "12":
                print("Entry Detected")
                message = "ID2023-ENTRY"
                publish_to_mqtt(message)
                logging.info("Entry")
                sequence = ""

            elif sequence == "21":
                print("Exit Detected")
                message = "ID2023-EXIT"
                publish_to_mqtt(message)
                logging.info("Exit")
                sequence = ""

            else:
                print("Invalid Sequence: ", sequence)
                logging.info("Invalid Sequence")
                sequence = ""

        elif len(sequence) > 2:
            sequence = ""


            


except KeyboardInterrupt:
    print("Stopping...")

except Exception as e:
    logging.exception("An error occurred: %s", str(e))

finally:
    GPIO.cleanup()
    client.disconnect()
    #mqtt_publish_worker_thread.join()
