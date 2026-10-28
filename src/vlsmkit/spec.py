"""Load and validate a network specification (``network.toml``).

Loading resolves every symbolic reference (subnet ids, ``host = N`` offsets,
``via = "R-Elephant"`` next hops) into concrete addresses and collects *all*
validation problems before failing, so a broken spec reports everything that
is wrong in one go.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from pathlib import Path
from typing import Any

from vlsmkit.allocator import Allocation, SubnetRequest, allocate

__all__ = [
    "DhcpPool",
    "Host",
    "Interface",
    "Network",
    "Ospf",
    "Router",
    "SpecError",
    "StaticRoute",
    "Subnet",
    "load",
    "parse",
]


class SpecError(ValueError):
    """The specification is invalid. ``problems`` lists every issue found."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("invalid network spec:\n" + "\n".join(f"  - {p}" for p in problems))


@dataclass(frozen=True, slots=True)
class DhcpPool:
    name: str
    exclude_first: int


@dataclass(frozen=True, slots=True)
class Subnet:
    id: str
    name: str
    allocation: Allocation
    dhcp: DhcpPool | None = None

    @property
    def network(self) -> IPv4Network:
        return self.allocation.network

    @property
    def is_point_to_point(self) -> bool:
        return self.allocation.usable_hosts == 2

    @property
    def dhcp_range(self) -> tuple[IPv4Address, IPv4Address] | None:
        if self.dhcp is None:
            return None
        return (
            self.allocation.host(self.dhcp.exclude_first + 1),
            self.allocation.last_host,
        )


@dataclass(frozen=True, slots=True)
class Interface:
    name: str
    subnet: Subnet
    address: IPv4Interface
    description: str
    dhcp_relay: IPv4Address | None = None

    @property
    def short_name(self) -> str:
        return self.name.replace("GigabitEthernet", "Gi").replace("FastEthernet", "Fa")


@dataclass(frozen=True, slots=True)
class StaticRoute:
    destination: IPv4Network
    next_hop: IPv4Address
    via_router: str


@dataclass(frozen=True, slots=True)
class Ospf:
    process: int
    router_id: IPv4Address
    area: int
    networks: tuple[IPv4Network, ...]
    passive: tuple[str, ...] = ()
    redistribute: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Router:
    hostname: str
    interfaces: tuple[Interface, ...]
    static_routes: tuple[StaticRoute, ...] = ()
    ospf: Ospf | None = None

    def interface(self, name: str) -> Interface:
        for iface in self.interfaces:
            if iface.name == name:
                return iface
        raise KeyError(f"{self.hostname} has no interface {name}")

    def interface_in(self, network: IPv4Network) -> Interface | None:
        for iface in self.interfaces:
            if iface.address.network == network:
                return iface
        return None


@dataclass(frozen=True, slots=True)
class Host:
    name: str
    subnet: Subnet
    address: IPv4Address
    gateway: IPv4Address
    role: str
    dns: tuple[str, ...] = ()
    mx: bool = False


@dataclass(frozen=True, slots=True)
class Network:
    name: str
    supernet: IPv4Network
    domain: str
    subnets: tuple[Subnet, ...]
    routers: tuple[Router, ...]
    hosts: tuple[Host, ...] = field(default_factory=tuple)

    def subnet(self, subnet_id: str) -> Subnet:
        for s in self.subnets:
            if s.id == subnet_id:
                return s
        raise KeyError(subnet_id)

    def router(self, hostname: str) -> Router:
        for r in self.routers:
            if r.hostname == hostname:
                return r
        raise KeyError(hostname)

    def host(self, name: str) -> Host:
        for h in self.hosts:
            if h.name == name:
                return h
        raise KeyError(name)

    @property
    def lans(self) -> tuple[Subnet, ...]:
        return tuple(s for s in self.subnets if not s.is_point_to_point)


def load(path: str | Path) -> Network:
    """Load and validate a TOML spec from ``path``."""
    with Path(path).open("rb") as fh:
        return parse(tomllib.load(fh))


def parse(raw: Mapping[str, Any]) -> Network:
    """Validate a decoded spec and resolve it into a :class:`Network`."""
    return _Resolver(raw).resolve()


