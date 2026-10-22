---
name: bb-recon
description: >-
  Use this skill for active attack-surface mapping against an authorized bug bounty
  scope: DNS resolution, host discovery, port scanning, service and version
  fingerprinting, TLS certificate analysis, virtual host and directory discovery,
  JavaScript endpoint and secret extraction, and consolidated asset inventory.
  Load it after bb-osint and before any vulnerability discovery.
---

# bb-recon / Recon Activo y Mapeo de Superficie

Convierte la lista de candidatos pasivos en un inventario real y deduplicado de
activos, puertos, servicios, versiones y superficies web. Es la base sobre la que
trabajan todas las fases siguientes.

**Regla de ritmo:** la rate limit es por activo y por herramienta, y los escaneos
se SUMAN. Nunca lances dos escaneos pesados a la vez sobre el mismo host.

## 1. Resolucion y hosts vivos

```bash
# Resolucion masiva (rapida, 1 qps)
dnsx -l subs_passive.txt -silent -a -aaaa -resp -o hosts_resolved.txt -r 1

# CNAME / registros que revelan servicios
dnsx -l subs_passive.txt -silent -cname -ns -mx -txt -resp

# Detectar subdominios "takeover-able" (CNAME a proveedor sin registro)
# nuclei -t takeovers -l hosts_resolved.txt
# o manual: para cada CNAME, comprobar si el destino responde "not found" del proveedor
```

```bash
# Alive check (HTTP)
httpx -l hosts_resolved.txt -silent -mc 200,401,403,404,405,500 -o hosts_http.txt
httpx -l hosts_resolved.txt -silent -title -tech-detect -status-code -web-server \
  -ip -cname -asn -cdn -content-length -follow-redirects -o hosts_rich.txt
```

Post-proceso: `httpx` con `-follow-redirects` puede sacar el titulo de un destino
fuera de scope. Filtra por host final.

## 2. Descubrimiento de puertos

```bash
# Rapido y de bajo ruido (top 1000 TCP) - preferido para bounty web
naabu -list hosts_resolved.txt -top-ports 1000 -rate 500 -c 10 -o ports_open.txt -silent

# SYN scan clasico (necesita root)
sudo nmap -Pn -sS -T3 --max-rate 1000 -p- -iL hosts_resolved.txt -oA ports_full

# Top ports rapido sin root (connect scan)
nmap -Pn -sT -T4 --top-ports 1000 -iL hosts_resolved.txt -oN ports_top1000

# UDP (muy lento y ruidoso: solo si el asset lo amerita y el programa lo permite)
sudo nmap -Pn -sU --top-ports 50 --max-rate 50 -iL hosts_vip.txt

# Servicios conocidos de interes
nmap -Pn -sV -sC -p 21,22,23,25,53,80,110,111,135,139,143,161,389,443,445,465,587,993,995,1433,1521,2049,2082,2083,3000,3306,3389,5000,5432,5900,6379,8000,8080,8443,9000,9090,9200,27017,11211,27018 -iL hosts_resolved.txt -oA services_full
```

Usa `masscan` solo para rangos grandes con IP dedicado y permiso explicito.
`zmap`/`unicornscan` solo con permiso y VPS propio.

Prioriza: web (80/443/8080/8443/8000/3000/5000) > management (22/3389/5900) >
database (1433/3306/5432/27017/6379/9200) > others.

## 3. Fingerprinting detallado

```bash
# WhatWeb: tecnologias, server, plugins
whatweb -a 3 --log-json=whatweb.json -iL hosts_http.txt

# Wappalyzer via httpx ya integrado (tech-detect)

# Nuclei tech detection + misconfig (templates RECON)
nuclei -l hosts_http.txt -t technologies/ -t misconfig/ -c 5 -rl 15 -silent -o nuclei_recon.txt

# TLS: versiones, cipher suites, nombres alternativos, expiracion
echo | openssl s_client -connect $HOST:443 -servername $HOST 2>/dev/null \
  | openssl x509 -noout -text | grep -A2 "Subject Alternative Name"
testssl.sh --full --jsonfile tls_$HOST.json $HOST
# sslscan: sslscan --show-certificate --xml sslscan_$HOST.xml $HOST:443
```

Detecta y reporta: **CDN/WAF** (Cloudflare, Akamai, AWS CloudFront, Fastly,
Imperva, Sucuri, F5), porque determina si el activo es del cliente o de un
tercero (out-of-scope).

```bash
# Headers de respuesta en cada host (importante para blue team y para reports)
for h in $(cat hosts_http.txt); do
  echo "=== $h ==="
  curl -sSI "https://$h" | sed -n '1,20p'
done > headers_all.txt
```

## 4. Virtual hosts

```bash
# ffuf con vhost wordlist
ffuf -w wordlist/vhosts.txt -u https://example.com -H "Host: FUZZ.example.com" \
  -fc 404 -mc 200,301,302 -t 20 -rate 50 -o vhosts.json

# gobuster
gobuster vhost -u https://example.com -w wordlist/vhosts.txt -b 404 --append-domain -t 20

# Comparacion de respuestas (interesante si cambia el tamano/ titulo)
```

Un vhost que responde distinto del default con contenido real es un activo
potencial. Verifica siempre que pertenece al programa.

