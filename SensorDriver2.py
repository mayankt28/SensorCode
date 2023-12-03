from hcsr04sensor import sensor
from statistics import median
import RPi.GPIO as GPIO
import time
import logging

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

# Configure logging
logging.basicConfig(filename='sensor_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    while True:
        sensorOneDatas = [value1.distance(value1.raw_distance()) for _ in range(10)]
        sensorTwoDatas = [value2.distance(value2.raw_distance()) for _ in range(10)]

        sensorOne = median_filter(sensorOneDatas, window_size)
        sensorTwo = median_filter(sensorTwoDatas, window_size)

        if sensorOne[0] < threshold:
            current = "S1"
            if last is not None and last != current:
                print("Entry")
                logging.info("Entry - Sensor 1")
            else:
                last = current

        if sensorTwo[0] < threshold:
            current = "S2"
            if last is not None and last != current:
                print("Exit")
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
