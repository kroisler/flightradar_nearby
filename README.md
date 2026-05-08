# ✈️ Flightradar Nearby

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant Integration die alle aktuellen Flüge in einem konfigurierbaren Radius um einen Standort anzeigt.

## Features

- Flüge im Umkreis mit allen Details:
  - Flugnummer & Airline
  - Startflughafen + Abflugzeit
  - Zielflughafen + Landezeit
  - Flugzeugtyp & Registration
  - Höhe, Geschwindigkeit, Heading
  - Entfernung zum Standort
- Konfigurierbarer Radius (km)
- Konfigurierbares Update-Intervall
- UI-basierte Einrichtung (Config Flow)
- Nächster Flug als Top-Level Attribute
- Custom Lovelace Card mit Mini-Karte (verschwindet wenn keine Flüge)

## Installation

### HACS (empfohlen)

1. HACS → Integrationen → ⋮ (drei Punkte oben rechts) → **Benutzerdefinierte Repositories**
2. URL: `https://github.com/kroisler/flightradar_nearby`
3. Kategorie: **Integration**
4. Klick auf "Hinzufügen"
5. Suche nach "Flightradar Nearby" → Installieren
6. Home Assistant neustarten
7. Einstellungen → Geräte & Dienste → **+ Integration hinzufügen** → "Flightradar Nearby"

### Lovelace Card installieren

1. Kopiere `www/flightradar-nearby-card.js` nach `/config/www/`
2. Dashboard → ⋮ → Ressourcen → Ressource hinzufügen:
   - URL: `/local/flightradar-nearby-card.js`
   - Typ: JavaScript-Modul

### Manuell (ohne HACS)

1. Kopiere `custom_components/flightradar_nearby/` nach `/config/custom_components/`
2. Home Assistant neustarten
3. Einstellungen → Geräte & Dienste → Integration hinzufügen → "Flightradar Nearby"

## Konfiguration

Bei der Einrichtung gibst du an:

| Feld | Beschreibung | Standard |
|------|-------------|----------|
| Breitengrad | Zentrum des Suchradius | HA-Standort |
| Längengrad | Zentrum des Suchradius | HA-Standort |
| Radius | Suchradius in km | 50 |
| Intervall | Update-Intervall in Sekunden | 30 |

## Entities

| Entity | Beschreibung |
|--------|-------------|
| `sensor.fluge_in_der_nahe` | Anzahl Flüge im Radius |
| `sensor.flightradar_fluge` | Alle Flugdetails als Attribute |

### Attribute von `sensor.flightradar_fluge`

- `flights` – Array mit allen Flügen (sortiert nach Entfernung)
- `nearest_flight` – Flugnummer des nächsten Flugs
- `nearest_airline` – Airline des nächsten Flugs
- `nearest_origin` – Startflughafen
- `nearest_destination` – Zielflughafen
- `nearest_distance_km` – Entfernung in km

### Jeder Flug im `flights`-Array enthält:

```json
{
  "flight_number": "LH1234",
  "airline": "Lufthansa",
  "aircraft_type": "A320",
  "registration": "D-AIZQ",
  "origin_airport": "Frankfurt am Main",
  "origin_iata": "FRA",
  "destination_airport": "München",
  "destination_iata": "MUC",
  "departure_time": "14:30",
  "arrival_time": "15:25",
  "altitude": 35000,
  "speed": 450,
  "heading": 180,
  "distance_km": 12.3
}
```

## Lovelace Card

Die passende Lovelace Card ist als separates HACS-Frontend-Repo verfügbar:

👉 **[flightradar-nearby-card](https://github.com/kroisler/flightradar-nearby-card)**

Installation: HACS → Frontend → ⋮ → Benutzerdefinierte Repositories → URL eintragen → Kategorie: Lovelace

### Konfiguration

```yaml
type: custom:flightradar-nearby-card
entity: sensor.flightradar_fluge
max_flights: 3
show_map: true
title: "✈️ Flüge in der Nähe"
```

| Option | Beschreibung | Standard |
|--------|-------------|----------|
| `entity` | Entity-ID des Flightradar-Sensors | *Pflicht* |
| `max_flights` | Maximale Anzahl angezeigter Flüge | 3 |
| `show_map` | Mini-Karte pro Flug anzeigen | true |
| `title` | Card-Titel | "✈️ Flüge in der Nähe" |

**Hinweis:** Die Card verschwindet automatisch wenn keine Flüge im Radius sind.

Siehe `lovelace-card.yaml` für weitere Beispiele (Markdown-Tabelle, Mushroom-Card).

## Hinweise

- Die Flightradar24 API ist kostenlos, hat aber Rate-Limits. Ein Intervall von 30s ist empfohlen.
- Nicht alle Flüge haben vollständige Details (Abflug-/Landezeit, Airline).
- Die Integration nutzt die inoffizielle FlightRadar24 Python API.
