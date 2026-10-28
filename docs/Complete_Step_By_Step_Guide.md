# Animal Kingdom - Complete Step-by-Step Implementation Guide

**Estimated Time: 3-4 hours**

---

## 📋 NETWORK DESIGN OVERVIEW

### Tribes & Requirements
- **Lion Tribe**: 3 devices + 4 servers (hosts all services)
- **Elephant Tribe**: 100 devices (central hub)
- **Cat Tribe**: 800 devices
- **Dog Tribe**: 1200 devices

### Network Addresses (VLSM)
| Tribe | Network | Subnet Mask | CIDR | Usable IPs |
|-------|---------|-------------|------|------------|
| Dog | 10.0.0.0 | 255.255.248.0 | /21 | 2046 |
| Cat | 10.0.8.0 | 255.255.252.0 | /22 | 1022 |
| Elephant | 10.0.12.0 | 255.255.255.128 | /25 | 126 |
| Lion | 10.0.12.128 | 255.255.255.240 | /28 | 14 |
| Lion-Elephant | 10.0.12.144 | 255.255.255.252 | /30 | 2 |
| Elephant-Cat | 10.0.12.148 | 255.255.255.252 | /30 | 2 |
| Elephant-Dog | 10.0.12.152 | 255.255.255.252 | /30 | 2 |

---

## STEP 1: BUILD THE TOPOLOGY (30 minutes)

### 1.1 Add Routers
1. Open **Cisco Packet Tracer**
2. From bottom menu: **Network Devices → Routers**
3. Drag **4x Router-2911** (or 2901) to workspace
4. Click each router → **Config** tab → **Display Name**
   - Router 1: `R-Lion`
   - Router 2: `R-Elephant`
   - Router 3: `R-Cat`
   - Router 4: `R-Dog`

### 1.2 Add Switches
1. From bottom menu: **Network Devices → Switches**
2. Drag **4x Switch-2960** to workspace
3. Rename them:
   - Switch 1: `SW-Lion`
   - Switch 2: `SW-Elephant`
   - Switch 3: `SW-Cat`
   - Switch 4: `SW-Dog`

### 1.3 Add Servers (Lion Tribe Only)
1. From bottom menu: **End Devices → Server**
2. Drag **4x Server-PT** near SW-Lion
3. Rename them:
   - Server 1: `DNS-Server`
   - Server 2: `Web-Server`
   - Server 3: `Email-Server`
   - Server 4: `DHCP-Server`

### 1.4 Add PCs
Drag **12x PC-PT** from **End Devices → End Devices**

**Lion Tribe (3 PCs):**
- `LionKing-PC`
- `PC-Lion-1`
- `PC-Lion-2`

**Elephant Tribe (3 PCs):**
- `ElephantChief-PC`
- `PC-Elephant-1`
- `PC-Elephant-2`

**Cat Tribe (3 PCs):**
- `CatChief-PC`
- `PC-Cat-1`
- `PC-Cat-2`

**Dog Tribe (3 PCs):**
- `DogChief-PC`
- `PC-Dog-1`
- `PC-Dog-2`

### 1.5 Connect Devices

**Use Copper Straight-Through cable for all connections**

**Lion Tribe Connections:**
1. R-Lion Gi0/1 ↔ SW-Lion Fa0/1
2. DNS-Server Fa0 ↔ SW-Lion Fa0/2
3. Web-Server Fa0 ↔ SW-Lion Fa0/3
4. Email-Server Fa0 ↔ SW-Lion Fa0/4
5. DHCP-Server Fa0 ↔ SW-Lion Fa0/5
6. LionKing-PC Fa0 ↔ SW-Lion Fa0/6
7. PC-Lion-1 Fa0 ↔ SW-Lion Fa0/7
8. PC-Lion-2 Fa0 ↔ SW-Lion Fa0/8

**Elephant Tribe Connections:**
1. R-Elephant Gi0/0 ↔ SW-Elephant Fa0/1
2. ElephantChief-PC Fa0 ↔ SW-Elephant Fa0/2
3. PC-Elephant-1 Fa0 ↔ SW-Elephant Fa0/3
4. PC-Elephant-2 Fa0 ↔ SW-Elephant Fa0/4

