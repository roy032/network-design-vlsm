# Animal Kingdom - Cisco Packet Tracer Implementation Guide

## Step-by-Step Implementation Instructions

---

## PHASE 1: Create Network Topology (30-45 minutes)

### Step 1: Add Network Devices

1. **Open Cisco Packet Tracer**
2. **Add Routers** (from Network Devices → Routers)
   - Add **4x Router-2911** (or 2901)
   - Label them: R-Lion, R-Elephant, R-Cat, R-Dog
   - Click on each router → Display Name → Change name

3. **Add Switches** (from Network Devices → Switches)
   - Add **4x Switch-2960** (24TT or 24PT)
   - Label them: SW-Lion, SW-Elephant, SW-Cat, SW-Dog

4. **Add Servers** (from End Devices → Servers)
   - Add **4x Server-PT** in Lion area
   - Label them: DNS-Server, Web-Server, Email-Server, DHCP-Server

5. **Add PCs** (from End Devices → End Devices)
   - Add **1 PC** for each tribal chief (4 total)
   - Add **2 PCs** per tribe for regular users (8 total)
   - **Total: 12 PCs**
   
   **Labeling:**
   - LionKing-PC, PC-Lion-1, PC-Lion-2
   - ElephantChief-PC, PC-Elephant-1, PC-Elephant-2
   - CatChief-PC, PC-Cat-1, PC-Cat-2
   - DogChief-PC, PC-Dog-1, PC-Dog-2

### Step 2: Connect Devices

**Connection Type Guide:**
- **PC to Switch**: Copper Straight-Through
- **Switch to Router**: Copper Straight-Through (or Auto-MDIX)
- **Router to Router**: Copper Straight-Through (GigabitEthernet) or Serial DCE/DTE

**Connections to Make:**

#### Lion Tribe
- SW-Lion FastEthernet0/1 → R-Lion GigabitEthernet0/1
- DNS-Server FastEthernet0 → SW-Lion FastEthernet0/2
- Web-Server FastEthernet0 → SW-Lion FastEthernet0/3
- Email-Server FastEthernet0 → SW-Lion FastEthernet0/4
- DHCP-Server FastEthernet0 → SW-Lion FastEthernet0/5
- LionKing-PC FastEthernet0 → SW-Lion FastEthernet0/6
- PC-Lion-1 FastEthernet0 → SW-Lion FastEthernet0/7
- PC-Lion-2 FastEthernet0 → SW-Lion FastEthernet0/8

#### Elephant Tribe
- SW-Elephant FastEthernet0/1 → R-Elephant GigabitEthernet1/0
- ElephantChief-PC FastEthernet0 → SW-Elephant FastEthernet0/2
- PC-Elephant-1 FastEthernet0 → SW-Elephant FastEthernet0/3
- PC-Elephant-2 FastEthernet0 → SW-Elephant FastEthernet0/4

#### Cat Tribe
- SW-Cat FastEthernet0/1 → R-Cat GigabitEthernet0/1
- CatChief-PC FastEthernet0 → SW-Cat FastEthernet0/2
- PC-Cat-1 FastEthernet0 → SW-Cat FastEthernet0/3
- PC-Cat-2 FastEthernet0 → SW-Cat FastEthernet0/4

#### Dog Tribe
- SW-Dog FastEthernet0/1 → R-Dog GigabitEthernet0/1
- DogChief-PC FastEthernet0 → SW-Dog FastEthernet0/2
- PC-Dog-1 FastEthernet0 → SW-Dog FastEthernet0/3
- PC-Dog-2 FastEthernet0 → SW-Dog FastEthernet0/4

#### Router-to-Router Links
- R-Lion GigabitEthernet0/0 → R-Elephant GigabitEthernet0/0
- R-Elephant GigabitEthernet0/1 → R-Cat GigabitEthernet0/0
- R-Elephant GigabitEthernet0/2 → R-Dog GigabitEthernet0/0

### Step 3: Organize Layout
- Arrange devices logically (Lion at top, Elephant in middle, Cat and Dog at bottom)
- Use the **Note** tool to label each network segment with network addresses
- Add text boxes for clarity

---

## PHASE 2: Configure Routers (45-60 minutes)

### Configure R-Lion

