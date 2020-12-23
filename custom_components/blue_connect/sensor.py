"""Representation of BlueConnect sensors."""

import logging


from homeassistant.components.sensor import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.dt import as_local

from .const import SIGNAL_API_UPDATED, DOMAIN
from .base_entity import BlueConnectEntity
from blueconnect.models import TemperatureUnit

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BlueConnect sensor platform from config entry."""

    sensors = {}
    blue_api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    @callback
    def async_data_received():
        """Create/update entities when data is received."""
        pool_id = blue_api.pool.swimming_pool_id
        # process pool measurements as sensors
        for measurement in blue_api.measurements:
            sensor_id = f"{pool_id}.{measurement.name}"
            if sensor_id not in sensors:
                # create entity
                sensors[sensor_id] = BlueConnectMeasurementSensor(
                    blue_api, sensor_id, measurement)
                async_add_entities([sensors[sensor_id]])
            else:
                # update existing sensor entity
                sensors[sensor_id].update_data(measurement)

    async_dispatcher_connect(
        hass, SIGNAL_API_UPDATED, async_data_received
    )


class BlueConnectMeasurementSensor(BlueConnectEntity):
    """Representation of a BlueConnect Measurement entity."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self._data.name == "temperature":
            return DEVICE_CLASS_TEMPERATURE
        return None

    @property
    def state(self):
        """Return state of the sensor."""
        return self._data.value

    @property
    def name(self):
        """Return the default name for the entity."""
        return f"{self._api.pool.name}: {self._data.name}"

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            "last_update": as_local(self._data.timestamp).strftime("%x %X"),
            "trend": self._data.trend.value,
            "ok_min": self._data.ok_min,
            "ok_max": self._data.ok_max,
            "warning_high": self._data.warning_high,
            "warning_low": self._data.warning_low,
            "issuer": self._data.issuer
        }

    @property
    def unit_of_measurement(self):
        """Return unit of measurement the value is expressed in."""
        if self._data.name == "temperature":
            if self._api.temperature_unit == TemperatureUnit.CELSIUS:
                return TEMP_CELSIUS
            return TEMP_FAHRENHEIT
        if self._data.name == "orp":
            return "mV"
        return None
