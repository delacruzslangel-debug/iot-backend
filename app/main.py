from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (IMPORTANTÍSIMO para la web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego puedes restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global del LED
estado_led = {"led": False}

@app.get("/")
def root():
    return {"status": "Backend IoT activo"}

@app.get("/estado")
def obtener_estado():
    return estado_led

@app.post("/led/on")
def led_on():
    estado_led["led"] = True
    return {"ok": True, "led": True}

@app.post("/led/off")
def led_off():
    estado_led["led"] = False
    return {"ok": True, "led": False}
