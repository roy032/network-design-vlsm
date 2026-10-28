from __future__ import annotations

from ipaddress import IPv4Address, IPv4Network
from typing import Any

import pytest

from vlsmkit.spec import Network, SpecError, parse


def test_spec_resolves_addresses(network: Network) -> None:
    lion = network.router("R-Lion")
    assert lion.interface("GigabitEthernet0/0/0").address.ip == IPv4Address("10.0.12.145")
    elephant = network.router("R-Elephant")
    assert elephant.interface("GigabitEthernet0/0").dhcp_relay == IPv4Address("10.0.12.133")
    assert network.host("DNS-Server").address == IPv4Address("10.0.12.131")
    assert network.host("DogChief-PC").gateway == IPv4Address("10.0.0.1")


def test_static_routes_resolve_neighbour_address(network: Network) -> None:
    routes = network.router("R-Lion").static_routes
    assert {r.next_hop for r in routes} == {IPv4Address("10.0.12.146")}
    assert IPv4Network("10.0.0.0/21") in {r.destination for r in routes}


def test_subnets_sorted_by_address_and_lans(network: Network) -> None:
    nets = [s.network for s in network.subnets]
    assert nets == sorted(nets)
    assert {s.id for s in network.lans} == {"dog-lan", "cat-lan", "elephant-lan", "lion-lan"}


def test_dhcp_ranges(network: Network) -> None:
    assert network.subnet("cat-lan").dhcp_range == (
        IPv4Address("10.0.8.10"),
        IPv4Address("10.0.11.254"),
    )
    assert network.subnet("lion-lan").dhcp_range is None


def test_lookup_errors(network: Network) -> None:
    with pytest.raises(KeyError):
        network.subnet("nope")
    with pytest.raises(KeyError):
        network.router("nope")
    with pytest.raises(KeyError):
        network.host("nope")
    with pytest.raises(KeyError):
        network.router("R-Lion").interface("Gi9/9")


def _problems(raw: dict[str, Any]) -> list[str]:
    with pytest.raises(SpecError) as excinfo:
        parse(raw)
    problems: list[str] = excinfo.value.problems
    return problems


def test_duplicate_ip_detected(raw_spec: dict[str, Any]) -> None:
    raw_spec["hosts"][1]["host"] = raw_spec["hosts"][0]["host"]
    assert any("assigned to both" in p for p in _problems(raw_spec))


def test_unknown_subnet_detected(raw_spec: dict[str, Any]) -> None:
    raw_spec["hosts"][0]["subnet"] = "atlantis"
    assert any("unknown subnet 'atlantis'" in p for p in _problems(raw_spec))


def test_host_index_out_of_range(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][0]["interfaces"][0]["host"] = 3  # a /30 has only 2 hosts
    assert any("outside 1..2" in p for p in _problems(raw_spec))


def test_static_route_without_shared_link(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][0]["static_routes"][0]["via"] = "R-Cat"
    assert any("share no subnet" in p for p in _problems(raw_spec))


def test_unknown_next_hop_router(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][0]["static_routes"][0]["via"] = "R-Unicorn"
    assert any("unknown next-hop router" in p for p in _problems(raw_spec))


def test_bad_ospf_options(raw_spec: dict[str, Any]) -> None:
    ospf = raw_spec["routers"][1]["ospf"]
    ospf["passive"] = ["Gi9/9"]
    ospf["redistribute"] = ["bgp"]
    problems = _problems(raw_spec)
    assert any("passive interface Gi9/9" in p for p in problems)
    assert any("cannot redistribute 'bgp'" in p for p in problems)


def test_static_host_inside_dhcp_pool(raw_spec: dict[str, Any]) -> None:
    chief = next(h for h in raw_spec["hosts"] if h["name"] == "CatChief-PC")
    chief["host"] = 50
    assert any("inside the DHCP pool" in p for p in _problems(raw_spec))


def test_unknown_dhcp_relay(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][2]["interfaces"][1]["dhcp_relay"] = "Nobody"
    assert any("unknown DHCP relay" in p for p in _problems(raw_spec))


def test_gateway_must_be_a_router(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][2]["interfaces"][1]["host"] = 3  # R-Cat LAN no longer .1
    assert any("no router interface owns gateway" in p for p in _problems(raw_spec))


def test_duplicate_router_and_interface(raw_spec: dict[str, Any]) -> None:
    raw_spec["routers"][3]["hostname"] = "R-Cat"
    raw_spec["routers"][0]["interfaces"][1]["name"] = "GigabitEthernet0/0/0"
    problems = _problems(raw_spec)
    assert any("duplicate router hostname R-Cat" in p for p in problems)
    assert any("interface defined twice" in p for p in problems)


def test_dhcp_exclusion_too_large(raw_spec: dict[str, Any]) -> None:
    raw_spec["subnets"][2]["dhcp"]["exclude_first"] = 500
    assert any("DHCP exclusion" in p for p in _problems(raw_spec))


def test_all_problems_reported_together(raw_spec: dict[str, Any]) -> None:
    raw_spec["hosts"][0]["subnet"] = "atlantis"
    raw_spec["routers"][0]["static_routes"][0]["via"] = "R-Unicorn"
    assert len(_problems(raw_spec)) >= 2


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda r: r.pop("network"), "supernet"),
        (lambda r: r.__setitem__("subnets", []), "no [[subnets]]"),
        (lambda r: r["subnets"][0].__setitem__("hosts", 10**9), "subnets:"),
    ],
)
def test_fatal_spec_errors(raw_spec: dict[str, Any], mutate: Any, message: str) -> None:
    mutate(raw_spec)
    with pytest.raises(SpecError, match=message.replace("[", r"\[").replace("]", r"\]")):
        parse(raw_spec)
