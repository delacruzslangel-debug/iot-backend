from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>ESP32 Dashboard</title>
</head>
<body>
    <h1>ESP32 conectado</h1>

    <button onclick="enviar()">Enviar petición</button>

    <p id="respuesta"></p>

    <script>
        async function enviar() {
            try {
                const res = await fetch("/api/test");
                const data = await res.json();
                document.getElementById("respuesta").innerText = data.mensaje;
            } catch (e) {
                document.getElementById("respuesta").innerText = "Error de conexión";
            }
        }
    </script>
</body>
</html>
"""
    

@app.get("/api/test")
def test():
    return {"mensaje": "Backend funcionando correctamente 🚀"}
