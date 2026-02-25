# Network Verification Commands

## Purpose
These commands are used to verify the proper configuration and connectivity of the Animal Kingdom network topology.

## Testing Connectivity

### 1. Ping Tests for Server Connectivity

Test connectivity to all servers in the Lion Tribe:

```bash
# Web Server
ping 10.0.12.130

# DNS Server
ping 10.0.12.131

# Email Server
ping 10.0.12.132

# DHCP Server
ping 10.0.12.133
```

### 2. Ping Tests for PC Connectivity

Test connectivity from various tribes:

```bash
# Dog Tribe PC
ping 10.0.0.1

# Cat Tribe PC
ping 10.0.8.2

# Elephant Tribe PC
ping 10.0.12.2

# Lion Tribe PC
ping 10.0.12.134
```

### 3. DNS Resolution Test

Verify DNS is working correctly:

```bash
nslookup www.animals.com
```

**Expected Output**: Should resolve to the Web Server IP (10.0.12.130)

### 4. Cross-Network Connectivity Tests

Test connectivity between different tribes to verify routing:

```bash
# From Dog Tribe to Elephant PC
ping 10.0.12.2

# From Cat Tribe to Lion PC
ping 10.0.12.134

# From any PC to Web Server
ping 10.0.12.130

# From any PC to DNS Server
ping 10.0.12.131

# From any PC to Email Server
ping 10.0.12.132
```

## Router Verification Commands

### 5. OSPF Neighbor Verification

Check OSPF neighbor relationships on routers:

```bash
show ip ospf neighbor
```

**Expected Output**: Should show all directly connected routers as FULL/DR, FULL/BDR, or FULL/DROTHER

### 6. Routing Table Verification

Display the routing table to verify all routes are learned:

```bash
show ip route
```

**Expected Output**: Should show:
- Connected routes (C)
- OSPF learned routes (O)
- All network segments (10.0.0.0/21, 10.0.8.0/22, 10.0.12.0/25, 10.0.12.128/28)

## Additional Verification Commands

### 7. Interface Status

```bash
show ip interface brief
```

Verifies all interfaces are up and properly configured.

### 8. DHCP Verification

On a PC configured for DHCP:

```bash
ipconfig /all
```

Should show an IP address assigned from the appropriate DHCP pool.

### 9. DNS Configuration Check

On servers/routers:

```bash
show running-config | include dns
```

## Testing Checklist

- [ ] All servers are reachable from all PCs
- [ ] DNS resolution works (www.animals.com resolves correctly)
- [ ] OSPF neighbors are in FULL state
- [ ] All networks appear in routing tables
- [ ] DHCP assigns addresses correctly
- [ ] Inter-VLAN routing works (PCs in different tribes can communicate)
- [ ] Point-to-point links are operational

## Troubleshooting Tips

If connectivity fails:

1. **Check interface status**: Ensure all interfaces are up/up
2. **Verify IP addressing**: Confirm IPs match the VLSM table
3. **Check OSPF**: Ensure OSPF is configured on all interfaces
4. **Verify routing**: Use `show ip route` to check for missing routes
5. **Test step-by-step**: Start with directly connected devices, then move to remote networks
