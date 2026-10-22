---
description: Recon activo - escaneo de puertos, servicios, fingerprinting, vhosts y directorios sobre el alcance autorizado
---

# /bb-recon

Mapeo activo de la superficie sobre el alcance autorizado. Carga `bb-recon` y
`bb-opsec` (rate).

## Uso

```
/bb-recon <target-file-or-host> [--profile quick|standard|deep] [--ports <list>] [--rate <n>] [--auth]
```

## Perfiles

| Perfil | Que hace | Ritmo |
|---|---|---|
| `quick` | dnsx + httpx alive + naabu top1000 + title/tech | 500 pps, 5 c |
| `standard` | quick + fingerprint (whatweb, nuclei RECON, headers) + TLS | 300 pps, 5 c |
| `deep` | standard + vhosts + fuzzing de directorios (wordlist pequena) + API discovery + JS secrets | 100-200 req/s, c 10 |

## Fases del perfil deep

1. Resolucion DNS y hosts vivos (`dnsx`, `httpx`).
2. Puertos (`naabu` / `nmap -sV`).
3. Fingerprinting (`whatweb`, `httpx -tech-detect`, `nuclei -t technologies/ -t misconfig/`).
4. Cabeceras de respuesta de cada host (cachear).
5. TLS (`openssl s_client`, `testssl.sh` si esta).
6. Virtual hosts (`ffuf -H "Host: FUZZ..."`).
7. Directorios (`ffuf` con wordlist pequena primero).
8. Crawling y endpoints (`katana`, `gospider`).
9. Secrets en JS y bundles.
10. API discovery (specs, graphql, rutas comunes).

## Salida

```
recon/active/
  hosts_resolved.txt
  hosts_http.txt
  hosts_rich.txt         # title, tech, server, cdn, ip, asn
  ports_open.txt
  services.txt
  headers_all.txt
  tls_summary.txt
  vhosts.json
  dirs_<host>.json
  urls.csv
  endpoints.txt
  secrets_found.txt
  assets.md              # inventario consolidado
```

## Reglas

- Cachea resultados: no repitas escaneos ya hechos.
- Un escaneo pesado a la vez por host.
- Marca en `assets.md` los activos `OUT-OF-SCOPE (third-party)` y no los escanees.
- Registra los comandos ejecutados en `logs/commands.log`.
- Si te bloquean: baja el ritmo 70%, y si persiste, para ese activo y documenta.
