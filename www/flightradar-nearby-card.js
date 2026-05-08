class FlightradarNearbyCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    if (!config.entity) throw new Error("'entity' muss angegeben werden");
    this._config = {
      entity: config.entity,
      max_flights: config.max_flights || 3,
      title: config.title || "✈️ Flüge in der Nähe",
      show_map: config.show_map !== false,
    };
  }

  _render() {
    if (!this._hass || !this._config) return;

    const entity = this._hass.states[this._config.entity];
    if (!entity) {
      this.innerHTML = "";
      return;
    }

    const flights = (entity.attributes.flights || []).slice(0, this._config.max_flights);

    // Nichts anzeigen wenn keine Flüge
    if (flights.length === 0) {
      this.innerHTML = "";
      return;
    }

    this.innerHTML = `
      <ha-card>
        <style>
          .fr-card { padding: 12px; }
          .fr-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: var(--primary-text-color); }
          .fr-flight { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 10px; padding: 10px; margin-bottom: 8px; }
          .fr-flight:last-child { margin-bottom: 0; }
          .fr-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
          .fr-flightnr { font-weight: 700; font-size: 14px; color: var(--accent-color); }
          .fr-dist { font-size: 11px; color: var(--secondary-text-color); }
          .fr-airline { font-size: 11px; color: var(--secondary-text-color); margin-bottom: 6px; }
          .fr-route { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
          .fr-apt { text-align: center; flex: 1; }
          .fr-iata { font-weight: 700; font-size: 13px; }
          .fr-name { font-size: 9px; color: var(--secondary-text-color); }
          .fr-time { font-size: 10px; color: var(--accent-color); margin-top: 2px; }
          .fr-arrow { color: var(--secondary-text-color); font-size: 14px; }
          .fr-meta { display: flex; gap: 8px; font-size: 10px; color: var(--secondary-text-color); padding-top: 6px; border-top: 1px solid var(--divider-color); flex-wrap: wrap; }
          .fr-minimap { width: 100%; height: 80px; border-radius: 8px; margin-top: 6px; overflow: hidden; position: relative; background: var(--secondary-background-color); }
          .fr-minimap-plane { position: absolute; font-size: 16px; }
          .fr-minimap-home { position: absolute; font-size: 14px; }
        </style>
        <div class="fr-card">
          <div class="fr-title">${this._config.title}</div>
          ${flights.map(f => this._renderFlight(f)).join("")}
        </div>
      </ha-card>
    `;
  }

  _renderFlight(f) {
    const mapHtml = this._config.show_map ? this._renderMiniMap(f) : "";
    return `
      <div class="fr-flight">
        <div class="fr-header">
          <span class="fr-flightnr">${f.flight_number}</span>
          <span class="fr-dist">${f.distance_km} km</span>
        </div>
        <div class="fr-airline">${f.airline} · ${f.aircraft_type}${f.registration ? " · " + f.registration : ""}</div>
        <div class="fr-route">
          <div class="fr-apt">
            <div class="fr-iata">${f.origin_iata || "?"}</div>
            <div class="fr-name">${f.origin_airport || ""}</div>
            <div class="fr-time">↑ ${f.departure_time || "?"}</div>
          </div>
          <div class="fr-arrow">✈ →</div>
          <div class="fr-apt">
            <div class="fr-iata">${f.destination_iata || "?"}</div>
            <div class="fr-name">${f.destination_airport || ""}</div>
            <div class="fr-time">↓ ${f.arrival_time || "?"}</div>
          </div>
        </div>
        <div class="fr-meta">
          <span>⬆️ ${f.altitude} ft</span>
          <span>💨 ${f.speed} kts</span>
          <span>🧭 ${f.heading}°</span>
        </div>
        ${mapHtml}
      </div>
    `;
  }

  _renderMiniMap(f) {
    const entity = this._hass.states[this._config.entity];
    const radius = entity.attributes.radius_km || 50;
    const homeLat = this._hass.config.latitude;
    const homeLon = this._hass.config.longitude;

    const scale = 80 / (radius * 2);
    const dx = (f.longitude - homeLon) * 111 * Math.cos(homeLat * Math.PI / 180);
    const dy = (f.latitude - homeLat) * 111;

    const centerX = 50;
    const centerY = 50;
    const planeX = Math.max(5, Math.min(95, centerX + dx * scale));
    const planeY = Math.max(5, Math.min(95, centerY - dy * scale));

    return `
      <div class="fr-minimap">
        <span class="fr-minimap-home" style="left:calc(${centerX}% - 7px); top:calc(${centerY}% - 7px);">🏠</span>
        <span class="fr-minimap-plane" style="left:calc(${planeX}% - 8px); top:calc(${planeY}% - 8px); transform:rotate(${f.heading}deg);">✈️</span>
      </div>
    `;
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement("flightradar-nearby-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "sensor.flightradar_fluge",
      max_flights: 3,
      title: "✈️ Flüge in der Nähe",
      show_map: true,
    };
  }
}

class FlightradarNearbyCardEditor extends HTMLElement {
  set hass(hass) { this._hass = hass; }

  setConfig(config) {
    this._config = config;
    this._render();
  }

  _render() {
    this.innerHTML = `
      <div style="padding: 16px;">
        <ha-textfield label="Entity" value="${this._config.entity || ""}" configValue="entity"></ha-textfield>
        <ha-textfield label="Max. Flüge anzeigen" type="number" value="${this._config.max_flights || 3}" configValue="max_flights"></ha-textfield>
        <ha-textfield label="Titel" value="${this._config.title || ""}" configValue="title"></ha-textfield>
        <ha-formfield label="Mini-Karte anzeigen">
          <ha-switch ${this._config.show_map !== false ? "checked" : ""} configValue="show_map"></ha-switch>
        </ha-formfield>
      </div>
    `;
    this.querySelectorAll("[configValue]").forEach(el => {
      el.addEventListener("change", (ev) => {
        const key = ev.target.getAttribute("configValue");
        let val = ev.target.value;
        if (key === "max_flights") val = parseInt(val);
        if (key === "show_map") val = ev.target.checked;
        this._config = { ...this._config, [key]: val };
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config } }));
      });
    });
  }
}

customElements.define("flightradar-nearby-card", FlightradarNearbyCard);
customElements.define("flightradar-nearby-card-editor", FlightradarNearbyCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "flightradar-nearby-card",
  name: "Flightradar Nearby",
  description: "Zeigt Flüge in der Nähe mit Details und Mini-Karte",
  preview: true,
});
