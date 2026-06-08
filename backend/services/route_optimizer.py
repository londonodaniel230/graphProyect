# -*- coding: utf-8 -*-
"""
route_optimizer.py  –  PERSONA 1
Capa de servicio que expone la optimización de rutas al resto del backend.

Actúa como fachada sobre path_algorithms: valida entradas, selecciona el
algoritmo correcto y devuelve un RouteResult uniforme.

Modos soportados actualmente:
    "distancia"  →  dijkstra_por_distancia   (responsabilidad DANIEL)
    "costo"      →  dijkstra_por_costo       (responsabilidad TAiKK)
"""

from typing import Optional

from ..models import Graph, RouteResult
from .path_algorithms import (
    CostOptions,
    TraversalConstraints,
    bfs_mayor_destinos,
    bfs_mayor_destinos_libre,
    dijkstra_por_costo,
    dijkstra_por_distancia,
    dijkstra_por_tiempo,
)


# Mapping of optimization modes to their corresponding pathfinding algorithms.
# Supports multiple criteria: distance, cost, time, and number of destinations.
_ALGORITMOS = {
    "distancia": dijkstra_por_distancia,
    "costo": dijkstra_por_costo,
    "tiempo": dijkstra_por_tiempo,
    "destinos": bfs_mayor_destinos,
    "destinos_libre": bfs_mayor_destinos_libre,
}


# Filters the graph by removing edges that are marked as blocked.
# Returns a new Graph object with only the allowed edges.
def _filtrar_aristas_bloqueadas(graph: Graph, blocked: Optional[list] = None) -> Graph:
    if not blocked:
        return graph
    bloqueados = set()
    for item in blocked:
        o = (item.get("origen") or "").strip()
        d = (item.get("destino") or "").strip()
        if o and d:
            bloqueados.add((o, d))
    if not bloqueados:
        return graph
    nuevas_aristas = [
        e for e in graph.aristas
        if (e.origen, e.destino) not in bloqueados
    ]
    return Graph(
        nodos=list(graph.nodos),
        aristas=nuevas_aristas,
        configuracion=graph.configuracion,
    )


def optimizar_ruta(
    graph: Graph,
    inicio_id: str,
    destino_id: str,
    modo: str = "distancia",
    presupuesto_total: Optional[float] = None,
    opciones: Optional[CostOptions] = None,
    inicio_ids: Optional[list] = None,
    destino_ids: Optional[list] = None,
    restricciones: Optional[TraversalConstraints] = None,
    rutas_bloqueadas: Optional[list] = None,
) -> RouteResult:
    """
    Calcula la ruta óptima entre dos nodos según el modo indicado.

    Parámetros
    ----------
    graph      : Graph  – grafo validado (devuelto por GraphLoader).
    inicio_id  : str    – ID del nodo origen.
    destino_id : str    – ID del nodo destino.
    modo       : str    – criterio de optimización.
                         Valores aceptados: "distancia", "costo", "tiempo"
                         (extensible: …).
    presupuesto_total : float | None – presupuesto maximo (USD) para el modo
                         "costo". Si es None, no se valida presupuesto.
    opciones  : CostOptions | None – opciones de costo (aeronaves, alimentacion,
                alojamiento, trabajo).
    inicio_ids : list | None – lista de IDs de origen (opcional).
    destino_ids: list | None – lista de IDs de destino (opcional).
    restricciones: TraversalConstraints | None – restricciones para busquedas
                   no optimas (presupuesto/tiempo/excluir secundarios).

    Retorna
    -------
    RouteResult – siempre se devuelve un objeto; si hay error, el campo
    ``encontrado`` será False y ``error`` contendrá la descripción.
    """
    graph = _filtrar_aristas_bloqueadas(graph, rutas_bloqueadas)

    modo_normalizado = modo.strip().lower()

    if modo_normalizado not in _ALGORITMOS:
        modos_disponibles = ", ".join(sorted(_ALGORITMOS.keys()))
        return RouteResult(
            camino=[],
            pasos=[],
            total_km=float("inf"),
            encontrado=False,
            error=(
                f"Modo '{modo}' no reconocido. "
                f"Modos disponibles: {modos_disponibles}."
            ),
        )

    algoritmo = _ALGORITMOS[modo_normalizado]
    if modo_normalizado == "costo":
        return algoritmo(
            graph,
            inicio_id,
            destino_id,
            presupuesto_total=presupuesto_total,
            opciones=opciones,
            inicio_ids=inicio_ids,
            destino_ids=destino_ids,
        )
    elif modo_normalizado == "tiempo":
        return algoritmo(
            graph,
            inicio_id,
            destino_id,
            opciones=opciones,
            inicio_ids=inicio_ids,
            destino_ids=destino_ids,
        )
    elif modo_normalizado in ("destinos", "destinos_libre"):
        return algoritmo(
            graph,
            inicio_id,
            destino_id,
            opciones=opciones,
            restricciones=restricciones,
            inicio_ids=inicio_ids,
            destino_ids=destino_ids,
        )
    return algoritmo(graph, inicio_id, destino_id)


def modos_disponibles() -> list:
    """Returns the list of registered optimization modes."""
    return sorted(_ALGORITMOS.keys())