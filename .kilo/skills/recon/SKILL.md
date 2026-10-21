---
name: recon
description: >
  Comprehensive reconnaissance framework for penetration testing and bug bounty.
  Covers passive/active information gathering, subdomain enumeration, DNS analysis,
  technology fingerprinting, certificate transparency, API discovery, and attack surface mapping.
metadata:
  category: security
  triggers:
    - recon
    - reconnaissance
    - information gathering
    - subdomain enumeration
    - dns enumeration
    - tech fingerprinting
    - attack surface
    - passive recon
    - active recon
    - osint
    - certificate transparency
    - api discovery
---

# Recon Framework / Marco de Reconocimiento

**Bilingual Professional Reference / Referencia Profesional Bilingüe**

---

## Quick Reference / Referencia Rápida

| Phase / Fase | Tools / Herramientas | Output / Salida |
|--------------|---------------------|-----------------|
| **Passive / Pasiva** | subfinder, amass, crt.sh, dnsx, httpx | Subdomains, DNS records, live hosts |
| **Active / Activa** | nmap, masscan, nuclei, ffuf | Open ports, services, vulnerabilities |
| **Tech Fingerprint / Huella Tech** | Wappalyzer, whatweb, retire.js | CMS, frameworks, versions, vulns |
| **API Discovery / Descubrimiento API** | swagger, postman, graphql | Endpoints, schemas, auth methods |
| **Cert Transparency / Transparencia Cert** | crt.sh, certspotter, ctfr | Historical subdomains, wildcard certs |

---

## Phase 1: Passive Reconnaissance / Fase 1: Reconocimiento Pasivo

### Subdomain Enumeration / Enumeración de Subdominios

```bash
# subfinder - Fast passive subdomain enumeration
subfinder -d target.com -o subdomains.txt
subfinder -d target.com -silent | httpx -silent -o live.txt

# amass - Comprehensive enumeration (passive + active)
amass enum -passive -d target.com -o amass_passive.txt
amass enum -active -d target.com -o amass_active.txt

# crt.sh via curl - Certificate transparency logs
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > crt_subs.txt

# certspotter - Alternative CT logs
certspotter --domain target.com --exclude-wildcards --out certspotter.txt

# ctfr - Python wrapper for crt.sh
python3 ctfr.py -d target.com -o ctfr.txt

# Consolidate & deduplicate
cat *.txt | sort -u > all_subdomains.txt
```

### DNS Enumeration / Enumeración DNS

```bash
# dnsx - Fast DNS toolkit
dnsx -l all_subdomains.txt -a -aaaa -cname -ns -mx -txt -resp -o dns_records.txt
dnsx -l all_subdomains.txt -silent -a -o resolved_ips.txt

# Mass DNS resolution
massdns -r resolvers.txt -t A -o S -w massdns_out.txt all_subdomains.txt

# Zone transfer attempt
dig axfr @ns1.target.com target.com
dig axfr @ns2.target.com target.com

# DNS zone walk (NSEC/NSEC3)
nmap --script dns-zone-transfer -p 53 target.com
```

### Technology Fingerprinting / Huella Digital Tecnológica

```bash
# httpx - HTTP probe with tech detection
httpx -l live.txt -tech-detect -status-code -title -server -cdn -o tech_fingerprint.txt

# whatweb - Comprehensive web scanner
whatweb -v -a 3 -i live.txt --log-json=whatweb.json

# Wappalyzer CLI (Node.js)
npx wappalyzer live.txt -o wappalyzer.json

# retire.js - JavaScript vulnerability scanner
retire --path ./js_files --outputformat json --outputpath retire.json

# nuclei - Template-based scanning
nuclei -l live.txt -t technologies/ -o nuclei_tech.txt
```

---

## Phase 2: Active Reconnaissance / Fase 2: Reconocimiento Activo

### Port Scanning / Escaneo de Puertos

```bash
# masscan - Ultra-fast port scanner
masscan -p1-65535 --rate=10000 -iL resolved_ips.txt -oG masscan.gnmap

# nmap - Comprehensive follow-up
nmap -sS -sV -sC -p- -T4 -iL masscan_top_ports.txt -oA nmap_full

# Specific service scans
nmap -sU --top-ports 100 -iL resolved_ips.txt -oA nmap_udp
```

### Service Enumeration / Enumeración de Servicios

```bash
# HTTP/HTTPS deep enumeration
nmap --script http-enum,http-title,http-headers,http-methods,http-robots.txt -p 80,443,8080,8443 -iL targets.txt

# SMB enumeration
nmap --script smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode -p 445 -iL targets.txt

# SNMP enumeration
nmap --script snmp-info,snmp-sysdescr,snmp-interfaces -p 161 -sU -iL targets.txt

# LDAP enumeration
nmap --script ldap-search,ldap-rootdse -p 389 -iL targets.txt
```

---

## Phase 3: Attack Surface Mapping / Fase 3: Mapeo de Superficie de Ataque

### Content Discovery / Descubrimiento de Contenido

```bash
# ffuf - Fast web fuzzer
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -o ffuf_root.json

# Feroxbuster - Recursive content discovery
feroxbuster -u https://target.com -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -r -x php,html,js,txt,json

# dirsearch - Python alternative
python3 dirsearch.py -u https://target.com -e php,html,js,txt,json -r -t 50

# katana - Crawling for endpoints
katana -u https://target.com -d 3 -jc -kf -o katana_endpoints.txt
```

