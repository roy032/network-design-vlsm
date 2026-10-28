# Animal Kingdom - Complete IP Addressing Table

## Network Summary

| Network Name     | Network Address | Subnet Mask     | CIDR | First IP    | Last IP       | Broadcast   | Gateway     |
|------------------|-----------------|-----------------|------|-------------|---------------|-------------|-------------|
| Dog Tribe        | 10.0.0.0        | 255.255.248.0   | /21  | 10.0.0.1    | 10.0.7.254    | 10.0.7.255  | 10.0.0.1    |
| Cat Tribe        | 10.0.8.0        | 255.255.252.0   | /22  | 10.0.8.1    | 10.0.11.254   | 10.0.11.255 | 10.0.8.1    |
| Elephant Tribe   | 10.0.12.0       | 255.255.255.128 | /25  | 10.0.12.1   | 10.0.12.126   | 10.0.12.127 | 10.0.12.1   |
| Lion Tribe       | 10.0.12.128     | 255.255.255.240 | /28  | 10.0.12.129 | 10.0.12.142   | 10.0.12.143 | 10.0.12.129 |
| Lion-Elephant    | 10.0.12.144     | 255.255.255.252 | /30  | 10.0.12.145 | 10.0.12.146   | 10.0.12.147 | N/A         |
| Elephant-Cat     | 10.0.12.148     | 255.255.255.252 | /30  | 10.0.12.149 | 10.0.12.150   | 10.0.12.151 | N/A         |
| Elephant-Dog     | 10.0.12.152     | 255.255.255.252 | /30  | 10.0.12.153 | 10.0.12.154   | 10.0.12.155 | N/A         |

---

## Detailed Device IP Assignments

### LION TRIBE (10.0.12.128/28)

| Device Name      | Interface/Type | IP Address    | Subnet Mask     | Default Gateway | Description                |
|------------------|----------------|---------------|-----------------|-----------------|----------------------------|
| R-Lion           | Gi0/0/0        | 10.0.12.145   | 255.255.255.252 | N/A             | To R-Elephant              |
| R-Lion           | Gi0/1          | 10.0.12.129   | 255.255.255.240 | N/A             | Lion LAN (Gateway)         |
| DNS-Server       | FastEthernet   | 10.0.12.131   | 255.255.255.240 | 10.0.12.129     | DNS Server (animals.com)   |
| Web-Server       | FastEthernet   | 10.0.12.130   | 255.255.255.240 | 10.0.12.129     | www.animals.com            |
| Email-Server     | FastEthernet   | 10.0.12.132   | 255.255.255.240 | 10.0.12.129     | Email Server (SMTP/POP3)   |
| DHCP-Server      | FastEthernet   | 10.0.12.133   | 255.255.255.240 | 10.0.12.129     | DHCP for all tribes        |
| LionKing-PC      | FastEthernet   | 10.0.12.134   | 255.255.255.240 | 10.0.12.129     | Chief (lionking@...)       |
| PC-Lion-1        | FastEthernet   | 10.0.12.135   | 255.255.255.240 | 10.0.12.129     | End device                 |
| PC-Lion-2        | FastEthernet   | 10.0.12.136   | 255.255.255.240 | 10.0.12.129     | End device                 |

**Static IP Range**: 10.0.12.129 - 10.0.12.142  
**Total Usable IPs**: 14

---

### ELEPHANT TRIBE (10.0.12.0/25)

| Device Name        | Interface/Type | IP Address    | Subnet Mask     | Default Gateway | Description                |
|--------------------|----------------|---------------|-----------------|-----------------|----------------------------|
| R-Elephant         | Gi0/0/0        | 10.0.12.146   | 255.255.255.252 | N/A             | To R-Lion                  |
| R-Elephant         | Gi0/1          | 10.0.12.149   | 255.255.255.252 | N/A             | To R-Cat                   |
| R-Elephant         | Gi0/2          | 10.0.12.153   | 255.255.255.252 | N/A             | To R-Dog                   |
| R-Elephant         | Gi0/0          | 10.0.12.1     | 255.255.255.128 | N/A             | Elephant LAN (Gateway)     |
| ElephantChief-PC   | FastEthernet   | 10.0.12.2     | 255.255.255.128 | 10.0.12.1       | Chief (elephantchief@...)  |
| PC-Elephant-1      | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |
| PC-Elephant-2      | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |

**Static IP Range**: 10.0.12.1 - 10.0.12.2 (Chief only)  
**DHCP Pool**: 10.0.12.10 - 10.0.12.126  
**Total Usable IPs**: 126

---

### CAT TRIBE (10.0.8.0/22)

| Device Name      | Interface/Type | IP Address    | Subnet Mask     | Default Gateway | Description                |
|------------------|----------------|---------------|-----------------|-----------------|----------------------------|
| R-Cat            | Gi0/0          | 10.0.12.150   | 255.255.255.252 | N/A             | To R-Elephant              |
| R-Cat            | Gi0/1          | 10.0.8.1      | 255.255.252.0   | N/A             | Cat LAN (Gateway)          |
| CatChief-PC      | FastEthernet   | 10.0.8.2      | 255.255.252.0   | 10.0.8.1        | Chief (catchief@...)       |
| PC-Cat-1         | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |
| PC-Cat-2         | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |

