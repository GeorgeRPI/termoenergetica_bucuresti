"""Sensor pentru Termoenergetica București - Fără dependințe externe."""
from __future__ import annotations
import logging
import asyncio
from datetime import timedelta
import urllib.request
import urllib.error
from html.parser import HTMLParser

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

class SimpleHTMLParser(HTMLParser):
    """Parser HTML simplu pentru a extrage textul."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        
    def handle_data(self, data):
        self.text_parts.append(data.strip())
        
    def get_full_text(self):
        return " ".join([part for part in self.text_parts if part])

class TermoenergeticaBaseSensor(SensorEntity):
    """Baza pentru senzorii Termoenergetica."""
    
    def __init__(self, punct_termic: str, strada: str, sensor_type: str):
        """Initializează senzorul."""
        self._punct_termic = punct_termic
        self._strada = strada
        self._sensor_type = sensor_type
        self._attr_native_value = "Necunoscut"
        self._attr_available = True
        
        # Setări de bază
        self._attr_name = f"Termoenergetica {sensor_type} - {strada}"
        self._attr_unique_id = f"termoenergetica_{sensor_type.lower()}_{punct_termic}_{strada.lower().replace(' ', '_').replace(',', '')}"
        
        if sensor_type == "Apă":
            self._attr_icon = "mdi:water-pump"
        else:
            self._attr_icon = "mdi:radiator"
        
        # Atribute
        self._attr_extra_state_attributes = {
            "punct_termic": punct_termic,
            "strada": strada,
            "ultima_actualizare": None,
            "stare": "Necunoscută"
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
        """Extrage datele de pe site folosind urllib."""
        try:
            # Folosim executorul pentru a nu bloca event loop
            html_content = await asyncio.get_event_loop().run_in_executor(
                None, self._download_page
            )
            
            await self._parse_html(html_content)
            
        except Exception as e:
            _LOGGER.error("Eroare la descărcare: %s", e)
            self._attr_native_value = "Eroare conexiune"

    def _download_page(self):
        """Descarcă conținutul paginii."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(
                "https://www.termoenergetica.ro/intreruperi-programate",
                headers=headers
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
                
        except urllib.error.URLError as e:
            _LOGGER.error("Eroare URL: %s", e)
            raise
        except Exception as e:
            _LOGGER.error("Eroare la descărcare: %s", e)
            raise

    async def _parse_html(self, html: str):
        """Parsează HTML-ul folosind parserul simplu."""
        try:
            # Folosim executorul pentru parsing
            parser = await asyncio.get_event_loop().run_in_executor(
                None, self._parse_html_content, html
            )
            
            page_text = parser.get_full_text().lower()
            search_text = self._strada.lower()
            
            _LOGGER.debug("Text extras din pagină: %s", page_text[:200])
            
            if search_text in page_text:
                # Verifică dacă este întrerupere pentru serviciul nostru
                if self._sensor_type == "Apă":
                    service_keywords = ['apă', 'apa', 'apei', 'apă potabilă']
                else:
                    service_keywords = ['căldură', 'caldura', 'caldurii', 'încălzire']
                
                service_found = any(keyword in page_text for keyword in service_keywords)
                
                if service_found:
                    self._attr_native_value = "Întrerupt"
                    self._attr_extra_state_attributes["stare"] = "Serviciu întrerupt"
                else:
                    self._attr_native_value = "Normal"
                    self._attr_extra_state_attributes["stare"] = "Serviciu normal"
            else:
                self._attr_native_value = "Normal"
                self._attr_extra_state_attributes["stare"] = "Fără întreruperi"
            
            self._attr_extra_state_attributes["ultima_actualizare"] = dt_util.now().isoformat()
            
        except Exception as e:
            _LOGGER.error("Eroare la parsare HTML: %s", e)
            self._attr_native_value = "Eroare procesare"

    def _parse_html_content(self, html: str):
        """Parsează conținutul HTML."""
        parser = SimpleHTMLParser()
        parser.feed(html)
        return parser

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
