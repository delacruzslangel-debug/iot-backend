from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt
import asyncio

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
clientes_ws = set()
event_loop = None   # 🔥 IMPORTANTE

app = FastAPI()

# ======================
# Static
# ======================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ======================
# WebSocket
# ======================
<script>
const ws = new WebSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") +
  location.host +
  "/ws"
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  actualizar(data.state);
};

ws.onerror = () => {
  document.getElementById("estado").innerText = "Error de conexión";
};

function toggle() {
  fetch("/toggle");
}
</script>

# ======================
# MQTT callbacks
# ======================
def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(TOPIC_STATUS)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if payload in ["ON", "OFF"]:
        estado_led["value"] = payload
        print("Estado desde ESP32:", payload)

        # 🔥 Enviar a WebSockets desde el event loop
        if event_loop:
            for ws in list(clientes_ws):
                asyncio.run_coroutine_threadsafe(
                    ws.send_json({"state": payload}),
                    event_loop
                )

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

@app.on_event("startup")
async def startup_event():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

# ======================
# Startup
# ======================
@app.on_event("startup")
async def startup_event():
    global event_loop
    event_loop = asyncio.get_running_loop()

# ======================
# HTTP endpoints
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

@app.get("/state")
def get_state():
    return {"state": estado_led["value"]}
