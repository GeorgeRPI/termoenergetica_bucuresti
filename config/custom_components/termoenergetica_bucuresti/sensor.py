"""Sensor for Termoenergetica Bucuresti."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor."""
    strada = entry.data["strada"]
    async_add_entities([
        TermoenergeticaSensor(strada, "apă"),
        TermoenergeticaSensor(strada, "căldură")
    ])

class TermoenergeticaSensor(SensorEntity):
    """Termoenergetica Sensor."""
    
    def __init__(self, strada: str, service_type: str):
        self._strada = strada
        self._service_type = service_type
        self._attr_name = f"Termoenergetica {service_type} - {strada}"
        self._attr_unique_id = f"termo_{service_type}_{strada.replace(' ', '_').replace(',', '').lower()}"
        self._attr_native_value = "Necunoscut"
        self._attr_available = True
        
        if service_type == "apă":
            self._attr_icon = "mdi:water-pump"
        else:
            self._attr_icon = "mdi:radiator"

    async def async_update(self):
        """Update sensor."""
        try:
            session = async_get_clientsession(self.hass)
            
            # Folosim URL-ul corect pentru CMTEB
            async with session.get(
                "https://www.cmteb.ro/functionare_sistem_termoficare.php",
                timeout=10
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    await self._process_page_content(text)
                else:
                    self._attr_native_value = "Eroare site"
                    self._attr_available = False
                    
        except asyncio.TimeoutError:
            self._attr_native_value = "Timeout"
            self._attr_available = False
        except Exception as e:
            _LOGGER.error("Eroare la conectare: %s", e)
            self._attr_native_value = "Eroare conexiune"
            self._attr_available = False

    async def _process_page_content(self, text: str):
        """Process the HTML content."""
        text_lower = text.lower()
        strada_lower = self._strada.lower()
        
        # Verifică dacă strada apare pe pagină
        if strada_lower in text_lower:
            # Verifică tipul de serviciu
            if self._service_type == "apă":
                service_keywords = ['apă', 'apa', 'apei', 'apă potabilă']
                if any(keyword in text_lower for keyword in service_keywords):
                    self._attr_native_value = "Întrerupt"
                else:
                    self._attr_native_value = "Normal"
            else:
                service_keywords = ['căldură', 'caldura', 'caldurii', 'încălzire', 'incalzire']
                if any(keyword in text_lower for keyword in service_keywords):
                    self._attr_native_value = "Întrerupt"
                else:
                    self._attr_native_value = "Normal"
        else:
            self._attr_native_value = "Normal"
        
        self._attr_available = True
