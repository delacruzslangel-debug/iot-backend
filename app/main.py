from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
import asyncio

# ======================
# MQTT
# ======================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_CONTROL = "ujat/iot/led/control"
TOPIC_STATUS  = "ujat/iot/led/status"

# ======================
# Estado
# ======================
estado_led = "OFF"
clientes_ws = set()

app = FastAPI()

# ======================
# WEB
# ======================
@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>ESP32 LED Control</title>
</head>
<body>
<h2>Control LED ESP32</h2>

<p>Estado: <span id="estado">Cargando...</span></p>
<button onclick="toggle()">Toggle LED</button>

<script>
const estadoTxt = document.getElementById("estado");

const ws = new WebSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws"
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  estadoTxt.textContent = data.state;
};

ws.onerror = () => {
  estadoTxt.textContent = "Error de conexión";
};

function toggle() {
  fetch("/toggle");
}
</script>
</body>
</html>
"""

# ======================
# WebSocket
# ======================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clientes_ws.add(ws)

    # Enviar estado inicial
    await ws.send_json({"state": estado_led})

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clientes_ws.remove(ws)

# ======================
# HTTP control
# ======================
@app.get("/toggle")
def toggle():
    global estado_led
    estado_led = "OFF" if estado_led == "ON" else "ON"
    mqtt_client.publish(TOPIC_CONTROL, estado_led)
    return {"state": estado_led}

# ======================
# MQTT
# ======================
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado")
    client.subscribe(TOPIC_STATUS)

def on_message(client, userdata, msg):
    global estado_led
    payload = msg.payload.decode()

    if payload in ["ON", "OFF"]:
        estado_led = payload

        # Notificar a todos los navegadores
        for ws in list(clientes_ws):
            asyncio.create_task(ws.send_json({"state": estado_led}))

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()