**Cat Tribe Connections:**
1. R-Cat Gi0/1 ↔ SW-Cat Fa0/1
2. CatChief-PC Fa0 ↔ SW-Cat Fa0/2
3. PC-Cat-1 Fa0 ↔ SW-Cat Fa0/3
4. PC-Cat-2 Fa0 ↔ SW-Cat Fa0/4

**Dog Tribe Connections:**
1. R-Dog Gi0/1 ↔ SW-Dog Fa0/1
2. DogChief-PC Fa0 ↔ SW-Dog Fa0/2
3. PC-Dog-1 Fa0 ↔ SW-Dog Fa0/3
4. PC-Dog-2 Fa0 ↔ SW-Dog Fa0/4

**Router-to-Router Connections:**
1. R-Lion Gi0/0/0 ↔ R-Elephant Gi0/0/0
2. R-Elephant Gi0/1 ↔ R-Cat Gi0/0
3. R-Elephant Gi0/2 ↔ R-Dog Gi0/0

### 1.6 Organize Layout
- Place Lion at top
- Place Elephant in middle
- Place Cat on bottom-left, Dog on bottom-right
- Use **Place Note** tool to label network segments

---

## STEP 2: CONFIGURE ROUTERS (60 minutes)

### 2.1 Configure R-Lion

1. Click **R-Lion** → **CLI** tab
2. Press **Enter**, type `no` when asked about initial configuration
3. Copy and paste these commands:

```cisco
enable
configure terminal
hostname R-Lion

! Configure interface to Elephant
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

! Static routes to all networks
ip route 10.0.12.0 255.255.255.128 10.0.12.146
ip route 10.0.8.0 255.255.252.0 10.0.12.146
ip route 10.0.0.0 255.255.248.0 10.0.12.146
ip route 10.0.12.148 255.255.255.252 10.0.12.146
ip route 10.0.12.152 255.255.255.252 10.0.12.146

end
write memory
```

4. Verify: Type `show ip interface brief` - Both interfaces should show "up/up"

---

### 2.2 Configure R-Elephant

1. Click **R-Elephant** → **CLI** tab
2. Type `no` when asked about initial configuration
3. Copy and paste these commands:

```cisco
enable
configure terminal
hostname R-Elephant

! Configure interface to Lion
interface GigabitEthernet0/0/0
 description Link to R-Lion
 ip address 10.0.12.146 255.255.255.252
 no shutdown
 exit

! Configure interface to Cat
interface GigabitEthernet0/1
 description Link to R-Cat
 ip address 10.0.12.149 255.255.255.252
 no shutdown
 exit

! Configure interface to Dog
interface GigabitEthernet0/2
 description Link to R-Dog
 ip address 10.0.12.153 255.255.255.252
 no shutdown
 exit

! Configure interface to Elephant LAN
interface GigabitEthernet0/0
 description Elephant Tribe LAN
 ip address 10.0.12.1 255.255.255.128
 ip helper-address 10.0.12.133
 no shutdown
 exit

! Configure OSPF
router ospf 1
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.127 area 0
 network 10.0.12.148 0.0.0.3 area 0
 network 10.0.12.152 0.0.0.3 area 0
 passive-interface GigabitEthernet0/0/0
 exit

! Static route to Lion and redistribute
ip route 10.0.12.128 255.255.255.240 10.0.12.145
router ospf 1
 redistribute static subnets
 exit

end
write memory
```

4. Verify: Type `show ip ospf neighbor` - Wait 30 seconds, should see Cat and Dog

---

### 2.3 Configure R-Cat

1. Click **R-Cat** → **CLI** tab
2. Type `no` when asked about initial configuration
3. Copy and paste these commands:

```cisco
enable
configure terminal
hostname R-Cat

! Configure interface to Elephant
interface GigabitEthernet0/0
 description Link to R-Elephant
 ip address 10.0.12.150 255.255.255.252
 no shutdown
 exit

! Configure interface to Cat LAN
interface GigabitEthernet0/1
 description Cat Tribe LAN
 ip address 10.0.8.1 255.255.252.0
 ip helper-address 10.0.12.133
 no shutdown
 exit

! Configure OSPF
router ospf 1
 router-id 3.3.3.3
 network 10.0.8.0 0.0.3.255 area 0
 network 10.0.12.148 0.0.0.3 area 0
 exit

end
write memory
```

4. Verify: Type `show ip interface brief`

---

### 2.4 Configure R-Dog

1. Click **R-Dog** → **CLI** tab
2. Type `no` when asked about initial configuration
3. Copy and paste these commands:

