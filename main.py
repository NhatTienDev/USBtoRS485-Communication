import serial.tools.list_ports
import time
import sys
import relayStatus
from Adafruit_IO import Client, MQTTClient, RequestError

AIO_USERNAME = "Nhat_Tien_2002"
AIO_KEY = "aio_XOoI31w6GWEmp8X2jQPXRjVYlaSJ"
AIO_FEED_IDS = "relay_status"

# String : !RELAYxx:ON#, !RELAYxx:OFF#
# xx (channel_index) from 00 to 31, corresponding to channel 1 to 32 of Modbus

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    global commPort
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

if getPort() != "None":
    print("Communication port is: " + commPort)
    ser = serial.Serial(port = getPort(), baudrate = 9600)
    print(ser)

relay_ON = relayStatus.relay_ON
relay_OFF = relayStatus.relay_OFF

def writeStatus(status, index):
    if status:
        ser.write(relay_ON[index])
        print(f"Channel_{index + 1} is ON")
    else:
        ser.write(relay_OFF[index])
        print(f"Channel_{index + 1} is OFF")

def connected(client):
    print("Waiting for receiving data from user")
    client.subscribe(AIO_FEED_IDS)

def disconnected(client):
    print("Disconnect to AdafruitIO server !")
    sys.exit(1)

def message(client, feed_id, payload):
    print(f'Received data: {payload}')
    if payload.startswith("!RELAY"):
        try:
            global relay_state
            parts = payload[6:].split(":")
            relay_index = int(parts[0])
            
            if relay_index < 0 or relay_index > 31:
                raise ValueError("Please input the correct relay index from 00 to 31")
            
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

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

try:
    # Connect to AdafruitIO server
    client.connect()
    client.loop_background()
except RequestError as e:
    print(f"Error connection to AdafruitIO server: {e}")

while True:
    time.sleep(5)