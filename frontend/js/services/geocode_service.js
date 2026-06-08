// Wrapper around ApiClient.geocode() for location lookups.
// Trims input and handles empty queries.
export class GeocodeService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  // Queries the backend for locations matching the search term.
  async geocode(query) {
    const term = (query || "").trim();
    if (!term) {
      return [];
    }

    return this.apiClient.geocode(term);
  }
}
