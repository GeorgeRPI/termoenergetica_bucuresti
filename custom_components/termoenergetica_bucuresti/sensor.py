"""Sensor pentru Termoenergetica București - Versiune funcțională."""
from __future__ import annotations
import logging
import asyncio
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

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
        self._attr_native_value = "Necunoscut"
        self._attr_available = True
        self._last_update = None
        self._interruption_details = ""
        
        # Atribute comune
        self._attr_extra_state_attributes = {
            "punct_termic": punct_termic,
            "strada": strada,
            "perioada_intrerupere": "Necunoscută",
            "detaliu_intrerupere": "",
            "ultima_actualizare": None,
            "zona_afectata": ""
        }

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return self._attr_available

    async def async_update(self):
        """Actualizează datele senzorului."""
        try:
            self._attr_available = False
            await self._fetch_data()
            self._attr_available = True
            self._last_update = dt_util.now()
            self._attr_extra_state_attributes["ultima_actualizare"] = self._last_update.isoformat()
            
        except Exception as e:
            _LOGGER.error("Eroare la actualizarea datelor pentru %s: %s", self._strada, e)
            self._attr_native_value = "Eroare conexiune"
            self._attr_available = False

    async def _fetch_data(self):
        """Extrage datele de pe site."""
        try:
            # Headers pentru a evita blocarea
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get("https://www.termoenergetica.ro/intreruperi-programate", headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        await self._parse_html(html)
                    else:
                        _LOGGER.error("Site-ul a returnat status code: %s", response.status)
                        self._attr_native_value = "Eroare site"
                        
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout la conectarea la site")
            self._attr_native_value = "Timeout"
        except Exception as e:
            _LOGGER.error("Eroare la conectare: %s", e)
            self._attr_native_value = "Eroare conexiune"

    async def _parse_html(self, html: str):
        """Parsează HTML-ul și extrage informațiile."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Curățăm textul pentru căutare
        search_strada = self._strada.lower().strip()
        
        # Căutăm toate secțiunile care conțin informații despre întreruperi
        # Vom căuta în toate elementele care conțin text relevant
        
        # Strategie 1: Căutăm în toate paragrafele și div-urile
        text_elements = soup.find_all(['p', 'div', 'span', 'td', 'li'])
        
        interruption_found = False
        service_type = self._get_service_type()
        
        for element in text_elements:
            text = element.get_text().strip()
            if text and len(text) > 10:  # Ignoră texte foarte scurte
                # Verifică dacă conține numele străzii și serviciul
                if (search_strada in text.lower() and 
                    self._contains_service_keywords(text, service_type)):
                    
                    interruption_found = True
                    self._process_interruption_text(text, service_type)
                    break
        
        # Strategie 2: Dacă nu găsim cu căutarea directă, încercăm să găsim tabele
        if not interruption_found:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join(cell.get_text().strip() for cell in cells)
                    if (search_strada in row_text.lower() and 
                        self._contains_service_keywords(row_text, service_type)):
                        
                        interruption_found = True
                        self._process_interruption_text(row_text, service_type)
                        break
                if interruption_found:
                    break
        
        # Setează starea finală
        if interruption_found:
            self._attr_native_value = "Întrerupt"
        else:
            self._attr_native_value = "Normal"
            self._attr_extra_state_attributes.update({
                "perioada_intrerupere": "Nu sunt întreruperi",
                "detaliu_intrerupere": f"Serviciu {service_type} funcțional",
                "zona_afectata": self._punct_termic
            })

    def _get_service_type(self) -> str:
        """Returnează tipul de serviciu pentru entitate."""
        if "apă" in self._attr_name.lower() or "apa" in self._attr_name.lower():
            return "apă"
        return "căldură"

    def _contains_service_keywords(self, text: str, service_type: str) -> bool:
        """Verifică dacă textul conține cuvinte cheie pentru serviciu."""
        text_lower = text.lower()
        
        if service_type == "apă":
            keywords = ['apă', 'apa', 'apei', 'apă potabilă', 'water', 'serviciu apă']
        else:
            keywords = ['căldură', 'caldura', 'caldurii', 'încălzire', 'incalzire', 'heat', 'heating']
        
        return any(keyword in text_lower for keyword in keywords)

    def _process_interruption_text(self, text: str, service_type: str):
        """Procesează textul întreruperii și extrage detaliile."""
        # Curățăm textul
        cleaned_text = ' '.join(text.split())
        
        # Extragem data/perioada folosind regex
        date_patterns = [
            r'\d{1,2}\s*[\.\/-]\s*\d{1,2}\s*[\.\/-]\s*\d{4}',
            r'\d{1,2}\s*[a-zA-Z]+\s*\d{4}',
            r'\d{1,2}\s*[-–]\s*\d{1,2}\s*[a-zA-Z]+',
            r'[0-9]{1,2}:[0-9]{2}\s*[-–]\s*[0-9]{1,2}:[0-9]{2}'
        ]
        
        period = "Perioadă necunoscută"
        for pattern in date_patterns:
            match = re.search(pattern, cleaned_text)
            if match:
                period = match.group()
                break
        
        # Setăm atributele
        self._attr_extra_state_attributes.update({
            "perioada_intrerupere": period,
            "detaliu_intrerupere": cleaned_text[:200],  # Limităm lungimea
            "zona_afectata": self._punct_termic,
            "strada_afectata": self._strada
        })
        
        _LOGGER.info("Întrerupere găsită pentru %s: %s", self._strada, cleaned_text[:100])

class TermoenergeticaApaSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi apă."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru apă."""
        super().__init__(punct_termic, strada)
        self._attr_name = f"Termoenergetica Apă - {strada}"
        self._attr_icon = "mdi:water-pump"
        self._attr_unique_id = f"termoenergetica_apa_{punct_termic}_{strada.lower().replace(' ', '_')}"
        self._attr_device_class = None

class TermoenergeticaCalduraSensor(TermoenergeticaBaseSensor):
    """Senzor pentru întreruperi căldură."""
    
    def __init__(self, punct_termic: str, strada: str):
        """Initializează senzorul pentru căldură."""
        super().__init__(punct_termic, strada)
        self._attr_name = f"Termoenergetica Căldură - {strada}"
        self._attr_icon = "mdi:radiator"
        self._attr_unique_id = f"termoenergetica_caldura_{punct_termic}_{strada.lower().replace(' ', '_')}"
        self._attr_device_class = None
