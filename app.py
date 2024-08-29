from counterfit_connection import CounterFitConnection
from counterfit_shims_seeed_python_dht import DHT
import paho.mqtt.client as mqtt
import time

# Initialize CounterFit connection
CounterFitConnection.init('127.0.0.1', 5000)

# Initialize the DHT sensor ("11" refers to DHT11 sensor, 5 refers to GPIO pin number)
sensor = DHT("11", 5)

ACCESS_TOKEN = 'xMguBXSmPtfbbSimZg5Y'  # Token of your device
broker = "192.168.80.121"         # Host name demo.thingsboard.io
port = 1883                            # Data listening port

# Define connection and publish status flags
is_connected = False

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        print("Connected to ThingsBoard successfully!")
        is_connected = True
    else:
        print(f"Failed to connect, return code {rc}")
        is_connected = False

def on_disconnect(client, userdata, rc):
    global is_connected
    print(f"Disconnected from ThingsBoard with result code {rc}")
    is_connected = False

def on_publish(client, userdata, mid):
    print("Data published successfully")

# Create the MQTT client and set access token
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.enable_logger()  # Enable detailed logging

# Connect to the ThingsBoard broker
try:
    client.connect(broker, port, 60)
    client.loop_start()  # Start loop to handle network traffic and callbacks
except Exception as e:
    print(f"Failed to connect to the broker: {e}")

while True:
    try:
        # Read both temperature and humidity
        humidity, temp = sensor.read()
        print(f'Temperature: {temp}°C, Humidity: {humidity}%')

        # Create payload with both temperature and humidity
        payload = '{{"temperature": {}, "humidity": {}}}'.format(temp, humidity)

        # Check connection status before publishing
        if is_connected:
            result = client.publish('v1/devices/me/telemetry', payload)
            if result.rc != 0:
                print(f"Failed to publish, result code: {result.rc}")
        else:
            print("Client is not connected. Retrying...")

        time.sleep(10)  # Wait 10 seconds before next reading
    except KeyboardInterrupt:
        print("Exiting the loop.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")

# Stop the MQTT loop and disconnect
client.loop_stop()
client.disconnect()
