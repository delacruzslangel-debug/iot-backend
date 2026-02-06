from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt
import asyncio

# ======================
# CONFIG MQTT
# ======================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_CONTROL = "ujat/iot/led/control"
TOPIC_STATUS = "ujat/iot/led/status"

# ======================
# ESTADO GLOBAL
# ======================
estado_led = {"value": "OFF"}
clientes_ws = set()

app = FastAPI()

# ======================
# ARCHIVOS ESTÁTICOS
# ======================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ======================
# WEBSOCKET
# ======================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clientes_ws.add(ws)

    # Estado inicial
    await ws.send_json({"state": estado_led["value"]})

    try:
        while True:
            await ws.receive_text()   # 🔥 MANTIENE VIVO EL WS
    except WebSocketDisconnect:
        clientes_ws.remove(ws)

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

        for ws in list(clientes_ws):
            try:
                asyncio.create_task(ws.send_json({"state": payload}))
            except:
                pass

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

@app.on_event("startup")
def startup_event():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

# ======================
# ENDPOINTS HTTP
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
    nuevo = "OFF" if estado_led["value"] == "ON" else "ON"
    estado_led["value"] = nuevo
    mqtt_client.publish(TOPIC_CONTROL, nuevo, qos=1)
    return {"state": nuevo}
