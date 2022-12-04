import datetime as dt
from dotenv import load_dotenv
import json
from os import getenv
import paho.mqtt.client as mqtt
from db import get_averages, insert_message, delete_old_messages, setup_db 
from stats_pubsub import publish_stats

load_dotenv()

TOPIC = getenv("TOPIC") or "DATA"
STATS_TOPIC = getenv("STATS_TOPIC") or "STATS"

mqttBroker = getenv("BROKER") or "localhost"

def on_connect(client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
		client.subscribe(topic=TOPIC, qos=1)

def on_message(client, userdata, message) -> None:
		mssg: str = str(message.payload.decode("utf-8"))
		print(f'received message: {mssg}, values {get_values_from_message(mssg)}')
		delete_old_messages(int(dt.datetime.now().strftime('%s')), 35)
		insert_message(get_values_from_message(mssg))
		stats :list = list(get_averages())
		avg_1min, avg_5min, avg_15min = stats[0]
		publish_stats(client, STATS_TOPIC, (float(avg_1min), float(avg_5min), float(avg_15min)))

def get_values_from_message(message: str) -> tuple[int, int]:
		"""extract number and epochtime from message"""
		values: dict = json.loads(message)
		return (values["number"], values["epochtime"]) 

if __name__ == "__main__":
		setup_db()
		client = mqtt.Client("subscriber")
		client.on_connect = on_connect
		client.on_message = on_message

		client.connect(mqttBroker) 

		client.loop_forever()
