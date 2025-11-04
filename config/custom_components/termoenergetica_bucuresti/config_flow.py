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
                title=f"Termoenergetica - {user_input['strada']}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("strada"): str,
        })
        
        return self.async_show_form(step_id="user", data_schema=schema)
