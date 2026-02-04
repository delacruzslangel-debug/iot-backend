from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt
import asyncio

app = FastAPI()

# =====================
# Estado global
# =====================
estado_led = {"value": "OFF"}
clientes_ws = set()

# =====================
# MQTT
# =====================
MQTT_BROKER = "broker.hivemq.com"
TOPIC_CMD = "ujat/iot/led/cmd"
TOPIC_STATE = "ujat/iot/led/state"

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(TOPIC_STATE)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if payload in ["ON", "OFF"]:
        estado_led["value"] = payload
        asyncio.run(notificar_websockets(payload))

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

# =====================
# WebSocket
# =====================
async def notificar_websockets(estado):
    for ws in clientes_ws:
        await ws.send_json({"state": estado})

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clientes_ws.add(ws)
    await ws.send_json({"state": estado_led["value"]})
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clientes_ws.remove(ws)

# =====================
# API
# =====================
@app.get("/")
def root():
    return {"status": "Backend IoT activo"}

@app.get("/toggle")
async def toggle():
    nuevo = "OFF" if estado_led["value"] == "ON" else "ON"
    estado_led["value"] = nuevo
    mqtt_client.publish(TOPIC_CMD, nuevo, qos=1)
    await notificar_websockets(nuevo)
    return {"state": nuevo}

# =====================
# Web
# =====================
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/web", response_class=HTMLResponse)
def web():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()
