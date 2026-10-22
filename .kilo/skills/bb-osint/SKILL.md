---
name: bb-osint
description: >-
  Use this skill for passive reconnaissance and OSINT against an authorized bug
  bounty program: subdomain and asset discovery from Certificate Transparency,
  search engines, WHOIS/ASN, historical DNS, Wayback URLs, public code and secret
  leaks, employee and organization footprint, and threat intelligence sources.
  Load it before any active scanning; it produces the candidate asset inventory.
---

# bb-osint / Recon Pasivo

Todo lo que se hace aqui es pasivo: no se envia ninguna peticion al objetivo
directamente (salvo consultas DNS publicas y CT logs, que no tocan los hosts del
programa). Sirve para construir el inventario de candidatos y priorizar antes de
tocar nada.

## 1. Orden de ejecucion (de menor a mayor ruido)

1. **CT logs** -> dominios y subdominios
2. **Passive DNS / historico** -> IPs, activos olvidados
3. **Search engines** -> paginas indexadas, exposed files, directorios
4. **Public code** -> repos, endpoints, secretos, rutas internas
5. **WHOIS/ASN/ORG** -> infraestructura, rangos, proveedores
6. **Wayback / archives** -> endpoints antiguos, API v1, endpointsya retiré
7. **Breach/leak sources publicas** -> solo verificacion, nunca stuffing
8. **Threat intel** -> exposicion previa conocida, CVEs

Empieza siempre por 1 y 2. Son gratuitoss, rapidos y de riesgo cero.

## 2. Certificate Transparency

```bash
# crt.sh (el mas completo)
curl -s "https://crt.sh/?q=%25.$DOMAIN&output=json" \
  | jq -r '.[].name_value' | tr '\r' '\n' | sort -u > subs_ct.txt

# Filtrar solo el dominio raiz y subdominios validos
grep -E "\.$DOMAIN$" subs_ct.txt | grep -v '^\*' > subs_clean.txt

# Alternativa: CertSpotter
curl -s "https://api.certspotter.com/v1/issuances?domain=$DOMAIN&include_subdomains=true&expand=dns_names" \
  | jq -r '.[].dns_names[]' | sort -u >> subs_ct.txt

# Alternativa rapida: bufferover / uncover
# uncover: go install github.com/projectdiscovery/uncover@latest
# python3 -m pip install uncover
uncover -d $DOMAIN -q crtsh,shodan,fofa,hunter,zoomeye,quake -o subs_uncover.txt
```

Post-procesado:
- Elimina entradas con `*` o dominios de terceros (cloud, CDN, SaaS).
- Deduplica y clasifica por profundidad de subdominio (1 nivel, 2 niveles...).
- Marca los que apuntan a IPs de terceros (posible takeover o out-of-scope).

```bash
# Resolucion DNS para separar vivos de muertos
dnsx -l subs_ct.txt -a -silent -o subs_resolved.txt -resp
# Los no resueltos tambien valen: pueden ser un takeover
```

## 3. Passive DNS y historico

```bash
# hackertarget hostsearch
curl -s "https://api.hackertarget.com/hostsearch/?q=$DOMAIN"

# AlienVault OTX passive DNS
curl -s "https://otx.alienvault.com/api/v1/indicators/domain/$DOMAIN/passive_dns" \
  | jq -r '.passive_dns[] | .hostname + " " + .address' | sort -u

# VirusTotal (cuota anonima muy baja; con API key funciona)
# curl -s "https://www.virustotal.com/api/v3/domains/$DOMAIN/resolutions?limit=40" \
#   -H "x-apikey: $VT_KEY"

# Wayback CDX: URLs historicas completas
curl -s "http://web.archive.org/cdx/search/cdx?url=*.${DOMAIN}/*&output=txt&fl=original,timestamp,statuscode,mimetype&collapse=urlkey&limit=5000" \
  > wayback_urls.txt

# Extraer solo endpoints epicurios
grep -E '\.(js|json|xml|txt|yml|yaml|conf|env|bak|sql|log|zip|tar|gz|key|pem|p12|pfx)$' wayback_urls.txt | cut -d' ' -f1 | sort -u > endpoints_hist.txt
```

Los endpoints historicos son de alto valor: `api/v1/` , `internal/`, `admin/`, `dev/`,
`staging/`, `test/`, `.bak`, `.old`, `debug/`, `swagger/`, `graphql`.

## 4. Search engines (dorks)

