"""Platforma Termoenergetica București."""
from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setare configurare."""
    hass.data.setdefault("termoenergetica_bucuresti", {})
    
    # Setup platform sensor
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Încărcare configurare."""
    await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return True
