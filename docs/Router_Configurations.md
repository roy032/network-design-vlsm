# Animal Kingdom - Router Configuration Commands

## R-LION Configuration (Static Routing Only)

```cisco
! ============================================
! R-LION - Lion Tribe Router
! Static Routing Only (As per requirements)
! ============================================

enable
configure terminal

! Set hostname
hostname R-Lion

! Configure interface to Elephant (Point-to-Point)
interface GigabitEthernet0/0/0
 description Link to R-Elephant
 ip address 10.0.12.145 255.255.255.252
 no shutdown
 exit

! Configure interface to Lion LAN
interface GigabitEthernet0/1
 description Lion Tribe LAN
 ip address 10.0.12.129 255.255.255.240
 no shutdown
 exit

! ============================================
! STATIC ROUTES - Lion uses ONLY static routing
! ============================================

! Route to Elephant Tribe LAN
ip route 10.0.12.0 255.255.255.128 10.0.12.146

! Route to Cat Tribe LAN
ip route 10.0.8.0 255.255.252.0 10.0.12.146

! Route to Dog Tribe LAN
ip route 10.0.0.0 255.255.248.0 10.0.12.146

! Route to Elephant-Cat Link
ip route 10.0.12.148 255.255.255.252 10.0.12.146

! Route to Elephant-Dog Link
ip route 10.0.12.152 255.255.255.252 10.0.12.146

! ============================================
! Save configuration
! ============================================
end
write memory
```

---

## R-ELEPHANT Configuration (OSPF + Static to Lion)

```cisco
! ============================================
! R-ELEPHANT - Elephant Tribe Router
! OSPF for Cat/Dog, Static for Lion
! ============================================

enable
configure terminal

! Set hostname
hostname R-Elephant

! Configure interface to Lion (Point-to-Point)
interface GigabitEthernet0/0/0
 description Link to R-Lion
 ip address 10.0.12.146 255.255.255.252
 no shutdown
 exit

! Configure interface to Cat (Point-to-Point)
interface GigabitEthernet0/1
 description Link to R-Cat
 ip address 10.0.12.149 255.255.255.252
 no shutdown
 exit

! Configure interface to Dog (Point-to-Point)
interface GigabitEthernet0/2
 description Link to R-Dog
 ip address 10.0.12.153 255.255.255.252
 no shutdown
 exit

! Configure interface to Elephant LAN
interface GigabitEthernet0/0
 description Elephant Tribe LAN
 ip address 10.0.12.1 255.255.255.128
 no shutdown
 exit

! ============================================
! DHCP RELAY - Forward DHCP requests to Lion
! ============================================
interface GigabitEthernet0/0
 ip helper-address 10.0.12.133
 exit

! ============================================
! OSPF CONFIGURATION
! ============================================
router ospf 1
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.127 area 0
 network 10.0.12.148 0.0.0.3 area 0
 network 10.0.12.152 0.0.0.3 area 0
 passive-interface GigabitEthernet0/0/0
 exit

! ============================================
! STATIC ROUTES - To Lion network (not in OSPF)
! ============================================
ip route 10.0.12.128 255.255.255.240 10.0.12.145

! Redistribute static routes into OSPF so Cat/Dog can reach Lion
router ospf 1
 redistribute static subnets
 exit

! ============================================
! Save configuration
! ============================================
end
write memory
```

---

## R-CAT Configuration (OSPF)

```cisco
! ============================================
! R-CAT - Cat Tribe Router
! OSPF Dynamic Routing
! ============================================

enable
configure terminal

! Set hostname
hostname R-Cat

! Configure interface to Elephant (Point-to-Point)
interface GigabitEthernet0/0
 description Link to R-Elephant
 ip address 10.0.12.150 255.255.255.252
 no shutdown
 exit

! Configure interface to Cat LAN
interface GigabitEthernet0/1
 description Cat Tribe LAN
 ip address 10.0.8.1 255.255.252.0
 no shutdown
 exit

! ============================================
! DHCP RELAY - Forward DHCP requests to Lion
! ============================================
interface GigabitEthernet0/1
 ip helper-address 10.0.12.133
 exit

! ============================================
! OSPF CONFIGURATION
! ============================================
router ospf 1
 router-id 3.3.3.3
 network 10.0.8.0 0.0.3.255 area 0
 network 10.0.12.148 0.0.0.3 area 0
 exit

! ============================================
! Save configuration
! ============================================
end
write memory
```

