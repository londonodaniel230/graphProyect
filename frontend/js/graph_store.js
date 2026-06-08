// In-memory store for the loaded travel network graph.
// Provides access to nodes and edges, and supports searching by country/name.
export class GraphStore {
  constructor() {
    this.graph = null;
  }

  // Stores the complete graph data; makes defensive copies of arrays.
  setGraph(graph) {
    if (!graph) {
      this.graph = null;
      return;
    }

    this.graph = {
      ...graph,
      nodos: [...(graph.nodos || [])],
      aristas: [...(graph.aristas || [])],
    };
  }

  // Returns true if a graph has been loaded.
  hasGraph() {
    return Boolean(this.graph);
  }

  // Returns the full graph object.
  getGraph() {
    return this.graph;
  }

  // Searches for a single node matching the given country name.
  findNodeByCountry(country) {
    if (!this.graph) {
      return null;
    }

    const key = normalizeName(country);
    return (
      this.graph.nodos.find((node) => normalizeName(node.pais) === key) ||
      this.graph.nodos.find((node) => normalizeName(node.nombre) === key) ||
      this.graph.nodos.find((node) => normalizeName(node.id) === key) ||
      null
    );
  }

  // Returns all nodes matching the given country name.
  findNodesByCountry(country) {
    if (!this.graph) {
      return [];
    }

    const key = normalizeName(country);
    return this.graph.nodos.filter((node) => {
      return (
        normalizeName(node.pais) === key ||
        normalizeName(node.nombre) === key ||
        normalizeName(node.id) === key
      );
    });
  }

  // Adds or updates a node in the store.
  upsertNode(node) {
    if (!this.graph) {
      return;
    }

    const key = normalizeName(node.id);
    const index = this.graph.nodos.findIndex(
      (item) => normalizeName(item.id) === key
    );

    if (index >= 0) {
      this.graph.nodos[index] = node;
    } else {
      this.graph.nodos.push(node);
    }
  }

  // Adds a new edge between two nodes if it doesn't already exist.
  addRoute(originId, destinationId, route) {
    if (!this.graph) {
      throw new Error("No hay un grafo cargado.");
    }

    const exists = this.graph.aristas.some(
      (edge) =>
        normalizeName(edge.origen) === normalizeName(originId) &&
        normalizeName(edge.destino) === normalizeName(destinationId)
    );

    if (exists) {
      throw new Error("La ruta ya existe.");
    }

    const newEdge = {
      origen: originId,
      destino: destinationId,
      distanciaKm: route.distanciaKm,
      aeronaves: route.aeronaves,
      costoBase: route.costoBase,
      estanciaMinima: route.estanciaMinima,
    };

    this.graph = {
      ...this.graph,
      nodos: [...this.graph.nodos],
      aristas: [...this.graph.aristas, newEdge],
    };

    return this.graph;
  }
}

function normalizeName(value) {
  return (value || "").trim().toLowerCase();
}
