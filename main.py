from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt

# ======================
# MQTT
# ======================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_CONTROL = "ujat/iot/led/control"
TOPIC_STATUS = "ujat/iot/led/status"

# ======================
# Estado global
# ======================
estado_led = {"value": "OFF"}

app = FastAPI()

# ======================
# Archivos estáticos
# ======================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ======================
# MQTT
# ======================
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(TOPIC_STATUS)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if payload in ["ON", "OFF"]:
        estado_led["value"] = payload
        print("Estado desde ESP32:", payload)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# ======================
# Endpoints
# ======================
@app.get("/")
def root():
    return {"status": "Backend IoT activo"}

@app.get("/web", response_class=HTMLResponse)
def web():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/state")
def get_state():
    return {"state": estado_led["value"]}

@app.get("/toggle")
def toggle_led():
    nuevo = "OFF" if estado_led["value"] == "ON" else "ON"
    estado_led["value"] = nuevo
    mqtt_client.publish(TOPIC_CONTROL, nuevo, qos=1)
    return {"state": nuevo}