**Static IP Range**: 10.0.8.1 - 10.0.8.2 (Chief only)  
**DHCP Pool**: 10.0.8.10 - 10.0.11.254  
**Total Usable IPs**: 1022

---

### DOG TRIBE (10.0.0.0/21)

| Device Name      | Interface/Type | IP Address    | Subnet Mask     | Default Gateway | Description                |
|------------------|----------------|---------------|-----------------|-----------------|----------------------------|
| R-Dog            | Gi0/0          | 10.0.12.154   | 255.255.255.252 | N/A             | To R-Elephant              |
| R-Dog            | Gi0/1          | 10.0.0.1      | 255.255.248.0   | N/A             | Dog LAN (Gateway)          |
| DogChief-PC      | FastEthernet   | 10.0.0.2      | 255.255.248.0   | 10.0.0.1        | Chief (dogchief@...)       |
| PC-Dog-1         | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |
| PC-Dog-2         | FastEthernet   | DHCP          | DHCP            | DHCP            | End device                 |

**Static IP Range**: 10.0.0.1 - 10.0.0.2 (Chief only)  
**DHCP Pool**: 10.0.0.10 - 10.0.7.254  
**Total Usable IPs**: 2046

---

## DHCP Configuration Summary

### DHCP Server (10.0.12.133)

| Pool Name | Network       | Subnet Mask     | Gateway     | DNS Server  | Excluded IPs         |
|-----------|---------------|-----------------|-------------|-------------|----------------------|
| DOG-POOL  | 10.0.0.0      | 255.255.248.0   | 10.0.0.1    | 10.0.12.131 | 10.0.0.1 - 10.0.0.9  |
| CAT-POOL  | 10.0.8.0      | 255.255.252.0   | 10.0.8.1    | 10.0.12.131 | 10.0.8.1 - 10.0.8.9  |
| ELE-POOL  | 10.0.12.0     | 255.255.255.128 | 10.0.12.1   | 10.0.12.131 | 10.0.12.1 - 10.0.12.9|

### DHCP Relay Agents

| Router     | Interface | Helper Address |
|------------|-----------|----------------|
| R-Elephant | Gi0/0     | 10.0.12.133    |
| R-Cat      | Gi0/1     | 10.0.12.133    |
| R-Dog      | Gi0/1     | 10.0.12.133    |

---

## DNS Configuration

### DNS Server (10.0.12.131)

| Record Type | Name              | Value          | Description                    |
|-------------|-------------------|----------------|--------------------------------|
| A Record    | www.animals.com   | 10.0.12.130    | Web server                     |
| A Record    | animals.com       | 10.0.12.130    | Domain root to web server      |
| A Record    | dns.animals.com   | 10.0.12.131    | DNS server itself              |
| MX Record   | animals.com       | 10.0.12.132    | Mail server                    |
| A Record    | mail.animals.com  | 10.0.12.132    | Mail server                    |

---

## Email Configuration

### Email Server (10.0.12.132)

| Email Account           | User Name       | Domain        | Full Email Address         |
|-------------------------|-----------------|---------------|----------------------------|
| Lion King               | lionking        | animals.com   | lionking@animals.com       |
| Elephant Chief          | elephantchief   | animals.com   | elephantchief@animals.com  |
| Cat Chief               | catchief        | animals.com   | catchief@animals.com       |
| Dog Chief               | dogchief        | animals.com   | dogchief@animals.com       |

**Domain**: animals.com  
**Server**: 10.0.12.132  
**DNS MX Record**: Points to 10.0.12.132

---

## Quick Reference - Router Interfaces

```
R-Lion (10.0.12.145, 10.0.12.129)
├─ Gi0/0/0: 10.0.12.145/30 → R-Elephant Gi0/0/0
└─ Gi0/1: 10.0.12.129/28 → Lion LAN

R-Elephant (10.0.12.146, 10.0.12.149, 10.0.12.153, 10.0.12.1)
├─ Gi0/0/0: 10.0.12.146/30 → R-Lion Gi0/0/0
├─ Gi0/1: 10.0.12.149/30 → R-Cat Gi0/0
├─ Gi0/2: 10.0.12.153/30 → R-Dog Gi0/0
└─ Gi0/0: 10.0.12.1/25 → Elephant LAN

R-Cat (10.0.12.150, 10.0.8.1)
├─ Gi0/0: 10.0.12.150/30 → R-Elephant Gi0/1
└─ Gi0/1: 10.0.8.1/22 → Cat LAN

R-Dog (10.0.12.154, 10.0.0.1)
├─ Gi0/0: 10.0.12.154/30 → R-Elephant Gi0/2
└─ Gi0/1: 10.0.0.1/21 → Dog LAN
```
