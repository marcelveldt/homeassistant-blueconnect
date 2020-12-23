"""Config flow for ozw integration."""
import voluptuous as vol

from homeassistant import config_entries

from blueconnect import BlueConnectApi
from .const import DOMAIN  # pylint:disable=unused-import

TITLE = "Blue Connect"

API_LANGUAGES = ["fr", "es", "en", "nl", "de", "it", "pt", "cs"]


async def validate_credentials(username, password):
    """Validate credentials for Blue Connect API."""
    blue_api = BlueConnectApi(username, password)
    user_info = await blue_api.get_user_info()
    await blue_api.close_async()
    return user_info not in [None, {}]


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ozw."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate credentials
            valid_credentials = await validate_credentials(
                user_input["username"], user_input["password"])
            if not valid_credentials:
                errors["base"] = "invalid_credentials"
            else:
                # finish
                return self.async_create_entry(title=TITLE, data=user_input)

        # Specify items in the order they are to be displayed in the UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                    vol.Required("language", default="en"): vol.In(API_LANGUAGES),
                }
            ),
            errors=errors,
        )
