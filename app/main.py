<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Control IoT LED</title>

  <style>
    body {
      font-family: Arial, sans-serif;
      background: #0f172a;
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 80px;
    }

    h1 {
      margin-bottom: 20px;
    }

    #estado {
      font-size: 20px;
      margin-bottom: 20px;
    }

    button {
      font-size: 22px;
      padding: 15px 40px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: 0.2s;
    }

    .on {
      background: #22c55e;
      color: black;
    }

    .off {
      background: #ef4444;
      color: white;
    }
  </style>
</head>

<body>

  <h1>🔌 Control de LED (ESP32)</h1>
  <p id="estado">Estado: Cargando...</p>
  <button id="btn" class="off" onclick="toggle()">Cargando...</button>

  <script>
    // =========================
    // WebSocket seguro (Render)
    // =========================
    const protocolo = location.protocol === "https:" ? "wss://" : "ws://";
    const ws = new WebSocket(protocolo + location.host + "/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      actualizar(data.state);
    };

    ws.onerror = () => {
      document.getElementById("estado").innerText = "Error de conexión";
      document.getElementById("btn").innerText = "Sin conexión";
    };

    // =========================
    // Toggle LED
    // =========================
    function toggle() {
      fetch("/toggle")
        .catch(() => {
          document.getElementById("estado").innerText = "Error backend";
        });
    }

    // =========================
    // Actualizar UI
    // =========================
    function actualizar(state) {
      const btn = document.getElementById("btn");
      const estado = document.getElementById("estado");

      estado.innerText = "Estado: " + state;

      if (state === "ON") {
        btn.innerText = "APAGAR";
        btn.className = "off";
      } else if (state === "OFF") {
        btn.innerText = "ENCENDER";
        btn.className = "on";
      }
    }
  </script>

</body>
</html>
