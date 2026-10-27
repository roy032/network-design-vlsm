# VLSM Tree Diagram for Project Documentation

## Visual VLSM Tree Structure

```
10.0.0.0/8
└── 10.0.0.0/20  (first 4,096 addresses used; 10.0.16.0 onward free)
    ├── 10.0.0.0/21        Dog       (1200 hosts -> 2046 usable)
    └── 10.0.8.0/21
        ├── 10.0.8.0/22    Cat       (800 hosts  -> 1022 usable)
        └── 10.0.12.0/22
            └── 10.0.12.0/24
                ├── 10.0.12.0/25      Elephant  (100 hosts -> 126 usable)
                └── 10.0.12.128/25
                    ├── 10.0.12.128/28    Lion  (10 hosts -> 14 usable)
                    └── 10.0.12.144/28
                        ├── 10.0.12.144/30    Lion-Elephant link
                        ├── 10.0.12.148/30    Elephant-Cat link
                        ├── 10.0.12.152/30    Elephant-Dog link
                        └── 10.0.12.156/30    free (spare /30 + 10.0.12.160/27 and up)
```

Blocks are carved largest-first; intermediate split levels that hold no allocation are collapsed for readability. Allocation order is largest to smallest, so every block is aligned and nothing overlaps. `python tools/verify_design.py` recomputes this plan and checks it against the IP table.

## Network Allocation Summary

| Network          | Hosts Needed | Hosts Available | Network Address | Subnet Mask     | CIDR | Usable Range              | Broadcast      |
|------------------|--------------|-----------------|-----------------|-----------------|------|---------------------------|----------------|
| Dog Tribe        | 1200         | 2046            | 10.0.0.0        | 255.255.248.0   | /21  | 10.0.0.1 - 10.0.7.254     | 10.0.7.255     |
| Cat Tribe        | 800          | 1022            | 10.0.8.0        | 255.255.252.0   | /22  | 10.0.8.1 - 10.0.11.254    | 10.0.11.255    |
| Elephant Tribe   | 100          | 126             | 10.0.12.0       | 255.255.255.128 | /25  | 10.0.12.1 - 10.0.12.126   | 10.0.12.127    |
| Lion Tribe       | 10           | 14              | 10.0.12.128     | 255.255.255.240 | /28  | 10.0.12.129 - 10.0.12.142 | 10.0.12.143    |
| Lion-Elephant    | 2            | 2               | 10.0.12.144     | 255.255.255.252 | /30  | 10.0.12.145 - 10.0.12.146 | 10.0.12.147    |
| Elephant-Cat     | 2            | 2               | 10.0.12.148     | 255.255.255.252 | /30  | 10.0.12.149 - 10.0.12.150 | 10.0.12.151    |
| Elephant-Dog     | 2            | 2               | 10.0.12.152     | 255.255.255.252 | /30  | 10.0.12.153 - 10.0.12.154 | 10.0.12.155    |

## VLSM Design Explanation

The VLSM design efficiently allocates IP addresses from the 10.0.0.0/8 network space:

1. **Dog Tribe (Largest)**: Allocated 10.0.0.0/21 to accommodate 1200 hosts
2. **Cat Tribe**: Allocated 10.0.8.0/22 to accommodate 800 hosts
3. **Elephant Tribe**: Allocated 10.0.12.0/25 to accommodate 100 hosts
4. **Lion Tribe**: Allocated 10.0.12.128/28 to accommodate servers and management devices
5. **Point-to-Point Links**: Three /30 networks for router interconnections

This hierarchical design minimizes IP address waste while providing room for growth in each network segment.
