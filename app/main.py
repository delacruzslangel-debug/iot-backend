from fastapi import FastAPI
from app.mqtt_client import start_mqtt, enviar_comando, obtener_estado

app = FastAPI()

@app.on_event("startup")
def startup():
    start_mqtt()

@app.get("/")
def root():
    return {"status": "Backend IoT activo"}

@app.post("/toggle")
def toggle():
    nuevo = "OFF" if obtener_estado() == "ON" else "ON"
    enviar_comando(nuevo)
    return {"estado": nuevo}

@app.get("/state")
def state():
    return {"estado": obtener_estado()}
