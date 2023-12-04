import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

# Trigger pins for both sensors
trigger_pin1 = 15
trigger_pin2 = 27

# Echo Pins for both sensors
echo_pin1 = 6
echo_pin2 = 23

threshold = 50 # Not the right value...needs to be changed :)
window_size = 3

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
    return (distance)            

# Driver Code Starts Here

while True:

    sensorOneDatas = [get_distance(trigger_pin1, echo_pin1) for _ in range(10)]
    sensorTwoDatas = [get_distance(trigger_pin2, echo_pin2) for _ in range(10)]

    sensorOne = median_filter(sensorOneDatas, window_size)[0]
    sensorTwo = median_filter(sensorTwoDatas, window_size)[0]

    print(sensorOne)
    print(sensorTwo)
    time.sleep(0.5)