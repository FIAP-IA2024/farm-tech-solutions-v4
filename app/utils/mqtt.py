import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime
from database import save_sensor_data

BROKER = "test.mosquitto.org"
TOPIC = "home/events"
CONNECTED = False
PORT = 1883


def generate_fake_data():
    return {
        "ltr_UMIDADE": round(random.uniform(28.9, 55.2), 2),
        "ltr_TEMPERATURA": round(random.uniform(7, 38.3), 2),
        "ltr_PH": round(random.uniform(6.3, 7.3), 2),
        "ltr_NUTRIENTE_P": random.choice([0, 1]),
        "ltr_NUTRIENTE_K": random.choice([0, 1]),
        "ltr_STATUS_IRRIGACAO": random.choice([0, 1]),
        "ltr_DATA": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }


def on_connect(client, userdata, flags, rc):
    global CONNECTED
    if rc == 0:
        CONNECTED = True
        print(f"Connected to MQTT Broker: {BROKER}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        humidity = payload["ltr_UMIDADE"]
        temperature = payload["ltr_TEMPERATURA"]
        ph = payload["ltr_PH"]
        nutrient_p = payload["ltr_NUTRIENTE_P"]
        nutrient_k = payload["ltr_NUTRIENTE_K"]
        irrigation_status = payload["ltr_STATUS_IRRIGACAO"]

        save_sensor_data(
            humidity, temperature, ph, nutrient_p, nutrient_k, irrigation_status
        )
        print(f"Data received and saved: {payload}")

    except KeyError as e:
        print(f"Missing field in payload: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    global CONNECTED

    # Initialize the MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    client.loop_start()

    try:
        while not CONNECTED:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            fake_data = generate_fake_data()
            client.publish(TOPIC, json.dumps(fake_data))
            print(f"Published fake data: {fake_data}")
            time.sleep(10)

    except KeyboardInterrupt:
        print("Disconnected!")
        client.loop_stop()


if __name__ == "__main__":
    main()
