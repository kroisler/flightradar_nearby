"""DataUpdateCoordinator for Flightradar Nearby."""
from __future__ import annotations

import logging
from datetime import timedelta, datetime, timezone

from FlightRadar24 import FlightRadar24API
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS

_LOGGER = logging.getLogger(__name__)


class FlightradarCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch flight data from Flightradar24."""

    def __init__(self, hass: HomeAssistant, config: dict, scan_interval: int) -> None:
        """Initialize."""
        self._lat = config[CONF_LATITUDE]
        self._lon = config[CONF_LONGITUDE]
        self._radius = config[CONF_RADIUS]
        self._api = FlightRadar24API()

        super().__init__(
            hass,
            _LOGGER,
            name="Flightradar Nearby",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from Flightradar24 API."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_flights)
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Flugdaten: {err}") from err

    def _fetch_flights(self) -> dict:
        """Fetch flights in radius (blocking)."""
        # Bounding Box berechnen (grob: 1° ≈ 111km)
        km_per_deg = 111.0
        delta_lat = self._radius / km_per_deg
        delta_lon = self._radius / (km_per_deg * abs(self._lat * 3.14159 / 180.0).__cos__() if self._lat != 0 else km_per_deg)

        # Fallback für cos-Berechnung
        import math
        delta_lon = self._radius / (km_per_deg * math.cos(math.radians(self._lat)))

        bounds = self._api.get_bounds_by_point(self._lat, self._lon, self._radius)
        flights_raw = self._api.get_flights(bounds=bounds)

        flights = []
        for flight in flights_raw:
            # Distanz berechnen
            dist = self._haversine(self._lat, self._lon, flight.latitude, flight.longitude)
            if dist > self._radius:
                continue

            # Flight Details holen
            try:
                details = self._api.get_flight_details(flight)
                flight.set_flight_details(details)
            except Exception:
                pass

            # Zeiten
            dep_time = None
            arr_time = None
            if flight.time_details:
                dep_ts = flight.time_details.get("real", {}).get("departure") or flight.time_details.get("scheduled", {}).get("departure")
                arr_ts = flight.time_details.get("estimated", {}).get("arrival") or flight.time_details.get("scheduled", {}).get("arrival")
                if dep_ts:
                    dep_time = datetime.fromtimestamp(dep_ts, tz=timezone.utc).strftime("%H:%M")
                if arr_ts:
                    arr_time = datetime.fromtimestamp(arr_ts, tz=timezone.utc).strftime("%H:%M")

            flights.append({
                "flight_number": flight.callsign or flight.id,
                "airline": getattr(flight, "airline_short_name", "") or getattr(flight, "airline_name", "") or "",
                "aircraft_type": getattr(flight, "aircraft_model", "") or getattr(flight, "aircraft_code", "") or "",
                "registration": getattr(flight, "registration", "") or "",
                "origin_airport": getattr(flight, "origin_airport_name", "") or getattr(flight, "origin_airport_iata", "") or "",
                "origin_iata": getattr(flight, "origin_airport_iata", "") or "",
                "destination_airport": getattr(flight, "destination_airport_name", "") or getattr(flight, "destination_airport_iata", "") or "",
                "destination_iata": getattr(flight, "destination_airport_iata", "") or "",
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "altitude": flight.altitude,
                "speed": flight.ground_speed,
                "heading": flight.heading,
                "distance_km": round(dist, 1),
                "latitude": flight.latitude,
                "longitude": flight.longitude,
            })

        # Nach Distanz sortieren
        flights.sort(key=lambda f: f["distance_km"])

        return {
            "flights": flights,
            "count": len(flights),
            "last_update": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        """Berechne Distanz in km zwischen zwei Koordinaten."""
        import math
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