```cisco
enable
configure terminal
hostname R-Dog

! Configure interface to Elephant
interface GigabitEthernet0/0
 description Link to R-Elephant
 ip address 10.0.12.154 255.255.255.252
 no shutdown
 exit

! Configure interface to Dog LAN
interface GigabitEthernet0/1
 description Dog Tribe LAN
 ip address 10.0.0.1 255.255.248.0
 ip helper-address 10.0.12.133
 no shutdown
 exit

! Configure OSPF
router ospf 1
 router-id 4.4.4.4
 network 10.0.0.0 0.0.7.255 area 0
 network 10.0.12.152 0.0.0.3 area 0
 exit

end
write memory
```

4. Verify: Type `show ip route` - Should see all networks

---

## STEP 3: CONFIGURE SERVERS (45 minutes)

### 3.1 Configure DNS-Server (10.0.12.131)

1. Click **DNS-Server** → **Desktop** tab → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.131`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

2. Click **Services** tab → **DNS**
   - Turn **DNS Service ON**

3. Add these DNS records (one at a time):

| Name | Type | Address |
|------|------|---------|
| www.animals.com | A Record | 10.0.12.130 |
| animals.com | A Record | 10.0.12.130 |
| mail.animals.com | A Record | 10.0.12.132 |
| dns.animals.com | A Record | 10.0.12.131 |

**For each record:**
- Type the name in "Name" field
- Select "A Record" from dropdown
- Enter the address
- Click **Add**

---

### 3.2 Configure Web-Server (10.0.12.130)

1. Click **Web-Server** → **Desktop** tab → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.130`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

2. Click **Services** tab → **HTTP**
   - Turn **HTTP Service ON**

3. Click **Edit** next to index.html and replace content with:

```html
<html>
<head><title>Animal Kingdom</title></head>
<body style="text-align:center; font-family:Arial; padding:50px;">
<h1 style="color:green; font-size:48px;">Welcome to the Animal Kingdom!</h1>
<p>United tribes of Lion, Elephant, Cat, and Dog</p>
</body>
</html>
```

4. Click **Save** (important!)

---

### 3.3 Configure Email-Server (10.0.12.132)

1. Click **Email-Server** → **Desktop** tab → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.132`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

2. Click **Services** tab → **EMAIL**
   - Turn **Email Service ON**
   - Set Domain Name: `animals.com`

3. Add user accounts (click **Set** after EACH user):

| User | Password |
|------|----------|
| lionking | lion123 |
| elephantchief | elephant123 |
| catchief | cat123 |
| dogchief | dog123 |

**For each user:**
- Enter username in "User" field
- Enter password in "Password" field
- Click **+** button
- Repeat for all 4 users

---

### 3.4 Configure DHCP-Server (10.0.12.133)

1. Click **DHCP-Server** → **Desktop** tab → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.133`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

2. Click **Services** tab → **DHCP**
   - Turn **DHCP Service ON**

3. Create Pool 1 - DOG-POOL:
   - Pool Name: `DOG-POOL`
   - Default Gateway: `10.0.0.1`
   - DNS Server: `10.0.12.131`
   - Start IP Address: `10.0.0.10`
   - Subnet Mask: `255.255.248.0`
   - Maximum Number of Users: `2036`
   - Click **Add**

4. Create Pool 2 - CAT-POOL:
   - Pool Name: `CAT-POOL`
   - Default Gateway: `10.0.8.1`
   - DNS Server: `10.0.12.131`
   - Start IP Address: `10.0.8.10`
   - Subnet Mask: `255.255.252.0`
   - Maximum Number of Users: `1012`
   - Click **Add**

5. Create Pool 3 - ELEPHANT-POOL:
   - Pool Name: `ELEPHANT-POOL`
   - Default Gateway: `10.0.12.1`
   - DNS Server: `10.0.12.131`
   - Start IP Address: `10.0.12.10`
   - Subnet Mask: `255.255.255.128`
   - Maximum Number of Users: `116`
   - Click **Add**

---

## STEP 4: CONFIGURE CHIEF PCs (20 minutes)

### 4.1 Configure LionKing-PC
1. Click **LionKing-PC** → **Desktop** → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.134`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

### 4.2 Configure ElephantChief-PC
1. Click **ElephantChief-PC** → **Desktop** → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.12.2`
   - Subnet Mask: `255.255.255.128`
   - Default Gateway: `10.0.12.1`
   - DNS Server: `10.0.12.131`