```bash
# Google/Bing via scraping manual o API (serpapi / duckduckgo html)
# DuckDuckGo html sin dependencias:
ddg() { curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=$1" \
  | grep -oP '(?<=result__a" href=").*?(?=")' | head -20; }

ddg "site:$DOMAIN"
ddg "site:$DOMAIN inurl:admin"
ddg "site:$DOMAIN filetype:pdf OR filetype:doc OR filetype:xlsx"
ddg "site:$DOMAIN inurl:api OR inurl:v1 OR inurl:v2"
ddg "\"$DOMAIN\" \"api_key\" OR \"secret\" OR \"password\""
ddg "site:$DOMAIN intitle:\"index of\""
ddg "site:$DOMAIN -www -mail"
```

Dorks de codigo (grep.app / GitHub code search):
```bash
# grep.app API (sin auth)
curl -s "https://grep.app/api/search?q=$DOMAIN" | jq -r '.hits.hits[] | .repo.raw + " " + .path.raw'

# GitHub code search (requiere token)
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/search/code?q=$DOMAIN+in:file" \
  | jq -r '.items[] | .repository.full_name + " :: " + .path'

# GitHub repos/orgs
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/search/repositories?q=$DOMAIN" \
  | jq -r '.items[] | .full_name + " | " + (.description // "")'
```

## 5. WHOIS, ASN, organizacion

```bash
whois $DOMAIN | grep -Ei "registrant|org|admin|tech|nameserver|registrar|created|updated|expir"

# IPs y rangos del ASN
whois -h whois.radb.net "AS$ASNUM"

# Reverse whois / org search
# https://bgp.he.net/search?search%5Bsearch%5D=$DOMAIN
# https://www.arin.net/resources/whois/

# ASN del asset web
curl -s "https://api.hackertarget.com/aslookup/?q=$IP"

# Rutas y rangos de la organizacion
amass -d $DOMAIN -list
asnmap -d $DOMAIN -silent
```

Objetivo: descubrir rango de IPs owned (CBN/rangos internos) y activos en
proveedores que no aparecen en DNS publico.

## 6. Secretos en repos publicos

```bash
# Gitleaks sobre repos publicos de la org (solo lectura, sin clonar si es posible)
gitleaks detect --source ./repo --no-git -v

# TruffleHog (busca credenciales validas)
trufflehog filesystem ./repo --only-verified
trufflehog github --org=$ORG --only-verified --json

# GitHub org audit
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/orgs/$ORG/repos?per_page=100"
```

Verifica cada secreto: que servicio es, si sigue activo, a que recurso da acceso,
y si laVictima tiene control del activo (si es un repo de un tercero, el
programa puede excluirlo).

## 7. Personas y superficie social (con cuidado)

```bash
# theHarvester: emails, hosts, IPs por dominio/dominio de correo
theHarvester -d $DOMAIN -b all -f harvester_$DOMAIN.txt

# Investigacion de correo sin login (theHarvester, holehe)
holehe $EMAIL              # solo verifica si el correo existe en servicios publicos
```

**Prohibido sin autorizacion explicita:** enviar phishing/phishing a empleados,
ingenieria social, contactarlos por redes sociales sobre el bounty. La mayoria de
programas lo excluye expresamente. Si el programa ofrece un programa de
recompensa por ingenieria social, se gestiona fuera de este flujo.

## 8. Amenazas y exposicion previa

```bash
# URLScan.io: historico de escaneos del objetivo (tecnologias, endpoints)
curl -s "https://urlscan.io/api/v1/search/?q=domain:$DOMAIN" \
  | jq -r '.results[] | .page.url + " | " + (.page.title // "") + " | " + (.page.ip // "")'

# Shodan / Censys / FOFA / Hunter / ZoomEye (registro requiere cuenta)
# Public search engines de CVEs ya explotados:
curl -s "https://api.hackertarget.com/vulnsearch/?q=$DOMAIN"
```

## 9. Salida: `recon/passive/assets_candidates.md`

```markdown
# Activos candidatos - <programa> - <fecha>

## Dominios y subdominios (N)
| Host | Source(s) | DNS | IP | ASN/Provider | Notes |
|---|---|---|---|---|---|
| api.example.com | crtsh, wayback | resolves | 1.2.3.4 | AWS | in-scope |

## IPs / Rangos
| IP/CIDR | Source | Owned by | Notes |

## Endpoints historicos de alto valor
| URL | Estado | Por que |

## Repos publicos
| Repo | Secrets encontrados | Activo? |

## Stack tecnologico inferido
| Tecnologia | Evidencia | Confianza |

## Candidatos fuera de alcance (NO TOCAR)
| Host | Razon |
```

## 10. Criterio de inclusion

Un host entra al inventario activo solo si:
1. Resuelve a una IP, O
2. Tiene evidencia historica solida Y esta dentro del literal scope.

Si no sabes de que plataforma es (Shopify, Salesforce, Cloudfront), no lo
pruebes: verifiquelo primero. Esto evita el baneo mas comun en bounty hunting.
