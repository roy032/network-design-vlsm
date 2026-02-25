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

## Tools Used

- Cisco Packet Tracer
- VLSM subnetting methodology
- OSPF / Static routing

## How to Open

1. Install [Cisco Packet Tracer](https://www.netacad.com/courses/packet-tracer)
2. Open `deliverables/project.pkt`
3. Refer to `docs/` for full configuration details
