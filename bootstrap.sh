#!/bin/bash

# Wait for WiFi connection
while ! /sbin/iwconfig wlan0 | grep -q "ESSID:Para2675"; do
    sleep 5
done

# WiFi connected, execute the Python script
python3 ./Documents/TestDriver/SensorDriver2.py
