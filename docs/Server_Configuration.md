# Animal Kingdom - Server Configuration Guide

## DNS Server Configuration (10.0.12.131)

### Device Settings
- **Device**: Server-PT
- **Display Name**: DNS-Server
- **IP Address**: 10.0.12.131
- **Subnet Mask**: 255.255.255.240
- **Default Gateway**: 10.0.12.129
- **DNS Server**: 10.0.12.131 (itself)

### Configuration Steps in Packet Tracer

1. **Click on the DNS Server**
2. **Go to Desktop Tab → IP Configuration**
   - Static IP Address: `10.0.12.131`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

3. **Go to Services Tab → DNS**
   - Turn DNS Service **ON**
   - Add the following DNS records:

| Name                | Type | Address/Value | TTL  |
|---------------------|------|---------------|------|
| www.animals.com     | A    | 10.0.12.130   | 3600 |
| animals.com         | A    | 10.0.12.130   | 3600 |
| mail.animals.com    | A    | 10.0.12.132   | 3600 |
| dns.animals.com     | A    | 10.0.12.131   | 3600 |
| dhcp.animals.com    | A    | 10.0.12.133   | 3600 |

**Steps to Add Each Record:**
1. Type the domain name in "Name" field
2. Select "A Record" from Type dropdown
3. Enter the IP address
4. Click "Add" button

---

## Web Server Configuration (10.0.12.130)

### Device Settings
- **Device**: Server-PT
- **Display Name**: Web-Server
- **IP Address**: 10.0.12.130
- **Subnet Mask**: 255.255.255.240
- **Default Gateway**: 10.0.12.129
- **DNS Server**: 10.0.12.131

### Configuration Steps in Packet Tracer

1. **Click on the Web Server**
2. **Go to Desktop Tab → IP Configuration**
   - Static IP Address: `10.0.12.130`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

3. **Go to Services Tab → HTTP**
   - Turn HTTP Service **ON**
   - Edit the `index.html` file with the following content:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Animal Kingdom</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f8ff;
            padding: 50px;
        }
        h1 {
            color: #2c5f2d;
            font-size: 48px;
        }
        .container {
            border: 3px solid #2c5f2d;
            padding: 30px;
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Animal Kingdom!</h1>
        <p>United tribes of Lion, Elephant, Cat, and Dog</p>
    </div>
</body>
</html>
```

4. **Also enable HTTPS** (Optional)
   - Go to Services Tab → HTTPS
   - Turn HTTPS Service **ON**

---

## Email Server Configuration (10.0.12.132)

### Device Settings
- **Device**: Server-PT
- **Display Name**: Email-Server
- **IP Address**: 10.0.12.132
- **Subnet Mask**: 255.255.255.240
- **Default Gateway**: 10.0.12.129
- **DNS Server**: 10.0.12.131

### Configuration Steps in Packet Tracer

1. **Click on the Email Server**
2. **Go to Desktop Tab → IP Configuration**
   - Static IP Address: `10.0.12.132`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

3. **Go to Services Tab → EMAIL**
   - Turn Email Service **ON**
   - Set Domain Name: `animals.com`
   
4. **Add User Accounts** (Click "Set" after each user)

| User Name       | Password    | Email Address               |
|-----------------|-------------|-----------------------------|
| lionking        | lion123     | lionking@animals.com        |
| elephantchief   | elephant123 | elephantchief@animals.com   |
| catchief        | cat123      | catchief@animals.com        |
| dogchief        | dog123      | dogchief@animals.com        |

**Steps to Add Each User:**
1. Enter username in "User" field
2. Enter password in "Password" field
3. Click "+" button to add
4. Repeat for all four tribal chiefs

---

## DHCP Server Configuration (10.0.12.133)

### Device Settings
- **Device**: Server-PT
- **Display Name**: DHCP-Server
- **IP Address**: 10.0.12.133
- **Subnet Mask**: 255.255.255.240
- **Default Gateway**: 10.0.12.129
- **DNS Server**: 10.0.12.131

### Configuration Steps in Packet Tracer

1. **Click on the DHCP Server**
2. **Go to Desktop Tab → IP Configuration**
   - Static IP Address: `10.0.12.133`
   - Subnet Mask: `255.255.255.240`
   - Default Gateway: `10.0.12.129`
   - DNS Server: `10.0.12.131`

3. **Go to Services Tab → DHCP**
   - Turn DHCP Service **ON**

4. **Configure DHCP Pools for Each Tribe**

### Pool 1: DOG-POOL
- **Pool Name**: `DOG-POOL`
- **Default Gateway**: `10.0.0.1`
- **DNS Server**: `10.0.12.131`
- **Start IP Address**: `10.0.0.10`
- **Subnet Mask**: `255.255.248.0`
- **Maximum Number of Users**: `2036`
- Click **Add** to save

### Pool 2: CAT-POOL
- **Pool Name**: `CAT-POOL`
- **Default Gateway**: `10.0.8.1`
- **DNS Server**: `10.0.12.131`
- **Start IP Address**: `10.0.8.10`
- **Subnet Mask**: `255.255.252.0`
- **Maximum Number of Users**: `1012`
- Click **Add** to save

### Pool 3: ELEPHANT-POOL
- **Pool Name**: `ELEPHANT-POOL`
- **Default Gateway**: `10.0.12.1`
- **DNS Server**: `10.0.12.131`
- **Start IP Address**: `10.0.12.10`
- **Subnet Mask**: `255.255.255.128`
- **Maximum Number of Users**: `116`
- Click **Add** to save

---

## Server Summary Table

| Server       | IP Address  | Services Enabled | Purpose                              |
|--------------|-------------|------------------|--------------------------------------|
| DNS-Server   | 10.0.12.131 | DNS              | Resolve domain names                 |
| Web-Server   | 10.0.12.130 | HTTP, HTTPS      | Host www.animals.com website         |
| Email-Server | 10.0.12.132 | SMTP, POP3       | Handle tribal chief emails           |
| DHCP-Server  | 10.0.12.133 | DHCP             | Assign IPs to all tribes dynamically |

---

## Testing the Servers

### Test DNS Resolution
1. From any PC, open **Desktop → Command Prompt**
2. Type: `nslookup www.animals.com`
3. Should return: `10.0.12.130`

### Test Web Server
1. From any PC, open **Desktop → Web Browser**
2. Type in URL: `www.animals.com` or `http://10.0.12.130`
3. Should display: "Welcome to the Animal Kingdom!"

### Test Email Server
1. Configure Email client on Chief PCs:
   - Open **Desktop → Email**
   - Set Email Address (e.g., lionking@animals.com)
   - Set Incoming/Outgoing Mail Server: `10.0.12.132`
   - Set Username and Password
   - Click "Save"
2. Compose email to another chief
3. Verify email is received

### Test DHCP Server
1. Set PC to DHCP mode:
   - Click on any non-chief PC
   - Go to **Desktop → IP Configuration**
   - Select **DHCP**
   - Wait for IP assignment
2. Verify IP is from correct pool range
3. Check gateway and DNS are correctly assigned

---

## Important Notes

1. **Configure servers BEFORE configuring PCs** - PCs need DNS to resolve names
2. **All servers are in Lion Tribe** - Connected to SW-Lion switch
3. **DHCP Relay is configured on routers** - Uses `ip helper-address 10.0.12.133`
4. **DNS must be working** - For email and web to function properly
5. **Email requires both DNS and Email services** - DNS for MX records
