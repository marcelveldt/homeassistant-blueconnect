"""Representation of BlueConnect binary sensors."""

import logging

from homeassistant.components.binary_sensor import (DEVICE_CLASS_BATTERY,
                                                    DEVICE_CLASS_PROBLEM)
from homeassistant.components.binary_sensor import \
    DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_API_UPDATED

from.base_entity import BlueConnectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up BlueConnect sensor platform from config entry."""

    sensors = {}
    blue_api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    @callback
    def async_data_received():
        """Create/update entities when data is received."""
        if blue_api.blue_device:
            # blue device battery sensor
            sensor_id = f"{blue_api.blue_device.serial}.battery"
            if sensor_id not in sensors:
                # create entity
                sensors[sensor_id] = BlueConnectBatterySensor(
                    blue_api, sensor_id, blue_api.blue_device)
                async_add_entities([sensors[sensor_id]])
            else:
                # update existing sensor entity
                sensors[sensor_id].update_data(blue_api.blue_device)
        if blue_api.feed_message:
            # feed message translated to status binary sensor
            sensor_id = f"{blue_api.pool.swimming_pool_id}.feed"
            if sensor_id not in sensors:
                # create entity
                sensors[sensor_id] = BlueConnectStatusSensor(
                    blue_api, sensor_id, blue_api.feed_message)
                async_add_entities([sensors[sensor_id]])
            else:
                # update existing sensor entity
                sensors[sensor_id].update_data(blue_api.feed_message)

    async_dispatcher_connect(
        hass, SIGNAL_API_UPDATED, async_data_received
    )


class BlueConnectBatterySensor(BlueConnectEntity, BinarySensorEntity):
    """Representation of BlueConnect battery entity."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS_BATTERY

    @property
    def is_on(self):
        """Return state of the sensor."""
        return self._data.battery_low

    @property
    def name(self):
        """Return the unique_id of the entity."""
        return f"{self._data.hw_product_name} {self._data.hw_product_type}: Battery low"

    @property
    def device_info(self):
        """Return device information for the device registry."""
        return {
            "identifiers": {(DOMAIN, self._data.serial)},
            "name": f"{self._data.hw_product_name} {self._data.hw_product_type}",
            "manufacturer": "Blue Riiot",
            "model": self._data.hw_product_type,
            "serial": self._data.serial
        }


class BlueConnectStatusSensor(BlueConnectEntity, BinarySensorEntity):
    """Representation of BlueConnect status(feed) entity."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS_PROBLEM

    @property
    def is_on(self):
        """Return state of the sensor."""
        return self._data.id != "SWP_OK"

    @property
    def name(self):
        """Return the unique_id of the entity."""
        return f"{self._api.pool.name}: Pool status"

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            "title": self._data.title,
            "message": self._data.message
        }
