from fastapi import FastAPI
import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
TOPIC_CMD = "iot/ujat/led/cmd"
TOPIC_STATE = "iot/ujat/led/state"

estado_led = {"led": False}

app = FastAPI()

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_STATE)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if payload == "ON":
        estado_led["led"] = True
    elif payload == "OFF":
        estado_led["led"] = False

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

@app.get("/")
def root():
    return {"status": "Backend IoT activo"}

@app.get("/estado")
def obtener_estado():
    return estado_led

@app.post("/led/on")
def led_on():
    mqtt_client.publish(TOPIC_CMD, "ON", qos=1)
    return {"ok": True}

@app.post("/led/off")
def led_off():
    mqtt_client.publish(TOPIC_CMD, "OFF", qos=1)
    return {"ok": True}
