"""Config flow pentru Termoenergetica București."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import logging

_LOGGER = logging.getLogger(__name__)

class TermoenergeticaConfigFlow(config_entries.ConfigFlow, domain="termoenergetica_bucuresti"):
    """Handle a config flow for Termoenergetica București."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Verifică unicitate
            await self.async_set_unique_id(
                f"termo_{user_input['punct_termic']}_{user_input['strada']}".lower()
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Termoenergetica - {user_input['strada']}",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required("punct_termic", default="centru"): vol.In({
                "centru": "Centru",
                "vest": "Vest", 
                "sud": "Sud",
                "nord": "Nord",
                "est": "Est"
            }),
            vol.Required("strada"): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )
