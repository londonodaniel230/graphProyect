const DEFAULT_ZONE = "Etc/UTC";

// Factory for creating node objects from geocoding results or manual data.
// Handles coordinate parsing, zone defaults, and cost initialization.
export class NodeFactory {
  constructor(geocodeService, options = {}) {
    this.geocodeService = geocodeService;
    const defaultFood = Number(options.defaultFoodCost);
    this.defaultFoodCost = Number.isFinite(defaultFood) ? defaultFood : 0;
  }

  // Creates a node by geocoding a query string and applying overrides.
  async createFromQuery(query, overrides = {}) {
    const results = await this.geocodeService.geocode(query);
    if (!results.length) {
      throw new Error("No se encontraron coordenadas para el pais.");
    }

    return this.createFromGeocode(results[0], overrides);
  }

  // Converts geocoded location data into a node object with optional field overrides.
  createFromGeocode(geo, overrides = {}) {
    const address = (geo && geo.address) || {};
    const pais =
      overrides.pais || geo.name || address.country || overrides.nombre || "";
    const nombre = overrides.nombre || geo.displayName || pais || "Nodo";
    const ciudad =
      overrides.ciudad ||
      address.city ||
      address.town ||
      address.village ||
      address.county ||
      "";

    const zonaHoraria = overrides.zonaHoraria || DEFAULT_ZONE;
    const esHub = Boolean(overrides.esHub);
    const costoAlojamiento = toNumber(overrides.costoAlojamiento, 0);
    const costoAlimentacion = toNumber(
      overrides.costoAlimentacion,
      this.defaultFoodCost
    );
    const actividades = Array.isArray(overrides.actividades)
      ? overrides.actividades
      : [];
    const trabajos = Array.isArray(overrides.trabajos) ? overrides.trabajos : [];

    const lat = toNumber(geo.lat, null);
    const lon = toNumber(geo.lon, null);
    const id =
      overrides.id ||
      (geo.countryCode
        ? String(geo.countryCode).toUpperCase()
        : pais || nombre || "NODE");

    return {
      id,
      nombre,
      ciudad,
      pais,
      zonaHoraria,
      esHub,
      costoAlojamiento,
      costoAlimentacion,
      actividades,
      trabajos,
      lat,
      lon,
    };
  }
}

function toNumber(value, fallback) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}
