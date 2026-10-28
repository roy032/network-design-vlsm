"""A small control-plane simulator used to verify a design before it is built.

It builds each router's routing table the way IOS would for this subset of
features (connected routes, static routes, single-area OSPF with passive
interfaces and redistribution, administrative distance, longest prefix match)
and then traces packets hop by hop. That is enough to prove every subnet can
reach every other one, and to catch black holes and routing loops in CI
instead of in Packet Tracer.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from ipaddress import IPv4Address, IPv4Network

from vlsmkit.spec import Network, Router

__all__ = [
    "Outcome",
    "Route",
    "Trace",
    "build_routing_tables",
    "ping",
    "reachability_matrix",
    "trace",
]

ADMIN_DISTANCE = {"C": 0, "S": 1, "O": 110, "O E2": 110}
MAX_HOPS = 30


@dataclass(frozen=True, slots=True)
class Route:
    prefix: IPv4Network
    source: str  # "C", "S", "O" or "O E2", as in `show ip route`
    next_hop: IPv4Address | None  # None for directly connected

    def __str__(self) -> str:
        via = "directly connected" if self.next_hop is None else f"via {self.next_hop}"
        return f"{self.source:<4} {self.prefix} {via}"


class Outcome(StrEnum):
    DELIVERED = "delivered"
    NO_ROUTE = "no route"
    LOOP = "routing loop"
    BAD_NEXT_HOP = "next hop unreachable"


@dataclass(frozen=True, slots=True)
class Trace:
    destination: IPv4Address
    hops: tuple[str, ...]
    outcome: Outcome

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.DELIVERED

    def __str__(self) -> str:
        return f"{' -> '.join(self.hops)} => {self.destination}: {self.outcome.value}"


def _ospf_interfaces(router: Router) -> list[tuple[str, IPv4Network]]:
    if router.ospf is None:
        return []
    return [
        (i.name, i.address.network)
        for i in router.interfaces
        if any(i.address.ip in n for n in router.ospf.networks)
    ]


def _adjacencies(network: Network) -> dict[str, list[tuple[str, IPv4Address]]]:
    """OSPF neighbours of each router, with the neighbour's address."""
    active: dict[str, dict[IPv4Network, IPv4Address]] = {}
    for r in network.routers:
        passive = set(r.ospf.passive) if r.ospf else set()
        active[r.hostname] = {
            net: r.interface(name).address.ip
            for name, net in _ospf_interfaces(r)
            if name not in passive
        }
    adj: dict[str, list[tuple[str, IPv4Address]]] = {r.hostname: [] for r in network.routers}
    for a, nets_a in active.items():
        for b, nets_b in active.items():
            if a != b:
                adj[a] += [(b, nets_b[n]) for n in nets_a.keys() & nets_b.keys()]
    return adj


def _advertised(router: Router) -> list[tuple[IPv4Network, str]]:
    """Prefixes ``router`` injects into OSPF, tagged intra-area or external."""
    if router.ospf is None:
        return []
    ads = [(net, "O") for _, net in _ospf_interfaces(router)]
    if "static" in router.ospf.redistribute:
        ads += [(s.destination, "O E2") for s in router.static_routes]
    if "connected" in router.ospf.redistribute:
        ospf_nets = {net for _, net in _ospf_interfaces(router)}
        ads += [
            (i.address.network, "O E2")
            for i in router.interfaces
            if i.address.network not in ospf_nets
        ]
    return ads


