import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

# Trigger pins for both sensors
trigger_pin1 = 15
trigger_pin2 = 27

# Echo Pins for both sensors
echo_pin1 = 6
echo_pin2 = 23

threshold = 10 # Not the right value...needs to be changed :)
sequence = ""

# Set trigger pins as output
GPIO.setup(trigger_pin1, GPIO.OUT)
GPIO.setup(trigger_pin2, GPIO.OUT)

# Set echo pins as input
GPIO.setup(echo_pin1, GPIO.IN)
GPIO.setup(echo_pin2, GPIO.IN)

# Give sensors time to calibrate
GPIO.output(trigger_pin1, False)
GPIO.output(trigger_pin2, False)
time.sleep(2)

# Function to measure distance
def measureDistance(trigger, echo):

    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

    while GPIO.input(echo) == 1:
        pulse_stop = time.time()

    pulse_duration = pulse_stop - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def noiseReducer(distanceFunction, trigger, echo, filterStrength):
    output = 0
    for i in range(filterStrength):
        output += distanceFunction(trigger, echo)

    output = output/filterStrength
    return output


# Driver Code Starts Here

while True:

    sensorOneData = noiseReducer(measureDistance, trigger_pin1, echo_pin1, filter)
    sensorTwoData = noiseReducer(measureDistance, trigger_pin2, echo_pin2, filter)

    print(sensorOneData)
    print(sensorTwoData)
    time.sleep(0.5)