class _Resolver:
    def __init__(self, raw: Mapping[str, Any]) -> None:
        self.raw = raw
        self.problems: list[str] = []

    def fail(self, message: str) -> None:
        self.problems.append(message)

    def resolve(self) -> Network:
        meta = self.raw.get("network", {})
        try:
            supernet = IPv4Network(meta["supernet"])
        except (KeyError, ValueError) as exc:
            raise SpecError([f"[network] supernet missing or invalid: {exc}"]) from exc

        subnets = self._subnets(supernet)
        by_id = {s.id: s for s in subnets}
        hosts = self._hosts(by_id)
        hosts_by_name = {h.name: h for h in hosts}
        routers = self._routers(by_id, hosts_by_name)
        self._check_unique_addresses(routers, hosts)

        if self.problems:
            raise SpecError(self.problems)
        return Network(
            name=str(meta.get("name", "network")),
            supernet=supernet,
            domain=str(meta.get("domain", "")),
            subnets=subnets,
            routers=routers,
            hosts=hosts,
        )

    def _subnets(self, supernet: IPv4Network) -> tuple[Subnet, ...]:
        raw_subnets = self.raw.get("subnets", [])
        if not raw_subnets:
            raise SpecError(["spec defines no [[subnets]]"])
        try:
            requests = [SubnetRequest(s["id"], int(s["hosts"])) for s in raw_subnets]
            allocations = {a.name: a for a in allocate(supernet, requests)}
        except (KeyError, ValueError) as exc:
            raise SpecError([f"subnets: {exc}"]) from exc

        subnets = []
        for s in raw_subnets:
            dhcp = None
            if "dhcp" in s:
                dhcp = DhcpPool(s["dhcp"]["pool"], int(s["dhcp"].get("exclude_first", 0)))
                if dhcp.exclude_first >= allocations[s["id"]].usable_hosts:
                    self.fail(f"subnet {s['id']}: DHCP exclusion covers the whole subnet")
                    dhcp = None
            subnets.append(
                Subnet(
                    id=s["id"],
                    name=s.get("name", s["id"]),
                    allocation=allocations[s["id"]],
                    dhcp=dhcp,
                )
            )
        # Address order makes every downstream table read naturally.
        return tuple(sorted(subnets, key=lambda s: s.network))

    def _address(self, where: str, subnet: Subnet, index: Any) -> IPv4Address | None:
        try:
            return subnet.allocation.host(int(index))
        except (IndexError, ValueError, TypeError) as exc:
            self.fail(f"{where}: {exc}")
            return None

    def _lookup(self, where: str, by_id: Mapping[str, Subnet], subnet_id: str) -> Subnet | None:
        if subnet_id not in by_id:
            self.fail(f"{where}: unknown subnet '{subnet_id}'")
            return None
        return by_id[subnet_id]

    def _hosts(self, by_id: Mapping[str, Subnet]) -> tuple[Host, ...]:
        hosts = []
        for h in self.raw.get("hosts", []):
            where = f"host {h.get('name', '?')}"
            subnet = self._lookup(where, by_id, h.get("subnet", ""))
            if subnet is None:
                continue
            address = self._address(where, subnet, h.get("host"))
            if address is None:
                continue
            hosts.append(
                Host(
                    name=h["name"],
                    subnet=subnet,
                    address=address,
                    gateway=subnet.allocation.first_host,
                    role=h.get("role", ""),
                    dns=tuple(h.get("dns", ())),
                    mx=bool(h.get("mx", False)),
                )
            )
        return tuple(hosts)

    def _routers(
        self, by_id: Mapping[str, Subnet], hosts: Mapping[str, Host]
    ) -> tuple[Router, ...]:
        # Pass 1: interfaces, so static routes can resolve neighbours by name.
        interfaces: dict[str, list[Interface]] = {}
        for r in self.raw.get("routers", []):
            hostname = r["hostname"]
            if hostname in interfaces:
                self.fail(f"duplicate router hostname {hostname}")
            ifaces: list[Interface] = []
            for i in r.get("interfaces", []):
                where = f"{hostname} {i.get('name', '?')}"
                subnet = self._lookup(where, by_id, i.get("subnet", ""))
                if subnet is None:
                    continue
                address = self._address(where, subnet, i.get("host"))
                if address is None:
                    continue
                relay = None
                if "dhcp_relay" in i:
                    if i["dhcp_relay"] in hosts:
                        relay = hosts[i["dhcp_relay"]].address
                    else:
                        self.fail(f"{where}: unknown DHCP relay target '{i['dhcp_relay']}'")
                if any(x.name == i["name"] for x in ifaces):
                    self.fail(f"{where}: interface defined twice")
                ifaces.append(
                    Interface(
                        name=i["name"],
                        subnet=subnet,
                        address=IPv4Interface((address, subnet.network.prefixlen)),
                        description=i.get("description", ""),
                        dhcp_relay=relay,
                    )
                )
            interfaces[hostname] = ifaces

        # Pass 2: routing.
        routers = []
        for r in self.raw.get("routers", []):
            hostname = r["hostname"]
            own = interfaces[hostname]
            statics = tuple(
                route
                for s in r.get("static_routes", [])
                if (route := self._static(hostname, s, own, interfaces, by_id)) is not None
            )
            ospf = self._ospf(hostname, r["ospf"], own, by_id) if "ospf" in r else None
            routers.append(Router(hostname, tuple(own), statics, ospf))
        return tuple(routers)

    def _static(
        self,
        hostname: str,
        raw: Mapping[str, Any],
        own: list[Interface],
        all_ifaces: Mapping[str, list[Interface]],
        by_id: Mapping[str, Subnet],
    ) -> StaticRoute | None:
        where = f"{hostname} static route to {raw.get('to', '?')}"
        dest = self._lookup(where, by_id, raw.get("to", ""))
        via = raw.get("via", "")
        if via not in all_ifaces:
            self.fail(f"{where}: unknown next-hop router '{via}'")
            return None
        if dest is None:
            return None
        # The next hop is the neighbour's address on the subnet we share.
        own_nets = {i.address.network for i in own}
        shared = [i for i in all_ifaces[via] if i.address.network in own_nets]
        if not shared:
            self.fail(f"{where}: {hostname} and {via} share no subnet")
            return None
        return StaticRoute(dest.network, shared[0].address.ip, via)

    def _ospf(
        self,
        hostname: str,
        raw: Mapping[str, Any],
        own: list[Interface],
        by_id: Mapping[str, Subnet],
    ) -> Ospf:
        own_names = {i.name for i in own}
        networks = []
        for subnet_id in raw.get("networks", []):
            subnet = self._lookup(f"{hostname} OSPF", by_id, subnet_id)
            if subnet is not None:
                networks.append(subnet.network)
        for name in raw.get("passive", []):
            if name not in own_names:
                self.fail(f"{hostname} OSPF: passive interface {name} does not exist")
        for proto in raw.get("redistribute", []):
            if proto not in {"static", "connected"}:
                self.fail(f"{hostname} OSPF: cannot redistribute '{proto}'")
        return Ospf(
            process=int(raw.get("process", 1)),
            router_id=IPv4Address(raw["router_id"]),
            area=int(raw.get("area", 0)),
            networks=tuple(networks),
            passive=tuple(raw.get("passive", ())),
            redistribute=tuple(raw.get("redistribute", ())),
        )

    def _check_unique_addresses(self, routers: tuple[Router, ...], hosts: tuple[Host, ...]) -> None:
        owners: dict[IPv4Address, str] = {}
        claims = [(i.address.ip, f"{r.hostname} {i.name}") for r in routers for i in r.interfaces]
        claims += [(h.address, h.name) for h in hosts]
        for address, owner in claims:
            if address in owners:
                self.fail(f"{address} assigned to both {owners[address]} and {owner}")
            owners[address] = owner
        gateways = {i.address.ip for r in routers for i in r.interfaces}
        for h in hosts:
            if h.gateway not in gateways:
                self.fail(f"{h.name}: no router interface owns gateway {h.gateway}")
            if h.subnet.dhcp_range and h.subnet.dhcp_range[0] <= h.address:
                self.fail(f"{h.name} static address {h.address} is inside the DHCP pool")
