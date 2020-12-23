"""Model for a base Blue Connect entity."""

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity


class BlueConnectEntity(Entity):
    """Representation of generic BlueConnect entity."""

    def __init__(self, blue_api, unique_id, data):
        """Initialize a BlueConnect sensor entity."""
        self._api = blue_api
        self._unique_id = unique_id
        self._data = data

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def unique_id(self):
        """Return the unique_id of the entity."""
        return self._unique_id

    @callback
    def update_data(self, new_data):
        """Update entity with new data."""
        self._data = new_data
        self.async_write_ha_state()
