from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt

# ======================
# Configuración MQTT
# ======================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_CONTROL = "ujat/iot/led/control"
TOPIC_STATUS = "ujat/iot/led/status"

# Estado global del LED
led_state = {"value": "OFF"}

app = FastAPI()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# ======================
# MQTT
# ======================
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(TOPIC_STATUS)

def on_message(client, userdata, msg):
    global led_state
    payload = msg.payload.decode()
    if payload in ["ON", "OFF"]:
        led_state["value"] = payload
        print("Estado actualizado desde ESP32:", payload)

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

@app.get("/toggle")
def toggle_led():
    global led_state

    new_state = "OFF" if led_state["value"] == "ON" else "ON"
    led_state["value"] = new_state

    mqtt_client.publish(TOPIC_CONTROL, new_state, qos=1)
    return {"state": new_state}

@app.get("/state")
def get_state():
    return {"state": led_state["value"]}

