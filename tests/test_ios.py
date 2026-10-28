"""The generated configs must be equivalent to the as-built Packet Tracer configs."""

from __future__ import annotations

from ipaddress import IPv4Address, IPv4Interface, IPv4Network

import pytest

from tests.conftest import ROOT
from vlsmkit import ios
from vlsmkit.spec import Network

AS_BUILT = ROOT / "deliverables" / "terminal_commands.txt"


@pytest.fixture(scope="module")
def as_built() -> dict[str, ios.ParsedConfig]:
    return ios.parse_many(AS_BUILT.read_text(encoding="utf-8"))


def test_as_built_file_has_every_router(as_built: dict[str, ios.ParsedConfig]) -> None:
    assert set(as_built) == {"R-Lion", "R-Elephant", "R-Cat", "R-Dog"}


@pytest.mark.parametrize("hostname", ["R-Lion", "R-Elephant", "R-Cat", "R-Dog"])
def test_generated_config_matches_as_built(
    network: Network, as_built: dict[str, ios.ParsedConfig], hostname: str
) -> None:
    generated = ios.parse(ios.render(network.router(hostname)))
    expected = as_built[hostname]
    assert generated.hostname == expected.hostname
    assert generated.interfaces == expected.interfaces
    assert generated.helpers == expected.helpers
    assert generated.static_routes == expected.static_routes
    assert generated.ospf_networks == expected.ospf_networks
    assert generated.ospf_router_id == expected.ospf_router_id
    assert generated.passive == expected.passive
    assert generated.redistribute == expected.redistribute


def test_render_shape(network: Network) -> None:
    text = ios.render(network.router("R-Cat"))
    assert text.startswith(ios.HEADER)
    assert " network 10.0.8.0 0.0.3.255 area 0" in text
    assert " ip helper-address 10.0.12.133" in text
    assert text.rstrip().endswith("write memory")


def test_parse_handles_comments_and_sections() -> None:
    cfg = ios.parse(
        "hostname R1\n! comment\ninterface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n"
        " ip helper-address 10.9.9.9\nip route 0.0.0.0 0.0.0.0 10.0.0.254\n"
        "router ospf 7\n router-id 1.1.1.1\n network 10.0.0.0 0.0.0.255 area 3\n"
        " passive-interface Gi0/0\n redistribute connected subnets\n"
    )
    assert cfg.interfaces == {"Gi0/0": IPv4Interface("10.0.0.1/24")}
    assert cfg.helpers == {"Gi0/0": IPv4Address("10.9.9.9")}
    assert cfg.static_routes == {(IPv4Network("0.0.0.0/0"), IPv4Address("10.0.0.254"))}
    assert cfg.ospf_networks == {(IPv4Network("10.0.0.0/24"), 3)}
    assert cfg.ospf_router_id == IPv4Address("1.1.1.1")
    assert cfg.passive == {"Gi0/0"}
    assert cfg.redistribute == {"connected"}
