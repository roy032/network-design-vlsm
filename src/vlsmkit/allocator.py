"""Variable Length Subnet Mask (VLSM) allocation.

The allocator implements the classic textbook algorithm:

1. Find the smallest prefix whose usable host count covers each request.
2. Sort requests largest block first (ties keep their declaration order).
3. Hand out blocks sequentially from the start of the parent network,
   aligning each block on its own size.

Allocating largest-first means every block starts on a boundary that is
already aligned for all smaller blocks that follow, so the plan never leaves
alignment gaps and the result is deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network

__all__ = [
    "Allocation",
    "InsufficientAddressSpaceError",
    "SubnetRequest",
    "allocate",
    "prefix_for_hosts",
]


class InsufficientAddressSpaceError(ValueError):
    """Raised when the parent network cannot hold every requested subnet."""


@dataclass(frozen=True, slots=True)
class SubnetRequest:
    """A named request for a subnet with at least ``hosts`` usable addresses."""

    name: str
    hosts: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("subnet name must not be empty")
        if self.hosts < 1:
            raise ValueError(f"{self.name}: hosts must be >= 1, got {self.hosts}")


@dataclass(frozen=True, slots=True)
class Allocation:
    """A subnet carved out of the parent network for one request."""

    name: str
    hosts_required: int
    network: IPv4Network

    @property
    def prefixlen(self) -> int:
        return self.network.prefixlen

    @property
    def netmask(self) -> IPv4Address:
        return self.network.netmask

    @property
    def wildcard(self) -> IPv4Address:
        return self.network.hostmask

    @property
    def usable_hosts(self) -> int:
        return usable_hosts(self.prefixlen)

    @property
    def first_host(self) -> IPv4Address:
        return self.network.network_address + 1

    @property
    def last_host(self) -> IPv4Address:
        return self.network.broadcast_address - 1

    @property
    def broadcast(self) -> IPv4Address:
        return self.network.broadcast_address

    @property
    def wasted(self) -> int:
        """Usable addresses that were allocated but not requested."""
        return self.usable_hosts - self.hosts_required

    def host(self, index: int) -> IPv4Address:
        """Return the ``index``-th usable address (1-based)."""
        if not 1 <= index <= self.usable_hosts:
            raise IndexError(f"{self.name}: host index {index} outside 1..{self.usable_hosts}")
        return self.network.network_address + index


def usable_hosts(prefixlen: int) -> int:
    """Usable host addresses in a subnet (network and broadcast excluded)."""
    return max((1 << (32 - prefixlen)) - 2, 0)


def prefix_for_hosts(hosts: int) -> int:
    """Smallest subnet (longest prefix) with at least ``hosts`` usable addresses.

    >>> prefix_for_hosts(2)
    30
    >>> prefix_for_hosts(1200)
    21
    """
    if hosts < 1:
        raise ValueError(f"hosts must be >= 1, got {hosts}")
    # Need 2**bits - 2 >= hosts  <=>  2**bits >= hosts + 2.
    bits = max((hosts + 1).bit_length(), 2)
    if bits > 32:
        raise ValueError(f"{hosts} hosts cannot fit in an IPv4 subnet")
    return 32 - bits


def allocate(
    parent: IPv4Network | str, requests: list[SubnetRequest] | tuple[SubnetRequest, ...]
) -> list[Allocation]:
    """Allocate a subnet for every request inside ``parent``.

    Returns allocations in address order. Raises
    :class:`InsufficientAddressSpaceError` if the requests do not fit and
    :class:`ValueError` for duplicate names.
    """
    parent = IPv4Network(parent)
    names = [r.name for r in requests]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"duplicate subnet names: {', '.join(duplicates)}")

    # sorted() is stable, so equal-sized requests keep declaration order.
    ordered = sorted(requests, key=lambda r: prefix_for_hosts(r.hosts))

    cursor = int(parent.network_address)
    end = int(parent.broadcast_address)
    allocations: list[Allocation] = []
    for request in ordered:
        prefixlen = prefix_for_hosts(request.hosts)
        if prefixlen < parent.prefixlen:
            raise InsufficientAddressSpaceError(
                f"{request.name} needs a /{prefixlen}, larger than {parent}"
            )
        size = 1 << (32 - prefixlen)
        start = (cursor + size - 1) // size * size  # align up to block size
        if start + size - 1 > end:
            raise InsufficientAddressSpaceError(
                f"{parent} has no room left for {request.name} "
                f"({request.hosts} hosts, /{prefixlen})"
            )
        allocations.append(
            Allocation(
                name=request.name,
                hosts_required=request.hosts,
                network=IPv4Network((start, prefixlen)),
            )
        )
        cursor = start + size
    return allocations
