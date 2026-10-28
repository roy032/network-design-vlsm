from __future__ import annotations

from ipaddress import IPv4Address, IPv4Network
from typing import Any

import pytest

from vlsmkit.routing import (
    Outcome,
    build_routing_tables,
    ping,
    reachability_matrix,
    trace,
)
from vlsmkit.spec import Network, parse


def test_every_lan_reaches_every_lan(network: Network) -> None:
    lans = {s.id for s in network.lans}
    matrix = reachability_matrix(network)
    failures = [
        (a, b)
        for (a, b), (req, rep) in matrix.items()
        if a in lans and b in lans and not (req.ok and rep.ok)
    ]
    assert failures == []


def test_routing_table_sources(network: Network) -> None:
    tables = build_routing_tables(network)
    cat = {str(r.prefix): r for r in tables["R-Cat"]}
    assert cat["10.0.8.0/22"].source == "C"
    assert cat["10.0.0.0/21"].source == "O"
    assert cat["10.0.12.128/28"].source == "O E2"  # Lion LAN via redistribution
    assert cat["10.0.12.128/28"].next_hop == IPv4Address("10.0.12.149")
    lion = {str(r.prefix): r for r in tables["R-Lion"]}
    assert all(r.source in {"C", "S"} for r in lion.values())


def test_trace_dog_to_web_server(network: Network) -> None:
    result = trace(network, "R-Dog", IPv4Address("10.0.12.130"))
    assert result.ok
    assert result.hops == ("R-Dog", "R-Elephant", "R-Lion")
    assert "delivered" in str(result)


def test_ping_dhcp_server_from_cat_chief(network: Network) -> None:
    request, reply = ping(network, IPv4Address("10.0.8.2"), IPv4Address("10.0.12.133"))
    assert request.ok
    assert reply.ok


def test_every_subnet_reaches_every_subnet(network: Network) -> None:
    """Includes router link addresses, e.g. the Lion-Elephant /30."""
    assert all(req.ok and rep.ok for req, rep in reachability_matrix(network).values())


def test_lion_link_needs_connected_redistribution(raw_spec: dict[str, Any]) -> None:
    """Regression: without it, 10.0.12.144/30 is unknown to Cat and Dog."""
    raw_spec["routers"][1]["ospf"]["redistribute"] = ["static"]
    gap = parse(raw_spec)
    request, _ = ping(gap, IPv4Address("10.0.0.2"), IPv4Address("10.0.12.145"))
    assert request.outcome is Outcome.NO_ROUTE


def test_missing_redistribution_breaks_lion(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][1]["ospf"]["redistribute"] = []
    broken = parse(raw_spec)
    request, reply = ping(broken, IPv4Address("10.0.8.2"), IPv4Address("10.0.12.130"))
    assert request.outcome is Outcome.NO_ROUTE
    assert reply.ok  # R-Lion still has a static route back


def test_passive_link_drops_adjacency(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][2]["ospf"]["passive"] = ["GigabitEthernet0/0"]
    broken = parse(raw_spec)
    cat = {r.prefix for r in build_routing_tables(broken)["R-Cat"]}
    assert IPv4Network("10.0.0.0/21") not in cat


def test_routing_loop_detected(raw_spec: dict[str, Any]) -> None:
    # R-Elephant sends the Lion LAN back to... itself via R-Cat, and R-Cat
    # (static beats OSPF) points it back at R-Elephant.
    raw_spec["routers"][1]["static_routes"] = [{"to": "lion-lan", "via": "R-Cat"}]
    raw_spec["routers"][1]["ospf"]["redistribute"] = []
    raw_spec["routers"][2]["static_routes"] = [{"to": "lion-lan", "via": "R-Elephant"}]
    looped = parse(raw_spec)
    result = trace(looped, "R-Dog", IPv4Address("10.0.12.130"))
    assert result.outcome is Outcome.NO_ROUTE  # R-Dog never learns it
    result = trace(looped, "R-Cat", IPv4Address("10.0.12.130"))
    assert result.outcome is Outcome.LOOP


def test_unattached_address_raises(network: Network) -> None:
    with pytest.raises(LookupError):
        ping(network, IPv4Address("192.0.2.1"), IPv4Address("10.0.0.2"))


def test_dhcp_client_address_resolves_to_lan_router(network: Network) -> None:
    request, reply = ping(network, IPv4Address("10.0.0.77"), IPv4Address("10.0.12.2"))
    assert request.hops[0] == "R-Dog"
    assert request.ok
    assert reply.ok