1. Click on **R-Lion** → **CLI** tab
2. Press Enter to start
3. Type **"no"** when asked about initial configuration dialog
4. Copy and paste (or type) the configuration from `Router_Configurations.md`

```cisco
enable
configure terminal
hostname R-Lion
interface GigabitEthernet0/0
 description Link to R-Elephant
 ip address 10.0.12.145 255.255.255.252
 no shutdown
 exit
interface GigabitEthernet0/1
 description Lion Tribe LAN
 ip address 10.0.12.129 255.255.255.240
 no shutdown
 exit
ip route 10.0.12.0 255.255.255.128 10.0.12.146
ip route 10.0.8.0 255.255.252.0 10.0.12.146
ip route 10.0.0.0 255.255.248.0 10.0.12.146
ip route 10.0.12.148 255.255.255.252 10.0.12.146
ip route 10.0.12.152 255.255.255.252 10.0.12.146
end
write memory
```

### Configure R-Elephant

1. Click on **R-Elephant** → **CLI** tab
2. Enter the full configuration from `Router_Configurations.md`

**Key sections:**
- Configure all 4 interfaces (Gi0/0, Gi0/1, Gi0/2, Gi1/0)
- Set up DHCP relay on Gi1/0
- Configure OSPF
- Add static route to Lion
- Redistribute static routes

### Configure R-Cat

1. Click on **R-Cat** → **CLI** tab
2. Enter the configuration from `Router_Configurations.md`

**Key sections:**
- Configure 2 interfaces (Gi0/0, Gi0/1)
- Set up DHCP relay on Gi0/1
- Configure OSPF

### Configure R-Dog

1. Click on **R-Dog** → **CLI** tab
2. Enter the configuration from `Router_Configurations.md`

**Key sections:**
- Configure 2 interfaces (Gi0/0, Gi0/1)
- Set up DHCP relay on Gi0/1
- Configure OSPF

### Verify Router Configuration

On each router, run:
```cisco
show ip interface brief
show ip route
show ip ospf neighbor  (on Elephant, Cat, Dog only)
```

---

## PHASE 3: Configure Servers (30-45 minutes)

### Configure All 4 Servers in Lion Tribe

Follow the detailed instructions in `Server_Configuration.md`:

1. **DNS-Server (10.0.12.131)**
   - Set static IP
   - Enable DNS service
   - Add DNS records for www.animals.com, mail.animals.com, etc.

2. **Web-Server (10.0.12.130)**
   - Set static IP
   - Enable HTTP/HTTPS service
   - Edit index.html with welcome message

3. **Email-Server (10.0.12.132)**
   - Set static IP
   - Enable EMAIL service
   - Set domain to animals.com
   - Create 4 email accounts for tribal chiefs

4. **DHCP-Server (10.0.12.133)**
   - Set static IP
   - Enable DHCP service
   - Create 3 DHCP pools (DOG-POOL, CAT-POOL, ELEPHANT-POOL)

---

## PHASE 4: Configure End Devices (20-30 minutes)

### Configure Tribal Chief PCs (Static IP)

#### LionKing-PC
- Desktop → IP Configuration → Static
- IP: 10.0.12.134
- Mask: 255.255.255.240
- Gateway: 10.0.12.129
- DNS: 10.0.12.131

#### ElephantChief-PC
- Desktop → IP Configuration → Static
- IP: 10.0.12.2
- Mask: 255.255.255.128
- Gateway: 10.0.12.1
- DNS: 10.0.12.131

#### CatChief-PC
- Desktop → IP Configuration → Static
- IP: 10.0.8.2
- Mask: 255.255.252.0
- Gateway: 10.0.8.1
- DNS: 10.0.12.131

#### DogChief-PC
- Desktop → IP Configuration → Static
- IP: 10.0.0.2
- Mask: 255.255.248.0
- Gateway: 10.0.0.1
- DNS: 10.0.12.131

### Configure Regular PCs (DHCP)

For all remaining PCs (PC-Lion-1, PC-Lion-2, PC-Elephant-1, PC-Elephant-2, PC-Cat-1, PC-Cat-2, PC-Dog-1, PC-Dog-2):

1. Click on PC
2. Desktop → IP Configuration
3. Select **DHCP**
4. Wait for IP assignment (you should see the IP appear)
5. Verify gateway and DNS are correct

