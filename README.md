# Animal Kingdom Network Design (VLSM)

A comprehensive network infrastructure project for a fictional **Animal Kingdom** with four tribes, designed and implemented in **Cisco Packet Tracer**. Demonstrates subnetting, routing protocols, and enterprise network services.

## Network Architecture

```
          Lion (10.0.12.128/28)
              |
        Elephant (10.0.12.0/25)
         /              \
      Cat               Dog
 (10.0.8.0/22)    (10.0.0.0/21)
```

| Tribe | Hosts | Role |
|-------|-------|------|
| Lion | 3 + 4 servers | King's residence, central services |
| Elephant | 100 | Central hub |
| Cat | 800 | Standard tribe |
| Dog | 1200 | Largest tribe |

## Key Features

- **VLSM Subnetting** — Efficient IP address allocation across variable-size networks
- **OSPF Dynamic Routing** — For Elephant, Cat, and Dog tribes
- **Static Routing** — For the Lion tribe
- **Centralized DHCP** — Single server handles all tribe allocations
- **DNS Service** — Resolves `www.animals.com`
- **Web Server** — Hosts the Animal Kingdom website
- **Email Service** — Inter-tribal communication between chiefs

## Project Structure

```
├── README.md
├── tools/
│   └── verify_design.py                     # checks VLSM plan, IP table and router CLI
├── docs/
│   ├── VLSM_Calculation.md
│   ├── IP_Address_Table.md
│   ├── Network_Topology.md
│   ├── Router_Configurations.md
│   ├── Server_Configuration.md
│   ├── Implementation_Guide.md
│   └── Complete_Step_By_Step_Guide.md
└── deliverables/
    ├── project.pkt                          # Cisco Packet Tracer file
    ├── topology.png                         # Network topology diagram
    ├── terminal_commands.txt                # Router CLI commands
    ├── verification_commands.txt            # Network verification commands
    ├── Verification_Commands_Documentation.md
    └── VLSM_Tree_for_Documentation.md
```

## Verify the Design

No Packet Tracer needed. The script recomputes the VLSM plan from the host requirements, checks every documented IP (usable host address, inside its subnet, no duplicates), compares router interface addresses in `deliverables/terminal_commands.txt` with the IP table, validates static-route next hops, and models OSPF adjacency and static redistribution to confirm every router can reach every LAN.

```bash
python tools/verify_design.py   # Python 3.8+, standard library only; exit code 1 on errors
```

Current result: 0 errors, 3 warnings. The warnings are known doc/CLI mismatches: `terminal_commands.txt` uses `Gi0/0/0` for the Lion-Elephant link on both routers and `Gi0/0` for the Elephant LAN, while the docs list `Gi0/0` and `Gi1/0`. Check which one matches `project.pkt` and align the other.

## Tools Used

- Cisco Packet Tracer
- VLSM subnetting methodology
- OSPF / Static routing

## How to Open

1. Install [Cisco Packet Tracer](https://www.netacad.com/courses/packet-tracer)
2. Open `deliverables/project.pkt`
3. Refer to `docs/` for full configuration details
