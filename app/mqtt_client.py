import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPIC_CMD = "home/foco1/cmd"
TOPIC_STATE = "home/foco1/state"

estado = "OFF"

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(TOPIC_STATE)

def on_message(client, userdata, msg):
    global estado
    estado = msg.payload.decode()
    print("Estado recibido:", estado)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    client.connect(BROKER, 1883, 60)
    client.loop_start()

def enviar_comando(cmd):
    client.publish(TOPIC_CMD, cmd, retain=True)

def obtener_estado():
    return estado