---

## R-DOG Configuration (OSPF)

```cisco
! ============================================
! R-DOG - Dog Tribe Router
! OSPF Dynamic Routing
! ============================================

enable
configure terminal

! Set hostname
hostname R-Dog

! Configure interface to Elephant (Point-to-Point)
interface GigabitEthernet0/0
 description Link to R-Elephant
 ip address 10.0.12.154 255.255.255.252
 no shutdown
 exit

! Configure interface to Dog LAN
interface GigabitEthernet0/1
 description Dog Tribe LAN
 ip address 10.0.0.1 255.255.248.0
 no shutdown
 exit

! ============================================
! DHCP RELAY - Forward DHCP requests to Lion
! ============================================
interface GigabitEthernet0/1
 ip helper-address 10.0.12.133
 exit

! ============================================
! OSPF CONFIGURATION
! ============================================
router ospf 1
 router-id 4.4.4.4
 network 10.0.0.0 0.0.7.255 area 0
 network 10.0.12.152 0.0.0.3 area 0
 exit

! ============================================
! Save configuration
! ============================================
end
write memory
```

---

## Verification Commands

### After configuring all routers, use these commands to verify:

```cisco
! Show IP interface brief - Check all interfaces are up
show ip interface brief

! Show IP route - Verify routing table
show ip route

! Show OSPF neighbors (on R-Elephant, R-Cat, R-Dog)
show ip ospf neighbor

! Show OSPF database
show ip ospf database

! Show running configuration
show running-config

! Test connectivity - Ping from router to router
ping 10.0.12.145    ! Ping R-Lion from R-Elephant
ping 10.0.12.150    ! Ping R-Cat from R-Elephant
ping 10.0.12.154    ! Ping R-Dog from R-Elephant

! Test connectivity to servers
ping 10.0.12.130    ! Ping Web Server
ping 10.0.12.131    ! Ping DNS Server
ping 10.0.12.132    ! Ping Email Server
ping 10.0.12.133    ! Ping DHCP Server
```

---

## Configuration Summary

### R-Lion (Static Routing)
- **Interfaces**: Gi0/0 (to Elephant), Gi0/1 (LAN)
- **Routing**: Static routes to all networks
- **Special**: No dynamic routing protocols

### R-Elephant (OSPF + Static)
- **Interfaces**: Gi0/0/0 (to Lion), Gi0/1 (to Cat), Gi0/2 (to Dog), Gi0/0 (LAN)
- **Routing**: OSPF for Cat/Dog/Elephant networks, Static for Lion
- **Special**: DHCP relay, redistributes static routes into OSPF

### R-Cat (OSPF)
- **Interfaces**: Gi0/0 (to Elephant), Gi0/1 (LAN)
- **Routing**: OSPF Area 0
- **Special**: DHCP relay

### R-Dog (OSPF)
- **Interfaces**: Gi0/0 (to Elephant), Gi0/1 (LAN)
- **Routing**: OSPF Area 0
- **Special**: DHCP relay

---

## Routing Protocol Decisions

**Why OSPF?**
- Link-state protocol suitable for hierarchical networks
- Fast convergence
- Scalable for the Animal Kingdom network
- Area 0 (backbone) includes all tribes except Lion

**Why Static for Lion?**
- Per project requirements: "Lion tribe will only use static routing"
- Simple configuration for small network
- All other routers learn Lion's routes via redistribution on R-Elephant

**Why DHCP Relay?**
- Centralized DHCP server in Lion tribe
- All tribes use the same DHCP server (10.0.12.133)
- `ip helper-address` forwards DHCP broadcasts across router boundaries
