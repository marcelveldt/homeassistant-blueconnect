"""Example Load Platform integration."""

import asyncio
import logging
from datetime import timedelta

import async_timeout
import voluptuous as vol

from blueconnect import BlueConnectSimpleAPI
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (DATA_KEY_API, DATA_KEY_UPDATE_TASK, DOMAIN, PLATFORMS,
                    SERVICE_UPDATE, SIGNAL_API_UPDATED)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


def run_periodic(period):
    def scheduler(fcn):
        async def wrapper(*args, **kwargs):
            while True:
                asyncio.create_task(fcn(*args, **kwargs))
                await asyncio.sleep(period)
        return wrapper
    return scheduler


async def async_setup(hass: HomeAssistant, config: dict):
    """Initialize basic config of component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up BlueConnect integration from a config entry."""
    username = entry.options.get("username", entry.data.get("username"))
    password = entry.options.get("password", entry.data.get("password"))
    language = entry.options.get("language", entry.data.get("language", "en"))
    blue_api = BlueConnectSimpleAPI(username, password, language)
    # store blue_api in hass data object
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_KEY_API: blue_api
    }

    async def start_platforms():
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_setup(entry, component)
                for component in PLATFORMS
            ]
        )

    @run_periodic(3600)
    async def async_update_data():
        """Fetch data from API endpoint."""
        async with async_timeout.timeout(10):
            blue_api = hass.data[DOMAIN][entry.entry_id][DATA_KEY_API]
            await blue_api.fetch_data()
            # inform platforms that we received (new) data
            async_dispatcher_send(hass, SIGNAL_API_UPDATED)

    async def force_update(service):
        """Update an existing schedule."""
        await hass.data[DOMAIN][entry.entry_id][DATA_KEY_API].fetch_data()
        async_dispatcher_send(hass, SIGNAL_API_UPDATED)

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE,
        force_update
    )

    # start platforms
    hass.async_create_task(start_platforms())

    # Fetch initial data
    hass.data[DOMAIN][entry.entry_id][DATA_KEY_UPDATE_TASK] = asyncio.create_task(
        async_update_data())

    # close api when hass stops
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, blue_api.close)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN][entry.entry_id][DATA_KEY_UPDATE_TASK].cancel()
    await hass.data[DOMAIN][entry.entry_id][DATA_KEY_API].close_async()
    return True