def build_routing_tables(network: Network) -> dict[str, list[Route]]:
    """Compute every router's routing table (best route per prefix)."""
    adj = _adjacencies(network)
    candidates: dict[str, list[Route]] = {r.hostname: [] for r in network.routers}

    for r in network.routers:
        connected = [i.address.network for i in r.interfaces]
        candidates[r.hostname] += [Route(n, "C", None) for n in connected]
        candidates[r.hostname] += [
            Route(s.destination, "S", s.next_hop)
            for s in r.static_routes
            if any(s.next_hop in n for n in connected)  # IOS drops unresolvable statics
        ]

    # OSPF: uniform link cost, so a BFS gives shortest paths; remember the
    # first hop's address as the next hop.
    for r in network.routers:
        if r.ospf is None:
            continue
        first_hop: dict[str, IPv4Address] = {}
        queue: deque[str] = deque()
        for neighbour, address in adj[r.hostname]:
            if neighbour not in first_hop:
                first_hop[neighbour] = address
                queue.append(neighbour)
        while queue:
            current = queue.popleft()
            for neighbour, _ in adj[current]:
                if neighbour != r.hostname and neighbour not in first_hop:
                    first_hop[neighbour] = first_hop[current]
                    queue.append(neighbour)
        for other, next_hop in first_hop.items():
            for prefix, kind in _advertised(network.router(other)):
                candidates[r.hostname].append(Route(prefix, kind, next_hop))

    tables: dict[str, list[Route]] = {}
    for hostname, routes in candidates.items():
        best: dict[IPv4Network, Route] = {}
        for route in routes:
            incumbent = best.get(route.prefix)
            if incumbent is None or (
                ADMIN_DISTANCE[route.source] < ADMIN_DISTANCE[incumbent.source]
            ):
                best[route.prefix] = route
        tables[hostname] = sorted(best.values(), key=lambda x: x.prefix)
    return tables


def _owner_of(network: Network, address: IPv4Address) -> Router | None:
    for r in network.routers:
        if any(i.address.ip == address for i in r.interfaces):
            return r
    return None


def trace(
    network: Network,
    source_router: str,
    destination: IPv4Address,
    tables: dict[str, list[Route]] | None = None,
) -> Trace:
    """Follow a packet from ``source_router`` towards ``destination``."""
    tables = tables if tables is not None else build_routing_tables(network)
    hops: list[str] = []
    current = network.router(source_router)
    while True:
        if current.hostname in hops or len(hops) >= MAX_HOPS:
            return Trace(destination, (*hops, current.hostname), Outcome.LOOP)
        hops.append(current.hostname)
        matches = [r for r in tables[current.hostname] if destination in r.prefix]
        if not matches:
            return Trace(destination, tuple(hops), Outcome.NO_ROUTE)
        route = max(matches, key=lambda r: r.prefix.prefixlen)
        if route.next_hop is None:
            return Trace(destination, tuple(hops), Outcome.DELIVERED)
        nxt = _owner_of(network, route.next_hop)
        if nxt is None:
            return Trace(destination, tuple(hops), Outcome.BAD_NEXT_HOP)
        current = nxt


def _attached_router(network: Network, address: IPv4Address) -> str:
    owner = _owner_of(network, address)
    if owner is not None:
        return owner.hostname
    for h in network.hosts:
        if h.address == address:
            gateway = _owner_of(network, h.gateway)
            if gateway is not None:
                return gateway.hostname
    for r in network.routers:
        if any(address in i.address.network for i in r.interfaces):
            return r.hostname
    raise LookupError(f"{address} is not attached to any router")


def ping(
    network: Network,
    source: IPv4Address,
    destination: IPv4Address,
    tables: dict[str, list[Route]] | None = None,
) -> tuple[Trace, Trace]:
    """Trace the echo request and the echo reply. Both must succeed."""
    tables = tables if tables is not None else build_routing_tables(network)
    request = trace(network, _attached_router(network, source), destination, tables)
    reply = trace(network, _attached_router(network, destination), source, tables)
    return request, reply


def _probe(network: Network, subnet: IPv4Network) -> IPv4Address:
    """The lowest assigned address in ``subnet`` (usually its gateway)."""
    assigned = [i.address.ip for r in network.routers for i in r.interfaces]
    assigned += [h.address for h in network.hosts]
    return min(a for a in assigned if a in subnet)


def reachability_matrix(
    network: Network,
) -> dict[tuple[str, str], tuple[Trace, Trace]]:
    """Ping from every subnet to every other subnet, keyed by subnet id."""
    tables = build_routing_tables(network)
    probes = {s.id: _probe(network, s.network) for s in network.subnets}
    return {
        (a, b): ping(network, probes[a], probes[b], tables)
        for a in probes
        for b in probes
        if a != b
    }
