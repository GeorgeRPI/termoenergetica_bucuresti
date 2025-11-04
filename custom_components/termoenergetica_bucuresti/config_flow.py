"""Config flow pentru Termoenergetica București."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_PUNCT_TERMIC, CONF_STRADA, PUNCTE_TERMICE

class TermoenergeticaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Termoenergetica București."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"Termoenergetica - {user_input[CONF_STRADA]}",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_PUNCT_TERMIC): vol.In(PUNCTE_TERMICE),
            vol.Required(CONF_STRADA): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )
