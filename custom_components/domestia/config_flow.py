import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_IP, CONF_MAC, DEFAULT_SCAN_INTERVAL, DEFAULT_DEBUG_MODE


class DomestiaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Domestia."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"Domestia ({user_input[CONF_IP]})",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_IP): str,
            vol.Required(CONF_MAC): str
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DomestiaOptionsFlowHandler(config_entry)


class DomestiaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Domestia options."""

    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        # Get current values or defaults
        current_interval = self._entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        current_debug = self._entry.options.get("debug_mode", DEFAULT_DEBUG_MODE)
        
        schema = vol.Schema({
            vol.Optional(
                "scan_interval",
                default=current_interval,
                description="Update interval in seconds (1-60)"
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Optional(
                "debug_mode",
                default=current_debug,
                description="Enable detailed logging for troubleshooting"
            ): bool
        })
        
        return self.async_show_form(step_id="init", data_schema=schema)
