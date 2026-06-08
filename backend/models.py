# -*- coding: utf-8 -*-
"""
models.py
Backend data models.

Original classes (unmodified):
    Activity, Job, Node, Edge, AircraftConfig, GlobalConfig, Graph

Classes added by PERSON 1 – Route algorithms and logic:
    RouteStep   – details of an individual route segment.
    RouteResult – complete result returned by route algorithms.

Classes added for 2.3 – Advanced planning with dynamic management:
    TripDecision – a decision made during an interactive trip step.
    StepOptions  – options available to the traveler at a concrete step.
    TripState    – complete state of the interactive trip.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ===========================================================================
# Original models (DO NOT MODIFY)
# ===========================================================================

# Represents an optional activity (tour, museum, etc.) available at a destination node.
# Activities have a name, type, duration in minutes, and cost in USD.
@dataclass(frozen=True)
class Activity:
    nombre: str
    tipo: str
    duracion_min: int
    costo_usd: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre,
            "tipo": self.tipo,
            "duracionMin": self.duracion_min,
            "costoUSD": self.costo_usd,
        }


# Represents a temporary job opportunity available at a destination node.
# Jobs have a name, hourly rate in USD, and maximum hours that can be worked.
@dataclass(frozen=True)
class Job:
    nombre: str
    tarifa_hora: float
    max_horas: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre,
            "tarifaHora": self.tarifa_hora,
            "maxHoras": self.max_horas,
        }


# Represents a location/destination in the travel graph.
# Nodes contain geographic info, lodging/meal costs, available activities and jobs.
# Hubs are key distribution centers; lat/lon enable mapping and distance calculation.
@dataclass(frozen=True)
class Node:
    id: str
    nombre: str
    ciudad: str
    pais: str
    zona_horaria: str
    es_hub: bool
    costo_alojamiento: float
    costo_alimentacion: float
    actividades: List[Activity]
    trabajos: List[Job]
    lat: Optional[float] = None
    lon: Optional[float] = None

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "id": self.id,
            "nombre": self.nombre,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "zonaHoraria": self.zona_horaria,
            "esHub": self.es_hub,
            "costoAlojamiento": self.costo_alojamiento,
            "costoAlimentacion": self.costo_alimentacion,
            "actividades": [actividad.to_dict() for actividad in self.actividades],
            "trabajos": [trabajo.to_dict() for trabajo in self.trabajos],
        }

        if self.lat is not None:
            payload["lat"] = self.lat
        if self.lon is not None:
            payload["lon"] = self.lon

        return payload


# Represents a flight connection between two nodes.
# Edges specify distance, available aircraft types, base cost, and minimum stay duration.
@dataclass(frozen=True)
class Edge:
    origen: str
    destino: str
    distancia_km: float
    aeronaves: List[str]
    costo_base: float
    estancia_minima: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "origen": self.origen,
            "destino": self.destino,
            "distanciaKm": self.distancia_km,
            "aeronaves": self.aeronaves,
            "costoBase": self.costo_base,
            "estanciaMinima": self.estancia_minima,
        }


# Configuration parameters for a specific aircraft type (cost per km, time per km).
# Used to calculate flight costs and durations based on selected aircraft.
@dataclass(frozen=True)
class AircraftConfig:
    costo_km: float
    tiempo_km: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "costoKm": self.costo_km,
            "tiempoKm": self.tiempo_km,
        }


# Global system configuration containing all aircraft types and
# mandatory cost thresholds (minimum budget %, lodging interval, meal interval).
@dataclass(frozen=True)
class GlobalConfig:
    aeronaves: Dict[str, AircraftConfig]
    presupuesto_minimo_porc: float
    intervalo_alojamiento: float
    intervalo_alimentacion: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "aeronaves": {
                key: value.to_dict() for key, value in self.aeronaves.items()
            },
            "presupuestoMinimoPorc": self.presupuesto_minimo_porc,
            "intervaloAlojamiento": self.intervalo_alojamiento,
            "intervaloAlimentacion": self.intervalo_alimentacion,
        }


@dataclass(frozen=True)
# Represents the complete travel network: a collection of destinations (nodes),
# flight connections between them (edges), and system-wide configuration settings.
class Graph:
    nodos: List[Node]
    aristas: List[Edge]
    configuracion: Optional[GlobalConfig]

    def to_dict(self) -> Dict[str, object]:
        return {
            "nodos": [nodo.to_dict() for nodo in self.nodos],
            "aristas": [arista.to_dict() for arista in self.aristas],
            "configuracion": self.configuracion.to_dict() if self.configuracion else None,
        }


# ===========================================================================
# New models – PERSON 1 / Route algorithms and logic
# ===========================================================================

# Represents a single leg of a calculated route.
# Stores origin, destination, distance, cumulative distance, and aircraft used.
@dataclass
class RouteStep:
    """
    Represents an individual segment within a calculated route.

    Attributes
    ----------
    origen                : ID of the segment departure node.
    destino               : ID of the segment arrival node.
    distancia_km          : distance of this segment in kilometers.
    distancia_acumulada_km: total distance traveled until reaching ``destino``.
    aeronave              : type of aircraft available for the segment (may
                            be None if the edge does not specify any).
    """

    origen: str
    destino: str
    distancia_km: float
    distancia_acumulada_km: float
    aeronave: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "origen": self.origen,
            "destino": self.destino,
            "distanciaKm": self.distancia_km,
            "distanciaAcumuladaKm": self.distancia_acumulada_km,
            "aeronave": self.aeronave,
        }


# Complete result from a pathfinding algorithm.
# Contains the full path (if found), individual route steps, total distance/cost, and any errors.
@dataclass
class RouteResult:
    """
    Complete result returned by any route algorithm.

    Attributes
    ----------
    camino      : list of node IDs in visit order
                  (empty if no route was found).
    pasos       : list of RouteStep with details of each segment.
    total_km    : total distance of the route in km
                  (math.inf if no route was found).
    total_costo : total cost of the route (USD) if applicable.
    encontrado  : True if a valid route exists, False otherwise.
    error       : descriptive message when ``encontrado`` is False.
    """

    camino: List[str]
    pasos: List[RouteStep]
    total_km: float
    encontrado: bool
    total_costo: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        total_km = self.total_km if not math.isinf(self.total_km) else None
        total_costo = None
        if self.total_costo is not None and not math.isinf(self.total_costo):
            total_costo = self.total_costo

        return {
            "camino": self.camino,
            "pasos": [paso.to_dict() for paso in self.pasos],
            "totalKm": total_km,
            "totalCosto": total_costo,
            "encontrado": self.encontrado,
            "error": self.error,
        }


# ===========================================================================
# ADVANCED PLANNING models – 2.3
# ===========================================================================


@dataclass
class TripDecision:
    """Record of a decision made during the interactive trip."""

    tipo: str  # "vuelo", "alojamiento", "alimentacion", "actividad", "trabajo", "tiempo_libre", "fin"
    node_id: str
    detalle: Dict[str, Any]
    costo: float
    ingreso: float
    tiempo_invertido_horas: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.tipo,
            "nodeId": self.node_id,
            "detalle": self.detalle,
            "costo": self.costo,
            "ingreso": self.ingreso,
            "tiempoInvertidoHoras": self.tiempo_invertido_horas,
        }


# Represents all available options to the traveler at a specific step:
# current location, required actions (lodging/meals), optional activities, jobs, and available flights.
@dataclass
class StepOptions:
    """Options available to the traveler at a concrete step of the trip."""

    # Information of the current step
    node_id: str
    node_nombre: str
    node_ciudad: str
    node_pais: str

    # Estado actual del viaje
    presupuesto_actual: float
    presupuesto_inicial: float
    tiempo_transcurrido_horas: float
    total_gastado: float
    total_ganado: float
    destinos_visitados: List[str]
    puede_trabajar: bool  # True si presupuesto < 35% del inicial

    # Requerimientos obligatorios
    necesita_alojamiento: bool
    necesita_alimentacion: bool
    costo_alojamiento: float
    costo_alimentacion: float

    # Actividades opcionales disponibles en este nodo
    actividades_opcionales: List[Activity]

    # Trabajos disponibles en este nodo
    trabajos_disponibles: List[Job]

    # Vuelos disponibles desde este nodo
    vuelos_disponibles: List[Dict[str, Any]]

    # Viaje completado?
    viaje_completado: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeId": self.node_id,
            "nodeNombre": self.node_nombre,
            "nodeCiudad": self.node_ciudad,
            "nodePais": self.node_pais,
            "presupuestoActual": self.presupuesto_actual,
            "presupuestoInicial": self.presupuesto_inicial,
            "tiempoTranscurridoHoras": self.tiempo_transcurrido_horas,
            "totalGastado": self.total_gastado,
            "totalGanado": self.total_ganado,
            "destinosVisitados": self.destinos_visitados,
            "puedeTrabajar": self.puede_trabajar,
            "necesitaAlojamiento": self.necesita_alojamiento,
            "necesitaAlimentacion": self.necesita_alimentacion,
            "costoAlojamiento": self.costo_alojamiento,
            "costoAlimentacion": self.costo_alimentacion,
            "actividadesOpcionales": [a.to_dict() for a in self.actividades_opcionales],
            "trabajosDisponibles": [j.to_dict() for j in self.trabajos_disponibles],
            "vuelosDisponibles": self.vuelos_disponibles,
            "viajeCompletado": self.viaje_completado,
        }


# Final summary report of a completed interactive trip.
# Aggregates all decisions, final budget/earnings, time spent, and activity counts.
@dataclass
class TripReport:
    """Reporte final del viaje interactivo."""

    camino: List[str]
    decisiones: List[TripDecision]
    total_gastado: float
    total_ganado: float
    presupuesto_final: float
    tiempo_total_horas: float
    destinos_visitados: int
    vuelos_realizados: int
    actividades_realizadas: int
    trabajos_realizados: int
    alojamientos_pagados: int
    alimentos_consumidos: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camino": self.camino,
            "decisiones": [d.to_dict() for d in self.decisiones],
            "totalGastado": round(self.total_gastado, 2),
            "totalGanado": round(self.total_ganado, 2),
            "presupuestoFinal": round(self.presupuesto_final, 2),
            "tiempoTotalHoras": round(self.tiempo_total_horas, 2),
            "destinosVisitados": self.destinos_visitados,
            "vuelosRealizados": self.vuelos_realizados,
            "actividadesRealizadas": self.actividades_realizadas,
            "trabajosRealizados": self.trabajos_realizados,
            "alojamientosPagados": self.alojamientos_pagados,
            "alimentosConsumidos": self.alimentos_consumidos,
        }