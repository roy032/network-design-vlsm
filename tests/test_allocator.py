from __future__ import annotations

from ipaddress import IPv4Network
from itertools import pairwise

import pytest
from hypothesis import given
from hypothesis import strategies as st

from vlsmkit.allocator import (
    InsufficientAddressSpaceError,
    SubnetRequest,
    allocate,
    prefix_for_hosts,
    usable_hosts,
)

ANIMAL_KINGDOM = [
    SubnetRequest("Dog", 1200),
    SubnetRequest("Cat", 800),
    SubnetRequest("Elephant", 100),
    SubnetRequest("Lion", 10),
    SubnetRequest("Lion-Elephant", 2),
    SubnetRequest("Elephant-Cat", 2),
    SubnetRequest("Elephant-Dog", 2),
]


@pytest.mark.parametrize(
    ("hosts", "prefix"),
    [
        (1, 30),
        (2, 30),
        (3, 29),
        (6, 29),
        (7, 28),
        (14, 28),
        (15, 27),
        (126, 25),
        (127, 24),
        (800, 22),
        (1022, 22),
        (1023, 21),
        (1200, 21),
        (2046, 21),
    ],
)
def test_prefix_for_hosts_boundaries(hosts: int, prefix: int) -> None:
    assert prefix_for_hosts(hosts) == prefix


@pytest.mark.parametrize("hosts", [0, -1])
def test_prefix_for_hosts_rejects_non_positive(hosts: int) -> None:
    with pytest.raises(ValueError, match="hosts must be"):
        prefix_for_hosts(hosts)


def test_prefix_for_hosts_rejects_too_many() -> None:
    with pytest.raises(ValueError, match="cannot fit"):
        prefix_for_hosts(2**32)


def test_animal_kingdom_plan_matches_documented_design() -> None:
    plan = {a.name: str(a.network) for a in allocate("10.0.0.0/8", ANIMAL_KINGDOM)}
    assert plan == {
        "Dog": "10.0.0.0/21",
        "Cat": "10.0.8.0/22",
        "Elephant": "10.0.12.0/25",
        "Lion": "10.0.12.128/28",
        "Lion-Elephant": "10.0.12.144/30",
        "Elephant-Cat": "10.0.12.148/30",
        "Elephant-Dog": "10.0.12.152/30",
    }


def test_allocation_order_is_independent_of_input_order() -> None:
    forward = allocate("10.0.0.0/8", ANIMAL_KINGDOM)
    backward = allocate("10.0.0.0/8", list(reversed(ANIMAL_KINGDOM)))
    assert {a.name: a.network for a in forward}["Dog"] == IPv4Network("10.0.0.0/21")
    assert {a.network for a in forward} == {a.network for a in backward}


def test_allocation_properties() -> None:
    lion = {a.name: a for a in allocate("10.0.0.0/8", ANIMAL_KINGDOM)}["Lion"]
    assert str(lion.netmask) == "255.255.255.240"
    assert str(lion.wildcard) == "0.0.0.15"
    assert str(lion.first_host) == "10.0.12.129"
    assert str(lion.last_host) == "10.0.12.142"
    assert str(lion.broadcast) == "10.0.12.143"
    assert lion.usable_hosts == 14
    assert lion.wasted == 4
    assert str(lion.host(2)) == "10.0.12.130"
    with pytest.raises(IndexError):
        lion.host(15)
    with pytest.raises(IndexError):
        lion.host(0)


def test_insufficient_space() -> None:
    with pytest.raises(InsufficientAddressSpaceError, match="no room"):
        allocate(
            "192.168.1.0/24",
            [SubnetRequest("a", 100), SubnetRequest("b", 100), SubnetRequest("c", 100)],
        )


def test_request_larger_than_parent() -> None:
    with pytest.raises(InsufficientAddressSpaceError, match="larger than"):
        allocate("192.168.1.0/24", [SubnetRequest("big", 300)])


def test_duplicate_names_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        allocate("10.0.0.0/24", [SubnetRequest("a", 2), SubnetRequest("a", 2)])


@pytest.mark.parametrize(("name", "hosts"), [("", 5), ("x", 0)])
def test_invalid_request(name: str, hosts: int) -> None:
    with pytest.raises(ValueError, match="must"):
        SubnetRequest(name, hosts)


def test_usable_hosts_never_negative() -> None:
    assert usable_hosts(32) == 0
    assert usable_hosts(31) == 0
    assert usable_hosts(30) == 2


requests_strategy = st.lists(st.integers(min_value=1, max_value=5000), min_size=1, max_size=25).map(
    lambda sizes: [SubnetRequest(f"net{i}", h) for i, h in enumerate(sizes)]
)


@given(requests_strategy)
def test_property_valid_plans(requests: list[SubnetRequest]) -> None:
    """For any input that fits: no overlap, aligned, minimal, inside parent."""
    parent = IPv4Network("10.0.0.0/8")
    plan = allocate(parent, requests)
    assert len(plan) == len(requests)
    nets = sorted(a.network for a in plan)
    for a, b in pairwise(nets):
        assert not a.overlaps(b)
    for alloc in plan:
        assert alloc.network.subnet_of(parent)
        assert alloc.usable_hosts >= alloc.hosts_required
        # minimal: one size smaller would not fit
        assert usable_hosts(alloc.prefixlen + 1) < alloc.hosts_required or alloc.prefixlen == 30


@given(requests_strategy)
def test_property_plan_is_contiguous(requests: list[SubnetRequest]) -> None:
    """Largest-first leaves no gaps: allocations tile a prefix of the parent."""
    plan = allocate("10.0.0.0/8", requests)
    total = sum(a.network.num_addresses for a in plan)
    end = max(int(a.network.broadcast_address) for a in plan)
    assert end - int(IPv4Network("10.0.0.0/8").network_address) + 1 == total


@given(st.lists(st.integers(min_value=1, max_value=200), min_size=1, max_size=40))
def test_property_fits_or_raises(sizes: list[int]) -> None:
    parent = IPv4Network("192.168.0.0/22")
    requests = [SubnetRequest(f"n{i}", h) for i, h in enumerate(sizes)]
    needed = sum(1 << (32 - prefix_for_hosts(h)) for h in sizes)
    if needed <= parent.num_addresses:
        assert len(allocate(parent, requests)) == len(sizes)
    else:
        with pytest.raises(InsufficientAddressSpaceError):
            allocate(parent, requests)
