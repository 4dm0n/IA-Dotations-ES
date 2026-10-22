---
description: Run nmap scan with predefined profiles for penetration testing
---

# Nmap Scan Command

Execute nmap scans using predefined pentesting profiles.

## Usage

```
/nmap <target> [profile]
```

## Parameters

- **target** (required): IP address, hostname, CIDR range, or file with `-iL`
- **profile** (optional): Scan profile to use (default: `quick`)

## Profiles

| Profile | Description | Nmap Flags |
|---------|-------------|------------|
| `quick` | Fast top-100 port scan | `-T4 -F` |
| `full` | Complete TCP port scan | `-p- -sS -T4` |
| `service` | Service/version detection + default scripts | `-sV -sC -p$PORTS` |
| `udp` | Top 100 UDP ports | `-sU --top-ports 100` |
| `stealth` | Slow fragmented SYN scan | `-sS -T2 -f` |
| `vuln` | Vulnerability scripts | `--script vuln` |
| `audit` | Aggressive: OS, version, scripts, traceroute | `-A -T4` |
| `web` | Web-focused (80,443,8080,8443) | `-p 80,443,8080,8443 -sV --script http-enum,http-title,ssl-cert` |
| `smb` | SMB enumeration | `-p 445 --script smb-enum-shares,smb-enum-users,smb-os-discovery` |
| `recon` | Host discovery only | `-sn` |

## Examples

```bash
# Quick scan of single host
/nmap 192.168.1.10

# Full scan of subnet
/nmap 192.168.1.0/24 full

# Service enumeration on specific ports
/nmap example.com service

# Vulnerability scan
/nmap 10.0.0.5 vuln

# Web application scan
/nmap webapp.example.com web

# SMB enumeration
/nmap 192.168.1.50 smb

# Custom: read targets from file
/nmap -iL targets.txt full
```

## Output

Results saved to current directory with timestamp:
- `nmap_<target>_<profile>_<timestamp>.nmap` (normal)
- `nmap_<target>_<profile>_<timestamp>.xml` (XML)
- `nmap_<target>_<profile>_<timestamp>.gnmap` (grepable)

## Notes

- Requires nmap installed and in PATH
- Privileged scans (SYN, OS detection) need root/Administrator
- For Windows: run terminal as Administrator
- Use `-Pn` flag if host discovery fails: `/nmap 192.168.1.10 -Pn full`
