"""Constants for the ozw integration."""
from homeassistant.components.binary_sensor import \
    DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN

DOMAIN = "blue_connect"
PLATFORMS = [
    SENSOR_DOMAIN,
    BINARY_SENSOR_DOMAIN
]


# Signals
SIGNAL_API_UPDATED = f"{DOMAIN}_api_updated"

# Services
SERVICE_UPDATE = "update"

# Hass data key names
DATA_KEY_API = "api"
DATA_KEY_UPDATE_TASK = "update_task"
