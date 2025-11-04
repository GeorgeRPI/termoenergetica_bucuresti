# Termoenergetica București pentru Home Assistant

Monitorizează întreruperile programate la apă și căldură de la Termoenergetica București direct în Home Assistant.

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)

## Caracteristici

- ✅ Monitorizare întreruperi apă
- ✅ Monitorizare întreruperi căldură  
- ✅ Selectare punct termic
- ✅ Configurare după stradă
- ✅ Actualizare automată la 30 de minute

## Instalare

### Metoda 1: Via HACS (Recomandat)

1. Deschide HACS în Home Assistant
2. Click pe **Integrations**
3. Click pe butonul ⋮ din colțul dreapta sus
4. Selectează **Custom repositories**
5. Adaugă:
   - Repository: `https://github.com/numeletau/termoenergetica_bucuresti`
   - Category: **Integration**
6. Click **Add**
7. Caută "Termoenergetica București" în HACS și instalează
8. Restartează Home Assistant

### Metoda 2: Manual

1. Descarcă ultima versiune [de aici](https://github.com/numeletau/termoenergetica_bucuresti/releases)
2. Copiază folderul `termoenergetica_bucuresti` în `config/custom_components/`
3. Restartează Home Assistant

## Configurare

1. Deschide Home Assistant
2. Mergi la **Configuration** → **Integrations**
3. Click pe **+ Add Integration**
4. Caută **"Termoenergetica București"**
5. Completează:
   - **Punct termic**: Alege din listă
   - **Stradă**: Introdu numele străzii tale

## Senzori

După configurare, vei avea 2 senzori noi:

- `sensor.termoenergetica_apa_stradata` - Starea apei
- `sensor.termoenergetica_caldura_stradata` - Starea căldurii

**Stări posibile:**
- `Normal` - Fără întreruperi
- `Întrerupt` - Serviciu întrerupt
- `Eroare` - Problemă la conectare

## Atribute

Fiecare senzor afișează:
- `perioada`: Perioada întreruperii
- `punct_termic`: Punctul termic selectat  
- `strada`: Strada monitorizată

## Suport

Dacă întâmpini probleme:
1. Verifică logs-urile Home Assistant
2. Asigură-te că strada este scrisă corect
3. Verifică conexiunea la internet

## Contribuții

Contribuțiile sunt binevenite! Poți:
- Raporta bug-uri
- Sugera îmbunătățiri
- Contribui cu cod

## Licență

Acest proiect este under MIT License.
