"""Sensor pentru Termoenergetica București."""
from __future__ import annotations
import logging
import asyncio
from datetime import timedelta
import requests
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_PUNCT_TERMIC, CONF_STRADA

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    punct_termic = entry.data[CONF_PUNCT_TERMIC]
    strada = entry.data[CONF_STRADA]

    sensors = [
        TermoenergeticaApaSensor(punct_termic, strada),
        TermoenergeticaCalduraSensor(punct_termic, strada),
    ]
    
    async_add_entities(sensors, True)

class TermoenergeticaBaseSensor(SensorEntity):
    """Baza pentru senzorii Termoenergetica."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul."""
        self._punct_termic = punct_termic
        self._strada = strada
        self._attr_name = None
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    @property
    def unique_id(self) -> str:
        """Returnează un ID unic."""
        return f"termoenergetica_{self._punct_termic}_{self._strada}_{self._attr_name.lower()}"

    async def async_update(self):
        """Actualizează datele senzorului."""
        try:
            await self._fetch_data()
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea datelor: %s", e)
            self._attr_native_value = "Eroare"
            
    async def _fetch_data(self):
        """Extrage datele de pe site."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._scrape_website)

    def _scrape_website(self):
        """Scrape site-ul Termoenergetica pentru întreruperi."""
        try:
            response = requests.get("https://www.termoenergetica.ro/intreruperi-programate", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Aici trebuie să analizezi structura HTML-ului site-ului
            # Aceasta este o implementare exemplu - trebuie adaptată la structura reală
            
            interruptions = soup.find_all('div', class_='interruption-item')
            
            for interruption in interruptions:
                location = interruption.find('span', class_='location')
                service = interruption.find('span', class_='service')
                period = interruption.find('span', class_='period')
                
                if location and self._strada.lower() in location.text.lower():
                    if 'apă' in service.text:
                        self._update_apa_sensor(period.text)
                    elif 'căldură' in service.text:
                        self._update_caldura_sensor(period.text)
                        
        except Exception as e:
            _LOGGER.error("Eroare la scrape: %s", e)

class TermoenergeticaApaSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi apă."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru apă."""
        super().__init__(punct_termic, strada)
        self._attr_name = f"Termoenergetica Apă - {strada}"
        self._attr_icon = "mdi:water-pump"

    def _update_apa_sensor(self, period: str):
        """Actualizează senzorul pentru apă."""
        self._attr_native_value = "Întrerupt" if period else "Normal"
        self._attr_extra_state_attributes = {
            "perioada": period,
            "punct_termic": self._punct_termic,
            "strada": self._strada
        }

class TermoenergeticaCalduraSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi căldură."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru căldură."""
        super().__init__(punct_termic, strada)
        self._attr_name = f"Termoenergetica Căldură - {strada}"
        self._attr_icon = "mdi:radiator"

    def _update_caldura_sensor(self, period: str):
        """Actualizează senzorul pentru căldură."""
        self._attr_native_value = "Întrerupt" if period else "Normal"
        self._attr_extra_state_attributes = {
            "perioada": period,
            "punct_termic": self._punct_termic,
            "strada": self._strada
        }
