import serial.tools.list_ports
import time
import sys
import relayStatus
from Adafruit_IO import Client, MQTTClient, RequestError

AIO_USERNAME = "Nhat_Tien_2002"
AIO_KEY = "aio_XOoI31w6GWEmp8X2jQPXRjVYlaSJ"
AIO_FEED_IDS = "relay_status"

# String : !RELAYxx:ON#, !RELAYxx:OFF#
# xx from 00 to 31, corresponding to channel 1 to 32 of Modbus
client = Client(AIO_USERNAME, AIO_KEY)

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

if getPort() != "None":
    print("Port communication is:" + commPort)
    ser = serial.Serial(port = portName, baudrate = 9600)
    print(ser)

relay_ON = relayStatus.relay_ON
relay_OFF = relayStatus.relay_OFF

def connected(client):
    print("Connecting to AdafruitIO server...")
    client.subscribe(AIO_FEED_IDS)

def disconnected(client):
    print("Disconnect to AdafruitIO server !")
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
            writeStatus(relay_state, relay_index)
        except (ValueError, IndexError) as e:
            print(f"Error parsing payload: {e}")

def writeStatus(status, index):
    if status:
        ser.write(relay_ON[index])
        print(f"CH{index} is ON")
    else:
        ser.write(relay_OFF[index])
        print(f"CH{index} is OFF")

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

try:
    # Connect to AdafruitIO server
    client.connect()
    client.loop_background()
except RequestError as e:
    print(f"Error connecting to Adafruit IO: {e}")

while True:
    time.sleep(10)