from typing import Dict, List, Optional, Set, Tuple


# Manages a set of blocked (prohibited) routes in real-time.
# Allows dynamically blocking/unblocking routes and filtering edges based on blocked status.
class RouteBlocker:
    def __init__(self):
        self._blocked: Set[Tuple[str, str]] = set()

    # Marks a route (origen -> destino) as blocked.
    def block(self, origen: str, destino: str) -> None:
        self._blocked.add((origen, destino))

    # Removes a route from the blocked list.
    def unblock(self, origen: str, destino: str) -> None:
        self._blocked.discard((origen, destino))

    # Returns True if the specified route is currently blocked.
    def is_blocked(self, origen: str, destino: str) -> bool:
        return (origen, destino) in self._blocked

    # Returns all blocked routes as a list of {origen, destino} dictionaries.
    def get_blocked(self) -> List[Dict[str, str]]:
        return [
            {"origen": o, "destino": d}
            for o, d in sorted(self._blocked)
        ]

    # Filters edges by removing those marked as blocked.
    def filter_edges(self, aristas: list) -> list:
        return [
            e for e in aristas
            if not self.is_blocked(e.origen, e.destino)
        ]

    def unblock_all(self) -> None:
        self._blocked.clear()


# Singleton compartido para que el TripService pueda consultarlo
_singleton: Optional["RouteBlocker"] = None


def get_route_blocker() -> "RouteBlocker":
    global _singleton
    if _singleton is None:
        _singleton = RouteBlocker()
    return _singleton