**Note:** Lion tribe PCs should use static IPs per requirements, so configure:
- PC-Lion-1: 10.0.12.135
- PC-Lion-2: 10.0.12.136

---

## PHASE 5: Configure Email on Chief PCs (15-20 minutes)

### On Each Tribal Chief PC:

1. **Open Desktop → Email**
2. **Configure as follows:**

#### LionKing-PC Email
- Your Name: Lion King
- Email Address: lionking@animals.com
- Incoming Mail Server: 10.0.12.132
- Outgoing Mail Server: 10.0.12.132
- User Name: lionking
- Password: lion123
- Click **Save**

#### ElephantChief-PC Email
- Your Name: Elephant Chief
- Email Address: elephantchief@animals.com
- Incoming Mail Server: 10.0.12.132
- Outgoing Mail Server: 10.0.12.132
- User Name: elephantchief
- Password: elephant123
- Click **Save**

#### CatChief-PC Email
- Your Name: Cat Chief
- Email Address: catchief@animals.com
- Incoming Mail Server: 10.0.12.132
- Outgoing Mail Server: 10.0.12.132
- User Name: catchief
- Password: cat123
- Click **Save**

#### DogChief-PC Email
- Your Name: Dog Chief
- Email Address: dogchief@animals.com
- Incoming Mail Server: 10.0.12.132
- Outgoing Mail Server: 10.0.12.132
- User Name: dogchief
- Password: dog123
- Click **Save**

---

## PHASE 6: Testing and Verification (20-30 minutes)

### Test 1: Basic Connectivity (Ping Tests)

From **Command Prompt** on any PC:

```
ping 10.0.12.130    # Web Server
ping 10.0.12.131    # DNS Server
ping 10.0.12.132    # Email Server
ping 10.0.12.133    # DHCP Server
ping 10.0.12.134    # LionKing PC
ping 10.0.12.2      # ElephantChief PC
ping 10.0.8.2       # CatChief PC
ping 10.0.0.2       # DogChief PC
```

**Expected Result:** All pings should succeed ✓

### Test 2: DNS Resolution

From any PC's Command Prompt:
```
nslookup www.animals.com
```
**Expected Result:** Should return 10.0.12.130

### Test 3: Web Access

From any PC:
1. Desktop → Web Browser
2. Enter: `www.animals.com` or `http://10.0.12.130`

**Expected Result:** "Welcome to the Animal Kingdom!" page displays ✓

### Test 4: Email Communication

1. On **LionKing-PC**:
   - Open Desktop → Email
   - Click **Compose**
   - To: dogchief@animals.com
   - Subject: Test Email
   - Message: Hello from Lion King
   - Click **Send**

2. On **DogChief-PC**:
   - Open Desktop → Email
   - Click **Receive**
   - Check for email from lionking@animals.com

**Expected Result:** Email successfully sent and received ✓

### Test 5: Inter-Tribe Connectivity

Test pings between different tribes:
- From Lion → Elephant, Cat, Dog
- From Elephant → Lion, Cat, Dog
- From Cat → Lion, Elephant, Dog
- From Dog → Lion, Elephant, Cat

**Expected Result:** All inter-tribe pings succeed ✓

### Test 6: DHCP Verification

1. Release/Renew IP on a DHCP client:
   - Click PC (non-chief)
   - Desktop → IP Configuration
   - Toggle to Static then back to DHCP
   - Verify new IP is assigned from correct pool

2. Check IP ranges:
   - Dog tribe: 10.0.0.10 - 10.0.7.254
   - Cat tribe: 10.0.8.10 - 10.0.11.254
   - Elephant tribe: 10.0.12.10 - 10.0.12.126

---

## PHASE 7: Documentation and Submission (30-45 minutes)

### 1. Save Packet Tracer File
- File → Save As → `AnimalKingdom_YourGroupName.pkt`

### 2. Take Topology Screenshot
- Use Packet Tracer's screenshot feature or Snipping Tool
- Ensure all devices and network labels are visible
- Save as `Topology_Diagram.png`

### 3. Add Network Address Labels
Use the **Place Note** tool in Packet Tracer to label:
- Lion LAN: 10.0.12.128/28
- Elephant LAN: 10.0.12.0/25
- Cat LAN: 10.0.8.0/22
- Dog LAN: 10.0.0.0/21
- Lion-Elephant Link: 10.0.12.144/30
- Elephant-Cat Link: 10.0.12.148/30
- Elephant-Dog Link: 10.0.12.152/30

