"""Verify the Animal Kingdom network design without opening Packet Tracer.

Checks:
  1. VLSM: recompute the allocation from the host requirements and compare it
     with docs/IP_Address_Table.md (aligned, non-overlapping, smallest fit).
  2. Addressing: every device IP in the table is a usable host address inside
     its subnet, and no IP is used twice.
  3. Router CLI (deliverables/terminal_commands.txt): interface addresses match
     the documented ones, static-route next hops are on connected subnets, and
     every subnet is reachable from every router (simple OSPF/static model).
  4. Docs vs CLI: interface names that differ between the two are reported.

Usage:  python tools/verify_design.py        (exit code 1 if any ERROR)
"""
import ipaddress as ip
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, warnings = [], []
err = errors.append
warn = warnings.append

# name -> hosts needed (Lion: 3 PCs + 4 servers + router gateway; links: 2 routers)
REQUIREMENTS = {"Dog": 1200, "Cat": 800, "Elephant": 100, "Lion": 8,
                "Lion-Elephant": 2, "Elephant-Cat": 2, "Elephant-Dog": 2}
# Elephant needs 100 hosts + router gateway; Lion's /28 in the docs leaves growth room.


def vlsm(requirements, base):
    pool, out = ip.ip_network(base), {}
    nxt = int(pool.network_address)
    for name, hosts in sorted(requirements.items(), key=lambda kv: -kv[1]):
        bits = (hosts + 2 - 1).bit_length()          # host bits incl. net+broadcast
        size = 1 << bits
        nxt = (nxt + size - 1) // size * size        # align to block size
        out[name] = ip.ip_network((nxt, 32 - bits))
        nxt += size
    return out


def parse_table(md):
    nets, devices, section, in_devices = {}, [], None, False
    ipv4 = r"\d+\.\d+\.\d+\.\d+"
    for line in md.splitlines():
        if line.startswith("## "):
            in_devices = line.startswith("## Detailed Device")
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) < 5:
            continue
        if re.fullmatch(r"/\d+", cells[3]) and re.fullmatch(ipv4, cells[1]):
            nets[cells[0]] = ip.ip_network(f"{cells[1]}{cells[3]}")
        elif in_devices and re.fullmatch(ipv4, cells[2]) and re.fullmatch(ipv4, cells[3]):
            devices.append((cells[0], cells[1], cells[2], cells[3], section))
    return nets, devices


def parse_cli(text):
    routers, cur, iface, ospf = {}, None, None, False
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"hostname (\S+)", line)
        if m:
            cur = routers.setdefault(m.group(1), {"ifaces": {}, "routes": [], "ospf": [],
                                                  "passive": set(), "redistribute": False})
            iface = None
        if cur is None:
            continue
        m = re.match(r"interface (\S+)", line)
        if m:
            iface = m.group(1)
        m = re.match(r"ip address ([\d.]+) ([\d.]+)", line)
        if m and iface:
            cur["ifaces"][iface] = ip.ip_interface(f"{m.group(1)}/{m.group(2)}")
        m = re.match(r"ip route ([\d.]+) ([\d.]+) ([\d.]+)", line)
        if m:
            cur["routes"].append((ip.ip_network(f"{m.group(1)}/{m.group(2)}"), ip.ip_address(m.group(3))))
        m = re.match(r"network ([\d.]+) ([\d.]+) area", line)
        if m:
            wild = ip.ip_address(m.group(2))
            mask = ip.ip_address(int(wild) ^ 0xFFFFFFFF)
            cur["ospf"].append(ip.ip_network(f"{m.group(1)}/{mask}"))
        m = re.match(r"passive-interface (\S+)", line)
        if m:
            cur["passive"].add(m.group(1))
        if line.startswith("redistribute static"):
            cur["redistribute"] = True
        if line == "interface" or line.startswith("router ospf"):
            iface = None
    return routers


def short(n):  # GigabitEthernet0/0 -> Gi0/0
    return re.sub(r"^GigabitEthernet", "Gi", n)