## 5. Directorios y archivos

```bash
# ffuf: fuzzing de directorios y extensiones
ffuf -w wordlist/dirbuster/directory-list-2.3-medium.txt -u https://$HOST/FUZZ \
  -mc 200,204,301,302,307,401,403,405,500 -fc 404 -t 30 -rate 50 -of json -o ffuf_$HOST.json

# Con wordlist pequena primero (rapido y menos ruido)
ffuf -w wordlist/common.txt -u https://$HOST/FUZZ -mc 200,301,302 -fc 404 -t 10 -rate 20

# Backup files sobre paths conocidos (extensions:)
for e in bak old orig backup tmp swp save zip tar.gz sql db; do
  for p in index config settings database application .env; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/$p.$e")
    [ "$code" = "200" ] && echo "https://$HOST/$p.$e"
  done
done

# Sin403:Ffuf no necesita. Alternativa: gobuster dir
```

Recupera la wordlist correcta segun la tecnologia: `wordlist/dirbuster/` (Apache),
`wordlist/DirBuster/`, `raft-small-words` (gobuster), `SecLists/Discovery/Web-Content/`.

## 6. Crawling y extraccion de endpoints y secretos

```bash
# katana: crawler moderno
katana -u https://$HOST -d 3 -jc -kf all -xlsx -o katana_$HOST.csv

# gospider: extrae endpoints de JS
gospider -s https://$HOST -d 3 -c 10 --js -o gospider_$HOST

# gau + waybackurls (historico)
gau --subs --providers --threads 5 https://$HOST | sort -u > gau_$HOST.txt
waybackurls https://$HOST >> gau_$HOST.txt

# Extraccion de secretos en JS (BlackArch blackarch-webapp / secrets)
# nuclei -t exposures/ -l hosts_http.txt
# trufflehog filesystem ./js_dump --only-verified
# Manual: descarga los bundles y busca
grep -rhoE "(api[_-]?key|apikey|secret|token|passwd|password|client_secret|access_key)[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-\/\+\.=]{8,60}[\"']" js/*.js | sort -u
```

Herramientas de la categoria BlackArch `blackarch-webapp` utiles:
`cariddi` (endpoints+secrets), `katana`, `gospider`, `secretfinder`, `truffleHog`,
`gitleaks`, `LinkFinder`.

```bash
# cariddi
cariddi -u https://$HOST -endpoints -plain -o cariddi_$HOST.txt
```

## 7. API discovery

```bash
# Rutas comunes de docs/spec
for p in swagger.json swagger/v1/swagger.json openapi.json openapi.yaml api-docs \
  v2/api-docs v3/api-docs graphql graphiql playground api/swagger api/docs \
  .well-known/openapi .well-known/security.txt actuator actuator/env actuator/health; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/$p")
  [ "$code" = "200" ] && echo "https://$HOST/$p"
done

# kiterunner sobre rutascaa
kiterunner scan "https://$HOST" -w routes.txt -x 20 -p 20 -o kr_$HOST.txt

# Subdominio con "api" / "graphql" en la enumeracion
grep -iE '(api|graphql|rest|internal|admin|dev|staging|uat|beta|old|v1|v2)' hosts_http.txt
```

## 8. Content-Type y tecnologia por puerto no estandar

```bash
# HTTP en puertos alternos
for p in 8000 8080 8443 3000 5000 9000 7001 8888 8081 8082 5555; do
  r=$(curl -sSI --max-time 4 "http://$HOST:$p" | head -1)
  echo "$p -> $r"
done
```

## 9. Consolidacion: `recon/active/assets.md`

```markdown
# Inventario activo - <programa> - <fecha>

## Resumen
- Hosts totales: N | Con HTTP: N | Puertos abiertos: N | Subdominios vivos: N

## Activos
| # | Host | Puerto | Protocolo | Status | Tech | Server | CDN/WAF | Auth | Scope | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

## Vhosts
| Host | Vhost | Evidencia |

## Endpoints discovered
| URL | Metodo | Fuente | Interes |

## Secrets / artefactos expuestos
| Tipo | Ubicacion | Estado (activo?) | Impacto |

## Fuera de alcance detectado (NO TOCAR)
| Host | Razon (CDN tercero / partner / SaaS) |

## Cobertura
| Tecnica | Ejecutada | Cobertura |
|---|---|---|
```

## 10. Cobertura y limitaciones

Registra explicitamente lo que NO probaste:
- Sin escaneo UDP (si aplica) -> razon
- Sin escaneo de puertos >1000 en X hosts -> razon
- Sin fuzzing en Y hosts por limite de tiempo
- Sin fuzzing autenticado (no tienes credenciales)

Esta seccion es lo que mas valoran los programas: demuestra rigor.

## 11. Anti-ruido

- No repitas escaneos sobre hosts ya escaneados. Lleva un registro `scanned.txt`.
- Cachea resultados en disco entre fases: `httpx -l ... -o httpx_cache.txt`, y
  reusa el cache con `-l` + `-silent` antes de re-ejecutar.
- Si te banean, baja el ritmo un 70% y continua. Si te banean dos veces, para
  ese activo y documenta el bloqueo (ver `bb-opsec`).
