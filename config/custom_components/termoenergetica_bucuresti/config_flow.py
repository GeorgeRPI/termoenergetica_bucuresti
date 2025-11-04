"""Config flow for Termoenergetica."""
from homeassistant import config_entries
import voluptuous as vol

class ConfigFlow(config_entries.ConfigFlow, domain="termoenergetica_bucuresti"):
    """Config flow."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Termoenergetica",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("strada"): str,
            vol.Required("zona", default="centru"): vol.In({
                "centru": "Centru",
                "nord": "Nord",
                "sud": "Sud",
                "est": "Est", 
                "vest": "Vest"
            })
        })
        
        return self.async_show_form(step_id="user", data_schema=schema)
