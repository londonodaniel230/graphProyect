// Custom error class for API request failures.
// Stores array of error messages from the server.
export class ApiError extends Error {
  constructor(messages) {
    super("API Error");
    this.messages = messages;
  }
}

// HTTP client for communicating with the backend API.
// Handles file uploads, geocoding requests, and route optimization queries.
export class ApiClient {
  // Sends a graph file to the server for validation and loading.
  async uploadGraph(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/graph", {
      method: "POST",
      body: formData,
    });

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const messages = data && data.errors ? data.errors : ["Unknown server error."];
      throw new ApiError(messages);
    }

    return data;
  }

  // Queries the backend geocoding service to find coordinates for a location.
  async geocode(query) {
    const url = `/api/geocode?query=${encodeURIComponent(query)}`;
    const response = await fetch(url);

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const messages = data && data.errors ? data.errors : ["Geocoding error."];
      throw new ApiError(messages);
    }

    return data && data.results ? data.results : [];
  }

  // Requests route optimization from the backend with specified criteria.
  async optimizeRoute(payload) {
    const response = await fetch("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const messages = data && data.errors ? data.errors : ["Unknown server error."];
      throw new ApiError(messages);
    }

    return data;
  }

  // Initializes an interactive trip session with origin and budget.
  async startTrip(payload) {
    const response = await fetch("/api/trip/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const messages = data && data.errors ? data.errors : ["Unknown server error."];
      throw new ApiError(messages);
    }

    return data;
  }

  // Sends a traveler action (activity, job, flight, etc.) to the current trip session.
  async tripAction(payload) {
    const response = await fetch("/api/trip/act", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let data = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      data = await response.json();
    }

    if (!response.ok) {
      const messages = data && data.errors ? data.errors : ["Unknown server error."];
      throw new ApiError(messages);
    }

    return data;
  }

  // Initiates a flight from the current node to a destination.
  async iniciarVuelo(payload) {
    const response = await fetch("/api/trip/act", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, action: "iniciar_vuelo" }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || [data.error || "Error al iniciar vuelo."]);
    }
    return data;
  }

  // Advances flight simulation by a time delta; updates progress and position.
  async avanzarVuelo(payload) {
    const response = await fetch("/api/trip/act", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, action: "avanzar_vuelo" }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error al avanzar vuelo."]);
    }
    return data;
  }

  // Checks if the current flight segment is blocked by a real-time route blocker.
  async verificarBloqueo(payload) {
    const response = await fetch("/api/trip/act", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, action: "verificar_bloqueo" }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error al verificar bloqueo."]);
    }
    return data;
  }

  // Cancels an ongoing flight and returns traveler to the origin node.
  async cancelarVuelo(payload) {
    const response = await fetch("/api/trip/act", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, action: "cancelar_vuelo" }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error al cancelar vuelo."]);
    }
    return data;
  }

  // Blocks a route between two nodes to simulate traffic or closures.
  async blockRoute(payload) {
    const response = await fetch("/api/route/block", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error blocking route."]);
    }
    return data;
  }

  // Unblocks a previously blocked route, restoring travel capability.
  async unblockRoute(payload) {
    const response = await fetch("/api/route/unblock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error unblocking route."]);
    }
    return data;
  }

  async getBlockedRoutes() {
    const response = await fetch("/api/route/blocked");
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error fetching blocked routes."]);
    }
    return data.blocked || [];
  }

  async autoPlan(payload) {
    const response = await fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.errors || ["Error planning routes."]);
    }
    return data;
  }
}
