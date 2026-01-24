from fastapi import APIRouter
from app.mqtt_client import publish_message

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

@router.post("/{device_id}/on")
def turn_on(device_id: str):
    topic = f"home/{device_id}/cmd"
    publish_message(topic, "ON")
    return {
        "device": device_id,
        "state": "ON"
    }

@router.post("/{device_id}/off")
def turn_off(device_id: str):
    topic = f"home/{device_id}/cmd"
    publish_message(topic, "OFF")
    return {
        "device": device_id,
        "state": "OFF"
    }
