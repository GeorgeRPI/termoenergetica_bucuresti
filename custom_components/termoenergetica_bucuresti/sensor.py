"""Sensor pentru Termoenergetica București - Versiune reparată."""
from __future__ import annotations
import logging
import asyncio
from datetime import timedelta
import aiohttp
from bs4 import BeautifulSoup
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    punct_termic = entry.data["punct_termic"]
    strada = entry.data["strada"]

    sensors = [
        TermoenergeticaApaSensor(punct_termic, strada),
        TermoenergeticaCalduraSensor(punct_termic, strada),
    ]
    
    async_add_entities(sensors, True)

class TermoenergeticaBaseSensor(SensorEntity):
    """Baza pentru senzorii Termoenergetica."""
    
    def __init__(self, punct_termic: str, strada: str, sensor_type: str):
        """Initializează senzorul."""
        self._punct_termic = punct_termic
        self._strada = strada
        self._sensor_type = sensor_type
        self._attr_native_value = "Necunoscut"
        self._attr_available = True
        self._last_update = None
        
        # Setări de bază
        self._attr_name = f"Termoenergetica {sensor_type} - {strada}"
        self._attr_unique_id = f"termoenergetica_{sensor_type.lower()}_{punct_termic}_{strada.lower().replace(' ', '_')}"
        
        if sensor_type == "Apă":
            self._attr_icon = "mdi:water-pump"
        else:
            self._attr_icon = "mdi:radiator"
        
        # Atribute
        self._attr_extra_state_attributes = {
            "punct_termic": punct_termic,
            "strada": strada,
            "perioada_intrerupere": "Necunoscută",
            "ultima_actualizare": None,
        }

    async def async_update(self):
        """Actualizează datele senzorului."""
        try:
            await self._fetch_data()
            self._attr_available = True
        except Exception as e:
            _LOGGER.error("Eroare la actualizare: %s", e)
            self._attr_native_value = "Eroare"
            self._attr_available = False

    async def _fetch_data(self):
        """Extrage datele de pe site."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://www.termoenergetica.ro/intreruperi-programate", headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        await self._parse_html(html)
                    else:
                        self._attr_native_value = "Eroare site"

        except Exception as e:
            _LOGGER.error("Eroare conexiune: %s", e)
            self._attr_native_value = "Eroare conexiune"

    async def _parse_html(self, html: str):
        """Parsează HTML-ul."""
        soup = BeautifulSoup(html, 'html.parser')
        search_text = self._strada.lower()
        
        # Caută în tot textul paginii
        page_text = soup.get_text().lower()
        
        if search_text in page_text:
            # Verifică dacă este întrerupere pentru serviciul nostru
            if self._sensor_type == "Apă":
                service_keywords = ['apă', 'apa', 'apei']
            else:
                service_keywords = ['căldură', 'caldura', 'caldurii']
            
            if any(keyword in page_text for keyword in service_keywords):
                self._attr_native_value = "Întrerupt"
                self._attr_extra_state_attributes["perioada_intrerupere"] = "Detectat"
            else:
                self._attr_native_value = "Normal"
        else:
            self._attr_native_value = "Normal"
        
        self._attr_extra_state_attributes["ultima_actualizare"] = dt_util.now().isoformat()

class TermoenergeticaApaSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi apă."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru apă."""
        super().__init__(punct_termic, strada, "Apă")

class TermoenergeticaCalduraSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi căldură."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru căldură."""
        super().__init__(punct_termic, strada, "Căldură")