### API Discovery / Descubrimiento de APIs

```bash
# Swagger/OpenAPI discovery
ffuf -u https://target.com/FUZZ -w swagger_paths.txt -mc 200 -o swagger.json
# Common paths: /swagger.json, /api-docs, /v1/swagger.json, /openapi.json

# GraphQL introspection
curl -X POST https://target.com/graphql -H "Content-Type: application/json" -d '{"query":"{__schema{types{name,fields{name}}}}"}' 

# Postman collection discovery
ffuf -u https://target.com/FUZZ -w postman_paths.txt -mc 200
# Common: /postman/collection.json, /api/collection.json
```

---

## Phase 4: Intelligence Correlation / Fase 4: Correlación de Inteligencia

### Data Aggregation Pipeline / Pipeline de Agregación

```bash
# 1. Consolidate all subdomains
cat subfinder.txt amass_*.txt crt_subs.txt certspotter.txt ctfr.txt | sort -u > master_subdomains.txt

# 2. Resolve all
dnsx -l master_subdomains.txt -a -silent -o resolved_master.txt

# 3. Probe HTTP/HTTPS
httpx -l resolved_master.txt -silent -status-code -tech-detect -title -server -cdn -ip -o http_probe.txt

# 4. Extract interesting targets
grep -E "200|301|302|403" http_probe.txt | awk '{print $1}' > interesting_targets.txt

# 5. Run nuclei on interesting
nuclei -l interesting_targets.txt -t cves/ -t vulnerabilities/ -t misconfiguration/ -o nuclei_results.txt

# 6. Content discovery on interesting
for target in $(cat interesting_targets.txt); do
  ffuf -u "$target/FUZZ" -w raft-medium.txt -mc 200,301,302,403 -o "ffuf_$(echo $target | sed 's|https\?://||' | sed 's|/.*||').json" &
done
wait
```

---

## Automation Scripts / Scripts de Automatización

### Master Recon Script / Script Maestro de Recon

```bash
#!/bin/bash
# recon_master.sh - Full automated reconnaissance
# Usage: ./recon_master.sh target.com

TARGET=$1
OUTDIR="recon_${TARGET}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "[+] Starting passive recon for $TARGET"

# Passive subdomain enum
subfinder -d "$TARGET" -o "$OUTDIR/subfinder.txt"
amass enum -passive -d "$TARGET" -o "$OUTDIR/amass_passive.txt"
curl -s "https://crt.sh/?q=%25.$TARGET&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > "$OUTDIR/crt.txt"

# Consolidate
cat "$OUTDIR"/*.txt | sort -u > "$OUTDIR/all_subs.txt"

# Resolve
dnsx -l "$OUTDIR/all_subs.txt" -a -aaaa -cname -ns -mx -txt -resp -o "$OUTDIR/dns.txt"
dnsx -l "$OUTDIR/all_subs.txt" -silent -a -o "$OUTDIR/resolved.txt"

# HTTP probe
httpx -l "$OUTDIR/resolved.txt" -tech-detect -status-code -title -server -cdn -ip -o "$OUTDIR/http.txt"

# Nuclei scan
nuclei -l "$OUTDIR/resolved.txt" -t cves/ -t vulnerabilities/ -t misconfiguration/ -o "$OUTDIR/nuclei.txt"

echo "[+] Recon complete. Results in $OUTDIR/"
```

---

## Best Practices / Mejores Prácticas

### Do / Hacer
- [ ] Start with **passive** recon to avoid detection
- [ ] Use **multiple sources** for subdomain enumeration
- [ ] **Validate** every finding actively before reporting
- [ ] **Document** methodology and tool versions
- [ ] **Rate limit** active scans to avoid DoS
- [ ] **Scope check** - only test authorized assets

### Don't / No Hacer
- [ ] Skip passive phase
- [ ] Rely on single tool output
- [ ] Scan out-of-scope assets
- [ ] Run intrusive scans without permission
- [ ] Ignore rate limiting / WAF responses

---

## Common Pitfalls / Errores Comunes

| Pitfall / Problema | Solution / Solución |
|---|---|
| Too many false positives | Cross-reference multiple tools; validate manually |
| Missing subdomains | Use both passive (CT logs) and active (brute force) |
| WAF blocking scans | Rotate IPs, use `-T2`, add delays, fragment packets |
| Rate limited by DNS | Use multiple resolvers; slow down massdns |
| Incomplete tech detection | Combine httpx + whatweb + nuclei + Wappalyzer |

---

## Tool Installation / Instalación de Herramientas

```bash
# Go-based tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install -v github.com/ffuf/ffuf@latest
go install -v github.com/OWASP/Amass/v3/...@latest

# masscan
git clone https://github.com/robertdavidgraham/masscan && cd masscan && make && sudo make install

# feroxbuster
cargo install feroxbuster

# katana
go install github.com/projectdiscovery/katana/cmd/katana@latest

# whatweb
gem install whatweb

# retire.js
npm install -g retire
```

---

## References / Referencias

- **Methodology**: PTES Technical Guidelines - Reconnaissance
- **Bug Bounty**: https://github.com/nahamsec/Resources-for-Beginner-Bug-Bounty-Hunters
- **Subdomain Enum**: https://github.com/projectdiscovery/subfinder
- **Nuclei Templates**: https://github.com/projectdiscovery/nuclei-templates
- **SecLists**: https://github.com/danielmiessler/SecLists
- **Awesome Recon**: https://github.com/redhuntlabs/Awesome-Recon