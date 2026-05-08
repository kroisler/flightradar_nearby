"""Sensor platform for Flightradar Nearby."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .coordinator import FlightradarCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors from a config entry."""
    config = entry.data
    scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = FlightradarCoordinator(hass, config, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        FlightradarCountSensor(coordinator, entry),
        FlightradarFlightsSensor(coordinator, entry),
    ])


class FlightradarCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor: Anzahl Flüge im Umkreis."""

    def __init__(self, coordinator: FlightradarCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_count"
        self._attr_name = "Flüge in der Nähe"
        self._attr_icon = "mdi:airplane"
        self._attr_native_unit_of_measurement = "Flüge"

    @property
    def native_value(self):
        """Return flight count."""
        if self.coordinator.data:
            return self.coordinator.data.get("count", 0)
        return 0

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}
        return {
            "last_update": self.coordinator.data.get("last_update"),
            "radius_km": self._entry.data.get("radius"),
        }


class FlightradarFlightsSensor(CoordinatorEntity, SensorEntity):
    """Sensor: Flugdetails als Attribut-Liste."""

    def __init__(self, coordinator: FlightradarCoordinator, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_flights"
        self._attr_name = "Flightradar Flüge"
        self._attr_icon = "mdi:radar"

    @property
    def native_value(self):
        """Return flight count as state."""
        if self.coordinator.data:
            return self.coordinator.data.get("count", 0)
        return 0

    @property
    def extra_state_attributes(self):
        """Return all flights as attributes."""
        if not self.coordinator.data:
            return {"flights": []}

        flights = self.coordinator.data.get("flights", [])
        return {
            "flights": flights,
            "last_update": self.coordinator.data.get("last_update"),
            "radius_km": self._entry.data.get("radius"),
            # Nächster Flug als Top-Level Attribute
            "nearest_flight": flights[0].get("flight_number") if flights else None,
            "nearest_airline": flights[0].get("airline") if flights else None,
            "nearest_origin": flights[0].get("origin_airport") if flights else None,
            "nearest_destination": flights[0].get("destination_airport") if flights else None,
            "nearest_distance_km": flights[0].get("distance_km") if flights else None,
            "nearest_altitude": flights[0].get("altitude") if flights else None,
        }
