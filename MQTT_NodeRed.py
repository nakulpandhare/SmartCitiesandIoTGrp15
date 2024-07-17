import grovepi
import paho.mqtt.client as mqtt
import time
import json
import math

# Connect the DHT22 sensor to digital port D4
sensor_port = 2
# Set up the sensor ports
ultrasonic_ranger_1 = 7  # D7
ultrasonic_ranger_2 = 8  # D8

count = 0
state1 = True
state2 = True
i = 1
temp = 0
humidity = 0

# MQTT settings
broker = "192.168.0.160"
port = 1883
topic = "home/room1/temperature_humidity"
topic1 = "home/room1/warning"

# Initialize MQTT client
client = mqtt.Client()
client.connect(broker, port, 60)
print("Connected to nodered")

def count_people():
    global distance1, distance2, state1, state2, i, count
    
    count = 0
    distance1 = grovepi.ultrasonicRead(ultrasonic_ranger_1)
    print(distance1)
    distance2 = grovepi.ultrasonicRead(ultrasonic_ranger_2)
    print(distance2)
    
    if distance1 > 0 and distance1 < 45 and i == 1 and state1:
        state1 = False
        time.sleep(0.1)
        i += 1

    elif distance2 > 0 and distance2 < 45 and i == 2 and state2:
        print("Entering inside the room")
        state2 = False
        time.sleep(0.1)
        i = 1
        count += 1
        print("No. of people inside room: ", count)
        if not math.isnan(count):
            client.publish(topic, str(count))
            print("Data Sent using MQTT")

    elif distance2 > 0 and distance2 < 45 and i == 1 and state2:
        state2 = False
        time.sleep(0.1)
        i = 2

    elif distance1 > 0 and distance1 < 45 and i == 2 and state1:
        print("Exiting from room")
        state1 = False
        time.sleep(0.1)
        count -= 1
        print("No. of people inside room: ", count)
        i = 1
        if not math.isnan(count):
            client.publish(topic, str(count))
            print("Data Sent using MQTT")

    # Reset states after detection
    state1 = True
    state2 = True

    return count

def temp_humidity_value():
    global temp, humidity
    temp, humidity = grovepi.dht(sensor_port, 0)
    # print("temp, hum")
    # print(temp)
    # print(humidity)
    return temp, humidity

while True:
    try:
        temp_humidity_value()
        
        dist1 = grovepi.ultrasonicRead(ultrasonic_ranger_1)
        dist2 = grovepi.ultrasonicRead(ultrasonic_ranger_2)
        if dist1 < 55 or dist2 < 55:
            count_people()
        
        if count > 5:
            warning_message = "Too manny people inside the room!!!"
            client.publish(topic1, warning_message)

        if not (math.isnan(temp) or math.isnan(humidity) or math.isnan(count)):
            payload = json.dumps({"temperature": temp, "humidity": humidity, "People_Count": count})
            client.publish(topic, payload)
        time.sleep(5)
    except IOError:
        print("Error reading from sensor")
