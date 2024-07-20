import serial.tools.list_ports
import time
import relayStatus
import sys
from Adafruit_IO import Client, MQTTClient, RequestError

ADAFRUIT_IO_USERNAME = "tuannguyen2208nat"
ADAFRUIT_IO_KEY = "aio_Tpqz630LWJqmQ5r5g4Kjzeg4BHHh"
FEED_KEY = "status"
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)

relay_ON = relayStatus.relay_ON
relay_OFF = relayStatus.relay_OFF

def setDevice(state, i):
    if state:
        ser.write(relay_ON[i])
        print(f"CH{i} ON")
    else:
        ser.write(relay_OFF[i])
        print(f"CH{i} OFF")

def connected(client):
    print('Connected to Adafruit IO! Listening for changes...')
    client.subscribe(FEED_KEY)

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print(f'Received data: {payload}')
    if payload.startswith("!RELAY"):
        try:
            parts = payload[6:].split(":")
            relay_index = int(parts[0])
            command = parts[1]
            if command == "ON#":
                relay_state = True
            elif command == "OFF#":
                relay_state = False
            else:
                raise ValueError("Invalid command")
            setDevice(relay_state, relay_index)
        except (ValueError, IndexError) as e:
            print(f"Error parsing payload: {e}")

# Set up the MQTT client
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

try:
    # Connect to Adafruit IO
    client.connect()
    client.loop_background()
except RequestError as e:
    print(f"Error connecting to Adafruit IO: {e}")

# Keep the script running
while True:
    time.sleep(10)