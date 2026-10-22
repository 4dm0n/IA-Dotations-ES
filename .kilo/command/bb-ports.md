---
description: Escaneo de puertos y servicios con nmap/masscan siguiendo la taxonomia BlackArch
---

# /bb-ports

Escaneo de puertos y fingerprinting de servicios.

Carga `bb-recon` y la skill `nmap-pentesting` si esta disponible.

## Uso

```
/bb-ports <target> [--profile quick|full|service|udp|web|smb|audit] [--rate <n>] [--ports <range>] [--iL <file>]
```

## Perfiles

| Perfil | Comando base | Notas |
|---|---|---|
| `quick` | `naabu -top-ports 1000` o `nmap -sT --top-ports 1000` | default |
| `full` | `sudo nmap -sS -p- -T3` | requiere root |
| `service` | `nmap -sV -sC -p <puertos>` | versiones y scripts NSE |
| `udp` | `sudo nmap -sU --top-ports 50 --max-rate 50` | lento y ruidoso: usa solo con justificacion |
| `web` | `nmap -p 80,443,8080,8443,8000,3000,5000 -sV --script http-enum,http-title,ssl-cert` | |
| `smb` | `nmap -p 445,139 --script smb-enum-shares,smb-enum-users,smb-os-discovery` | |
| `audit` | `nmap -A -T4` | agresivo: solo con permiso |

## Opciones

- `--rate <n>`: paquetes por segundo (nmap `--max-rate`, naabu `-rate`).
- `--ports <rango>`: `1-1024`, `80,443,8000-8100`.
- `--iL <file>`: objetivos desde fichero.
- `--no-root`: usa connect scan si no hay privilegios.

## Flujo recomendado en bounty web

```bash
# 1. Rapido y sin ruido para priorizar
naabu -list hosts_resolved.txt -top-ports 1000 -rate 500 -c 10 -o ports_open.txt -silent

# 2. Profundizar solo en los hosts con puertos web
nmap -Pn -sV -sC -p 80,443,8080,8443,8000,3000,5000 -iL web_hosts.txt -oA services_web

# 3. Servicios de gestion solo si son in-scope y hay justificacion
nmap -Pn -sV -p 22,3389,5900,6379,27017 -iL management_hosts.txt -oA services_mgmt
```

## Salida

- `ports_<target>_<profile>_<timestamp>.nmap` (normal), `.xml`, `.gnmap`.
- Resumen por puerto y por host en `recon/active/services.txt`.

## Notas

- Sin root: `-sT` en lugar de `-sS`; los puertos filtrados no se distinguen.
- `-Pn` si el host no responde a ping (normal en cloud).
- Nunca escanees rangos de IP de proveedores cloud: son del proveedor.
- Un puerto abierto no es un finding. El finding requiere servicio exposed con
  impacto demonstrated.
