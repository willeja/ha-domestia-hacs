import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback




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

