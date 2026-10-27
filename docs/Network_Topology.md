# Animal Kingdom - Network Topology Design

## Network Diagram Description

```
                    INTERNET (Optional)
                           |
                    +------+------+
                    |   Lion     |
                    |  Router    |
                    | (R-Lion)   |
                    +------+------+
                           |
                    [10.0.12.144/30]
                           |
                    +------+------+
                    | Elephant   |
                    |  Router    |
                    | (R-Elephant)|
                    +------+------+
                     /           \
      [10.0.12.148/30]         [10.0.12.152/30]
                   /               \
          +-------+------+    +------+-------+
          |    Cat       |    |     Dog      |
          |   Router     |    |    Router    |
          |   (R-Cat)    |    |   (R-Dog)    |
          +-------+------+    +------+-------+


====================================================================
                    DETAILED NETWORK LAYOUT
====================================================================

┌─────────────────────────────────────────────────────────────────┐
│                        LION TRIBE                               │
│                    Network: 10.0.12.128/28                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Router: R-Lion                                                 │
│  ├─ GigabitEthernet0/0/0 (to Elephant): 10.0.12.145/30          │
│  └─ GigabitEthernet0/1 (LAN): 10.0.12.129/28                  │
│                                                                 │
│  Switch: SW-Lion (Layer 2)                                     │
│                                                                 │
│  Servers (Static IPs):                                         │
│  ├─ Web Server: 10.0.12.130 (www.animals.com)                 │
│  ├─ DNS Server: 10.0.12.131 (animals.com zone)                │
│  ├─ Email Server: 10.0.12.132 (SMTP/POP3)                     │
│  └─ DHCP Server: 10.0.12.133                                  │
│                                                                 │
│  Chief's Computer (Static IP):                                 │
│  └─ Lion King PC: 10.0.12.134                                 │
│     Email: lionking@animals.com                                │
│                                                                 │
│  End Devices (Static):                                         │
│  ├─ PC-Lion-1: 10.0.12.135                                    │
│  └─ PC-Lion-2: 10.0.12.136                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ELEPHANT TRIBE                             │
│                    Network: 10.0.12.0/25                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Router: R-Elephant                                             │
│  ├─ GigabitEthernet0/0/0 (to Lion): 10.0.12.146/30              │
│  ├─ GigabitEthernet0/1 (to Cat): 10.0.12.149/30               │
│  ├─ GigabitEthernet0/2 (to Dog): 10.0.12.153/30               │
│  └─ GigabitEthernet0/0 (LAN): 10.0.12.1/25                    │
│                                                                 │
│  Switch: SW-Elephant (Layer 2)                                 │
│                                                                 │
│  Chief's Computer (Static IP):                                 │
│  └─ Elephant Chief PC: 10.0.12.2                              │
│     Email: elephantchief@animals.com                           │
│                                                                 │
│  End Devices (DHCP):                                           │
│  ├─ PC-Elephant-1: DHCP (from 10.0.12.133)                    │
│  └─ PC-Elephant-2: DHCP (from 10.0.12.133)                    │
│                                                                 │
│  DHCP Pool Range: 10.0.12.10 - 10.0.12.126                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        CAT TRIBE                                │
│                    Network: 10.0.8.0/22                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Router: R-Cat                                                  │
│  ├─ GigabitEthernet0/0 (to Elephant): 10.0.12.150/30          │
│  └─ GigabitEthernet0/1 (LAN): 10.0.8.1/22                     │
│                                                                 │
│  Switch: SW-Cat (Layer 2)                                      │
│                                                                 │
│  Chief's Computer (Static IP):                                 │
│  └─ Cat Chief PC: 10.0.8.2                                    │
│     Email: catchief@animals.com                                │
│                                                                 │
│  End Devices (DHCP):                                           │
│  ├─ PC-Cat-1: DHCP (from 10.0.12.133)                         │
│  └─ PC-Cat-2: DHCP (from 10.0.12.133)                         │
│                                                                 │
│  DHCP Pool Range: 10.0.8.10 - 10.0.11.254                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        DOG TRIBE                                │
│                    Network: 10.0.0.0/21                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Router: R-Dog                                                  │
│  ├─ GigabitEthernet0/0 (to Elephant): 10.0.12.154/30          │
│  └─ GigabitEthernet0/1 (LAN): 10.0.0.1/21                     │
│                                                                 │
│  Switch: SW-Dog (Layer 2)                                      │
│                                                                 │
│  Chief's Computer (Static IP):                                 │
│  └─ Dog Chief PC: 10.0.0.2                                    │
│     Email: dogchief@animals.com                                │
│                                                                 │
│  End Devices (DHCP):                                           │
│  ├─ PC-Dog-1: DHCP (from 10.0.12.133)                         │
│  └─ PC-Dog-2: DHCP (from 10.0.12.133)                         │
│                                                                 │
│  DHCP Pool Range: 10.0.0.10 - 10.0.7.254                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

====================================================================
                    CONNECTIVITY SUMMARY
====================================================================

Point-to-Point Links:
├─ Lion ↔ Elephant: 10.0.12.144/30
│  ├─ R-Lion Gi0/0/0: 10.0.12.145
│  └─ R-Elephant Gi0/0/0: 10.0.12.146
│
├─ Elephant ↔ Cat: 10.0.12.148/30
│  ├─ R-Elephant Gi0/1: 10.0.12.149
│  └─ R-Cat Gi0/0: 10.0.12.150
│
└─ Elephant ↔ Dog: 10.0.12.152/30
   ├─ R-Elephant Gi0/2: 10.0.12.153
   └─ R-Dog Gi0/0: 10.0.12.154

Routing Protocols:
├─ Lion: Static routing ONLY
├─ Elephant: OSPF + static routes to Lion
├─ Cat: OSPF
└─ Dog: OSPF

Services (All in Lion Tribe):
├─ DNS: 10.0.12.131 (resolves www.animals.com, email domains)
├─ Web: 10.0.12.130 (www.animals.com)
├─ Email: 10.0.12.132 (handles all @animals.com emails)
└─ DHCP: 10.0.12.133 (serves all four tribes via DHCP relay)
```

## Implementation Notes

### For Packet Tracer:
1. **Routers**: Use 2911 or 2901 series routers
2. **Switches**: Use 2960 series switches
3. **Servers**: Use Server-PT devices
4. **PCs**: Use PC-PT devices
5. **Connections**: 
   - Copper Straight-Through for PC-to-Switch
   - Copper Cross-Over or Auto for Switch-to-Router
   - Serial or Copper Straight-Through for Router-to-Router

### Labels to Add in Packet Tracer:
- Use Notes tool to label each network segment with its network address
- Label each device with its hostname
- Label routers with interface IPs on the topology
