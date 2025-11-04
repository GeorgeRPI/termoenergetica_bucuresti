"""Constante pentru Termoenergetica București."""
DOMAIN = "termoenergetica_bucuresti"
CONF_PUNCT_TERMIC = "punct_termic"
CONF_STRADA = "strada"

BASE_URL = "https://www.termoenergetica.ro"
API_URL = f"{BASE_URL}/intreruperi-programate"

PUNCTE_TERMICE = {
    "centru": "Centru",
    "vest": "Vest", 
    "sud": "Sud",
    "nord": "Nord",
    "est": "Est"
}

SCAN_INTERVAL = 30  # minute
