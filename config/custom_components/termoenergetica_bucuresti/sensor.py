"""Sensor for Termoenergetica."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
        self._attr_unique_id = f"termo_{service_type}_{strada.replace(' ', '_').lower()}"
        self._attr_native_value = "Necunoscut"
        
        if service_type == "apă":
            self._attr_icon = "mdi:water-pump"
        else:
            self._attr_icon = "mdi:radiator"

    async def async_update(self):
        """Update sensor."""
        try:
            session = async_get_clientsession(self.hass)
            
            # Folosim URL-ul tău corect
            async with session.get(
                "https://www.cmteb.ro/functionare_sistem_termoficare.php",
                timeout=10
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    
                    # Verifică dacă strada apare pe pagină
                    if self._strada.lower() in text.lower():
                        # Verifică tipul de serviciu
                        if self._service_type == "apă":
                            if any(keyword in text.lower() for keyword in ['apă', 'apa', 'apei']):
                                self._attr_native_value = "Întrerupt"
                            else:
                                self._attr_native_value = "Normal"
                        else:
                            if any(keyword in text.lower() for keyword in ['căldură', 'caldura', 'caldurii']):
                                self._attr_native_value = "Întrerupt"
                            else:
                                self._attr_native_value = "Normal"
                    else:
                        self._attr_native_value = "Normal"
                else:
                    self._attr_native_value = "Eroare site"
                    
        except Exception as e:
            self._attr_native_value = "Eroare conexiune"
