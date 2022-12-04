import paho.mqtt.client as mqtt 
from random import randrange
import datetime as dt, time
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()

TOPIC = getenv("TOPIC") or ""
mqttBroker = getenv("BROKER") or "localhost"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    publish_message(client)

def on_publish(client, userdata, result):
    print(f"on_publish {userdata}, {result}: publish again")
    publish_message(client)

def publish_message(client) -> None:
    randNumber = randrange(1, 100) 
    message :dict = {"number": randNumber, "epochtime": dt.datetime.now().strftime('%s')}
    client.publish(topic=TOPIC, payload=json.dumps(message), qos=1)
    print(f"published {json.dumps(message)} to topic {TOPIC}")
    time.sleep(randrange(1, 30))


if __name__ == "__main__":
    client = mqtt.Client("publisher")
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(mqttBroker) 

    client.loop_forever()