### 4. Export Router Configurations

For each router, use CLI:
```cisco
show running-config
```
Copy output to text files:
- R-Lion_Config.txt
- R-Elephant_Config.txt
- R-Cat_Config.txt
- R-Dog_Config.txt

### 5. Create Submission PDF

Combine the following into one PDF document:

**Page 1: Cover Page**
- Project Title: Animal Kingdom Network
- Group Member Names and Contributions
- Date

**Page 2-3: VLSM Tree**
- Include the VLSM tree from `VLSM_Calculation.md`
- Show subnet allocation

**Page 4-5: IP Address Table**
- Complete IP addressing table from `IP_Address_Table.md`

**Page 6-10: Router Configurations**
- Full configuration output for all 4 routers
- Include verification command outputs

**Page 11-12: Topology Diagram**
- Full network topology with labels
- Legend explaining icons and connections

**Page 13: Testing Results**
- Screenshots of successful ping tests
- Screenshot of website access
- Screenshot of email communication
- DHCP verification screenshots

---

## Troubleshooting Guide

### Problem: Ping fails between tribes
**Solution:**
- Check router interfaces: `show ip interface brief`
- Verify routing table: `show ip route`
- Check OSPF neighbors: `show ip ospf neighbor`
- Ensure cables are connected to correct ports

### Problem: DHCP not working
**Solution:**
- Verify DHCP server IP and service is ON
- Check `ip helper-address` on router LAN interfaces
- Verify DHCP pools are correctly configured
- Check router connectivity to DHCP server

### Problem: DNS resolution fails
**Solution:**
- Verify DNS server IP (10.0.12.131) is reachable
- Check DNS records are added correctly
- Ensure PCs have correct DNS server configured
- Test with: `nslookup www.animals.com`

### Problem: Website doesn't load
**Solution:**
- Ping web server: `ping 10.0.12.130`
- Check HTTP service is enabled on web server
- Verify DNS resolves www.animals.com correctly
- Try accessing by IP: `http://10.0.12.130`

### Problem: Email not working
**Solution:**
- Verify email server IP (10.0.12.132) is reachable
- Check email service is ON
- Verify user accounts are created correctly
- Ensure PC email clients have correct server settings
- Check domain is set to "animals.com"

### Problem: OSPF neighbors not forming
**Solution:**
- Check interfaces are up: `show ip interface brief`
- Verify OSPF network statements match interface IPs
- Check OSPF area numbers match (should be area 0)
- Ensure no passive-interface on OSPF links
- Wait 40 seconds for OSPF convergence

---

## Checklist Before Submission

- [ ] All 4 routers configured and working
- [ ] All 4 switches connected properly
- [ ] All 4 servers configured (DNS, Web, Email, DHCP)
- [ ] All 12 PCs configured (4 chiefs static, 8 regular DHCP/static)
- [ ] Tribal chief PCs can email each other
- [ ] Website "www.animals.com" is accessible from all PCs
- [ ] All PCs can ping each other across tribes
- [ ] DHCP assigns IPs correctly to non-chief PCs
- [ ] DNS resolves www.animals.com
- [ ] Network diagram has proper labels
- [ ] .pkt file saved and tested
- [ ] Screenshots taken of successful tests
- [ ] PDF documentation completed
- [ ] Work distribution documented

---

## Time Estimate

| Phase | Task | Estimated Time |
|-------|------|----------------|
| 1 | Create Topology | 30-45 min |
| 2 | Configure Routers | 45-60 min |
| 3 | Configure Servers | 30-45 min |
| 4 | Configure End Devices | 20-30 min |
| 5 | Configure Email | 15-20 min |
| 6 | Testing | 20-30 min |
| 7 | Documentation | 30-45 min |
| **Total** | | **3-4 hours** |

---

## Final Notes

- **Save frequently** - Use File → Save As to create backup versions
- **Test incrementally** - Don't wait until the end to test connectivity
- **Use Simulation Mode** - To visualize packet flow and troubleshoot
- **Color code** - Use different colors for different tribes in topology
- **Document assumptions** - Any design decisions you make
- **Collaborate** - Divide work among team members efficiently

Good luck with your Animal Kingdom network implementation! 🦁🐘🐱🐶
