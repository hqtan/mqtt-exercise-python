from dotenv import load_dotenv
import json
from os import getenv
import paho.mqtt.client as mqtt
from tabulate import tabulate

load_dotenv()

STATS_TOPIC = getenv("STATS_TOPIC") or "STATS"

mqttBroker = getenv("BROKER") or "localhost"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic=STATS_TOPIC, qos=1)

def on_message(client, userdata, message) -> None:
    mssg: str = str(message.payload.decode("utf-8"))
    # print(f'received message: {mssg}')
    display_stats(json.loads(mssg))

def publish_stats(client, topic, stats: tuple[float, float, float]) -> None:
    avg_1min, avg_5min, avg_30min = stats
    message: dict = {"avg_1min": avg_1min, "avg_5min": avg_5min, "avg_30min": avg_30min}
    client.publish(topic=topic, payload=json.dumps(message), qos=1)
    print(f"published stats {json.dumps(message)} to topic {STATS_TOPIC}")

def display_stats(stats: dict) -> None:
    table = [stats.keys(), stats.values()]
    print(tabulate(table, headers="firstrow"))
    # print(f"1 min average: {avg_1min}, 5 min average: {avg_5min}, 30 min average: {avg_30min}")

if __name__ == "__main__":
    client = mqtt.Client("stats_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqttBroker) 

    client.loop_forever()