### 4.3 Configure CatChief-PC
1. Click **CatChief-PC** → **Desktop** → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.8.2`
   - Subnet Mask: `255.255.252.0`
   - Default Gateway: `10.0.8.1`
   - DNS Server: `10.0.12.131`

### 4.4 Configure DogChief-PC
1. Click **DogChief-PC** → **Desktop** → **IP Configuration**
   - Select **Static**
   - IP Address: `10.0.0.2`
   - Subnet Mask: `255.255.248.0`
   - Default Gateway: `10.0.0.1`
   - DNS Server: `10.0.12.131`

---

## STEP 5: CONFIGURE REGULAR PCs (15 minutes)

### 5.1 Lion Tribe PCs (Static)
**PC-Lion-1:**
- Desktop → IP Configuration → **Static**
- IP: `10.0.12.135`, Mask: `255.255.255.240`
- Gateway: `10.0.12.129`, DNS: `10.0.12.131`

**PC-Lion-2:**
- Desktop → IP Configuration → **Static**
- IP: `10.0.12.136`, Mask: `255.255.255.240`
- Gateway: `10.0.12.129`, DNS: `10.0.12.131`

### 5.2 Elephant Tribe PCs (DHCP)
**PC-Elephant-1:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP (should get 10.0.12.10 or similar)

**PC-Elephant-2:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP

### 5.3 Cat Tribe PCs (DHCP)
**PC-Cat-1:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP (should get 10.0.8.10 or similar)

**PC-Cat-2:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP

### 5.4 Dog Tribe PCs (DHCP)
**PC-Dog-1:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP (should get 10.0.0.10 or similar)

**PC-Dog-2:**
- Desktop → IP Configuration → Select **DHCP**
- Wait for IP

---

## STEP 6: CONFIGURE EMAIL ON CHIEF PCs (15 minutes)

### 6.1 LionKing-PC Email
1. Click **LionKing-PC** → **Desktop** → **Email**
2. Configure:
   - Your Name: `Lion King`
   - Email Address: `lionking@animals.com`
   - Incoming Mail Server: `10.0.12.132`
   - Outgoing Mail Server: `10.0.12.132`
   - User Name: `lionking`
   - Password: `lion123`
3. Click **Save**

### 6.2 ElephantChief-PC Email
1. Click **ElephantChief-PC** → **Desktop** → **Email**
2. Configure:
   - Your Name: `Elephant Chief`
   - Email Address: `elephantchief@animals.com`
   - Incoming Mail Server: `10.0.12.132`
   - Outgoing Mail Server: `10.0.12.132`
   - User Name: `elephantchief`
   - Password: `elephant123`
3. Click **Save**

### 6.3 CatChief-PC Email
1. Click **CatChief-PC** → **Desktop** → **Email**
2. Configure:
   - Your Name: `Cat Chief`
   - Email Address: `catchief@animals.com`
   - Incoming Mail Server: `10.0.12.132`
   - Outgoing Mail Server: `10.0.12.132`
   - User Name: `catchief`
   - Password: `cat123`
3. Click **Save**

### 6.4 DogChief-PC Email
1. Click **DogChief-PC** → **Desktop** → **Email**
2. Configure:
   - Your Name: `Dog Chief`
   - Email Address: `dogchief@animals.com`
   - Incoming Mail Server: `10.0.12.132`
   - Outgoing Mail Server: `10.0.12.132`
   - User Name: `dogchief`
   - Password: `dog123`
3. Click **Save**

---

## STEP 7: TEST EVERYTHING (30 minutes)

### 7.1 Test Basic Connectivity
From **any PC** → **Desktop** → **Command Prompt**:

```
ping 10.0.12.130    (Web Server - should work)
ping 10.0.12.131    (DNS Server - should work)
ping 10.0.12.132    (Email Server - should work)
ping 10.0.12.133    (DHCP Server - should work)
```

✓ All should reply successfully

### 7.2 Test Inter-Tribe Connectivity
From **DogChief-PC** → **Command Prompt**:

```
ping 10.0.0.1       (Dog router - should work)
ping 10.0.8.2       (Cat Chief - should work)
ping 10.0.12.2      (Elephant Chief - should work)
ping 10.0.12.134    (Lion King - should work)
```

✓ All should reply successfully

### 7.3 Test DNS Resolution
From **any PC** → **Command Prompt**:

```
nslookup www.animals.com
```

✓ Should return: **10.0.12.130**

### 7.4 Test Website
From **any PC** → **Desktop** → **Web Browser**:
1. Type in address bar: `www.animals.com`
2. Press **Go**

✓ Should display: **"Welcome to the Animal Kingdom!"**

### 7.5 Test Email
1. On **LionKing-PC** → **Desktop** → **Email**
2. Click **Compose**
3. Fill in:
   - To: `dogchief@animals.com`
   - Subject: `Test Email`
   - Message: `Hello from Lion King!`
4. Click **Send**

5. On **DogChief-PC** → **Desktop** → **Email**
6. Click **Receive**

✓ Email should appear in inbox

### 7.6 Test DHCP
1. Pick any DHCP PC (like PC-Dog-1)
2. **Desktop** → **IP Configuration**
3. Toggle to **Static**, then back to **DHCP**
4. Verify new IP is assigned

✓ Should receive IP from correct range

---

## STEP 8: FINAL VERIFICATION CHECKLIST

### Router Verification
On **R-Elephant** → **CLI**:
```
show ip ospf neighbor
```
✓ Should show R-Cat and R-Dog as neighbors

On **R-Lion** → **CLI**:
```
show ip route
```
✓ Should show all 7 networks

### Comprehensive Ping Test
From **CatChief-PC** → **Command Prompt**, ping ALL these:
```
ping 10.0.0.2       (Dog Chief)
ping 10.0.12.2      (Elephant Chief)
ping 10.0.12.134    (Lion King)
ping 10.0.12.130    (Web Server)
ping 10.0.12.131    (DNS Server)
ping 10.0.12.132    (Email Server)
```

✓ All must succeed for full marks

---

## STEP 9: CREATE DOCUMENTATION (30 minutes)

### 9.1 Add Network Labels
1. Click **Place Note** tool (bottom toolbar)
2. Add labels for each network segment:
   - `Lion LAN: 10.0.12.128/28`
   - `Elephant LAN: 10.0.12.0/25`
   - `Cat LAN: 10.0.8.0/22`
   - `Dog LAN: 10.0.0.0/21`
   - `Lion-Elephant: 10.0.12.144/30`
   - `Elephant-Cat: 10.0.12.148/30`
   - `Elephant-Dog: 10.0.12.152/30`

### 9.2 Save Packet Tracer File
1. **File** → **Save As**
2. Name: `AnimalKingdom_YourName.pkt`
3. Save to project folder

### 9.3 Take Screenshot
1. Use **Print Screen** or Snipping Tool
2. Capture entire topology with labels
3. Save as `Topology_Diagram.png`

### 9.4 Export Router Configurations
For each router, **CLI** → Type:
```
show running-config
```
Copy output and save to separate text files:
- `R-Lion_Config.txt`
- `R-Elephant_Config.txt`
- `R-Cat_Config.txt`
- `R-Dog_Config.txt`

### 9.5 Take Test Screenshots
Capture screenshots of:
1. Successful ping from one tribe to another
2. Website displaying in browser
3. Email sent/received between chiefs
4. DHCP IP assignment

---

## COMPLETE IP ADDRESS TABLE

### Servers (Lion Tribe)
| Device | IP | Subnet Mask | Gateway | DNS |
|--------|-----|-------------|---------|-----|
| DNS-Server | 10.0.12.131 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |
| Web-Server | 10.0.12.130 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |
| Email-Server | 10.0.12.132 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |
| DHCP-Server | 10.0.12.133 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |

### Tribal Chiefs
| Device | IP | Subnet Mask | Gateway | DNS |
|--------|-----|-------------|---------|-----|
| LionKing-PC | 10.0.12.134 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |
| ElephantChief-PC | 10.0.12.2 | 255.255.255.128 | 10.0.12.1 | 10.0.12.131 |
| CatChief-PC | 10.0.8.2 | 255.255.252.0 | 10.0.8.1 | 10.0.12.131 |
| DogChief-PC | 10.0.0.2 | 255.255.248.0 | 10.0.0.1 | 10.0.12.131 |

### Lion Regular PCs
| Device | IP | Subnet Mask | Gateway | DNS |
|--------|-----|-------------|---------|-----|
| PC-Lion-1 | 10.0.12.135 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |
| PC-Lion-2 | 10.0.12.136 | 255.255.255.240 | 10.0.12.129 | 10.0.12.131 |

### Other Regular PCs (DHCP)
| Device | IP Assignment |
|--------|---------------|
| PC-Elephant-1 | DHCP (10.0.12.10+) |
| PC-Elephant-2 | DHCP (10.0.12.10+) |
| PC-Cat-1 | DHCP (10.0.8.10+) |
| PC-Cat-2 | DHCP (10.0.8.10+) |
| PC-Dog-1 | DHCP (10.0.0.10+) |
| PC-Dog-2 | DHCP (10.0.0.10+) |

### Router Interfaces
| Router | Interface | IP | Subnet Mask | Description |
|--------|-----------|-----|-------------|-------------|
| R-Lion | Gi0/0/0 | 10.0.12.145 | 255.255.255.252 | To R-Elephant |
| R-Lion | Gi0/1 | 10.0.12.129 | 255.255.255.240 | Lion LAN |
| R-Elephant | Gi0/0/0 | 10.0.12.146 | 255.255.255.252 | To R-Lion |
| R-Elephant | Gi0/1 | 10.0.12.149 | 255.255.255.252 | To R-Cat |
| R-Elephant | Gi0/2 | 10.0.12.153 | 255.255.255.252 | To R-Dog |
| R-Elephant | Gi0/0 | 10.0.12.1 | 255.255.255.128 | Elephant LAN |
| R-Cat | Gi0/0 | 10.0.12.150 | 255.255.255.252 | To R-Elephant |
| R-Cat | Gi0/1 | 10.0.8.1 | 255.255.252.0 | Cat LAN |
| R-Dog | Gi0/0 | 10.0.12.154 | 255.255.255.252 | To R-Elephant |
| R-Dog | Gi0/1 | 10.0.0.1 | 255.255.248.0 | Dog LAN |

---

## TROUBLESHOOTING COMMON ISSUES

### Issue: "Request timed out" when pinging
**Solutions:**
1. Check all cables are connected (green triangles on both ends)
2. Verify interfaces are up: `show ip interface brief`
3. Check IP addresses are correct
4. Wait 60 seconds for OSPF to converge

### Issue: DHCP not assigning IPs
**Solutions:**
1. Verify DHCP service is ON on DHCP-Server
2. Check `ip helper-address 10.0.12.133` on router interfaces
3. Verify DHCP pools are configured correctly
4. Ping DHCP server from router: `ping 10.0.12.133`

### Issue: DNS not resolving
**Solutions:**
1. Verify DNS service is ON on DNS-Server
2. Check DNS records are added correctly
3. Verify PCs have DNS server set to 10.0.12.131
4. Test: `ping 10.0.12.131` first

### Issue: Website doesn't load
**Solutions:**
1. Test DNS: `nslookup www.animals.com` (should return 10.0.12.130)
2. Verify HTTP service is ON
3. Check index.html was edited and SAVED
4. Try IP directly: `http://10.0.12.130`