def main():
    table = (ROOT / "docs/IP_Address_Table.md").read_text(encoding="utf8")
    cli = (ROOT / "deliverables/terminal_commands.txt").read_text(encoding="utf8")
    nets, devices = parse_table(table)
    routers = parse_cli(cli)

    # 1. VLSM
    plan = vlsm(REQUIREMENTS, "10.0.0.0/8")
    for name, want in plan.items():
        doc = next((n for k, n in nets.items() if k.replace(" Tribe", "") == name), None)
        if doc is None:
            err(f"VLSM: {name} missing from IP_Address_Table summary")
        elif doc != want:
            err(f"VLSM: {name} documented {doc}, recomputed {want}")
    nl = sorted(nets.values())
    for a, b in zip(nl, nl[1:]):
        if a.overlaps(b):
            err(f"overlap: {a} and {b}")
    print("Subnet plan (recomputed):")
    for n, net in plan.items():
        print(f"  {n:<14} {str(net):<18} usable={net.num_addresses - 2}")

    # 2. Device addressing
    seen = {}
    for dev, iface, addr, mask, tribe in devices:
        a = ip.ip_address(addr)
        net = ip.ip_interface(f"{addr}/{mask}").network
        if net not in nets.values():
            err(f"{dev} {iface}: {addr}/{mask} is not one of the planned subnets")
        elif a in (net.network_address, net.broadcast_address):
            err(f"{dev} {iface}: {addr} is the network/broadcast address of {net}")
        if addr in seen:
            err(f"duplicate IP {addr}: {seen[addr]} and {dev}")
        seen[addr] = dev

    # 3. Router CLI vs docs
    doc_if = {}
    for dev, iface, addr, mask, _ in devices:
        if dev.startswith("R-"):
            doc_if.setdefault(dev, {})[short(iface)] = ip.ip_interface(f"{addr}/{mask}")
    for r, d in routers.items():
        doc_ips = {i.ip: (n, i) for n, i in doc_if.get(r, {}).items()}
        for iname, iface in d["ifaces"].items():
            if iface.ip not in doc_ips:
                err(f"{r} {iname}: CLI address {iface} not in IP_Address_Table")
                continue
            dname, dif = doc_ips[iface.ip]
            if dif != iface:
                err(f"{r} {iname}: CLI {iface} differs from docs {dif}")
            if dname != short(iname):
                warn(f"{r}: {iface.ip} is on {short(iname)} in terminal_commands.txt but {dname} in the docs")
        for net, nh in d["routes"]:
            if not any(nh in i.network for i in d["ifaces"].values()):
                err(f"{r}: static route {net} next hop {nh} is not on a connected subnet")
        for iname, iface in d["ifaces"].items():
            if d["ospf"] and not any(iface.ip in o for o in d["ospf"]) and d["routes"] == []:
                warn(f"{r} {iname}: {iface.network} not covered by an OSPF network statement")

    # 3b. Reachability model: OSPF adjacency across links where both ends are enabled
    def ospf_ifaces(d):
        return {n: i for n, i in d["ifaces"].items()
                if any(i.ip in o for o in d["ospf"]) and n not in d["passive"]}
    known = {r: {i.network for i in d["ifaces"].values()} | {n for n, _ in d["routes"]}
             for r, d in routers.items()}
    adj = {r: set() for r in routers}
    for a in routers:
        for b in routers:
            if a < b:
                common = {i.network for i in ospf_ifaces(routers[a]).values()} & \
                         {i.network for i in ospf_ifaces(routers[b]).values()}
                if common:
                    adj[a].add(b); adj[b].add(a)
    comp, todo = {}, list(routers)
    while todo:
        r = todo.pop()
        if r in comp:
            continue
        group, stack = set(), [r]
        while stack:
            x = stack.pop()
            if x not in group:
                group.add(x); stack.extend(adj[x])
        for x in group:
            comp[x] = group
        if len(group) > 1:
            learned = set()
            for x in group:
                d = routers[x]
                learned |= {i.network for i in d["ifaces"].values() if any(i.ip in o for o in d["ospf"])}
                if d["redistribute"]:
                    learned |= {n for n, _ in d["routes"]}
            for x in group:
                known[x] |= learned
    lans = [n for k, n in nets.items() if "-" not in k]
    for r in routers:
        for n in lans:
            if not any(n.subnet_of(k) for k in known[r]):
                err(f"reachability: {r} has no route to {n}")

    print()
    for w in warnings:
        print("WARN :", w)
    for e in errors:
        print("ERROR:", e)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