### Issue: Email not working
**Solutions:**
1. Verify email service is ON
2. Check domain is set to `animals.com`
3. Verify all 4 user accounts exist
4. Check email client settings (server should be 10.0.12.132)
5. Ensure credentials match exactly

### Issue: OSPF neighbors not forming
**Solutions:**
1. Wait 40 seconds after router configuration
2. Check OSPF network statements
3. Verify interface IPs are correct
4. Ensure both routers have OSPF configured
5. Check: `show ip ospf neighbor`

---

## FINAL SUBMISSION CHECKLIST

- [ ] .pkt file saved and tested
- [ ] Topology screenshot with network labels
- [ ] All devices can ping each other
- [ ] DNS resolves www.animals.com
- [ ] Website displays "Welcome to the Animal Kingdom!"
- [ ] Tribal chiefs can send/receive emails
- [ ] DHCP assigns IPs correctly
- [ ] Router configurations exported
- [ ] Test screenshots captured
- [ ] Work distribution documented
- [ ] PDF document created with:
  - [ ] VLSM tree
  - [ ] IP address table
  - [ ] Router configurations
  - [ ] Test results

---

## YOU'RE DONE! 🎉

Your Animal Kingdom network is complete. All tribes can now communicate!

**Total Implementation Time: 3-4 hours**

Good luck! 🦁🐘🐱🐶
