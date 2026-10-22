---
description: Recon pasivo de OSINT (CT logs, Wayback, search engines, codigo publico) sin tocar el objetivo
---

# /bb-subs

Enumeracion pasiva de subdominios y activos candidatos. No envia ninguna peticion
al host del objetivo.

Carga la skill `bb-osint`.

## Uso

```
/bb-subs <domain> [--deep] [--out recon/passive/]
```

## Fases

1. **CT logs**: `crt.sh`, CertSpotter, `uncover` (crtsh, shodan, fofa, hunter,
   zoomeye, quake).
2. **Passive DNS**: AlienVault OTX, HackerTarget hostsearch.
3. **Historico**: Wayback CDX (URLs completas, no solo hosts), `gau`, `waybackurls`.
4. **Codigo publico**: grep.app, GitHub code search, repos de la organizacion.
5. **Infraestructura**: WHOIS, ASN, `asnmap`, rangos de la organizacion.
6. **OSINT de personas**: `theHarvester` (solo emails publicos, sin login).

## Salida

```
recon/passive/
  subs_ct.txt          # crt.sh
  subs_combined.txt    # union deduplicada
  subs_resolved.txt    # los que resuelven
  ips.txt              # IPs unicas
  urls_historical.txt  # endpoints de Wayback
  endpoints_interesting.txt
  assets_candidates.md # informe
```

## Flags

- `--deep`: añade Wayback completo, dorks de codigo y busqueda de leaks publicos.
- `--subs-only`: solo subdominios, sin OSINT de personas.

## Notas

- Todo pasivo. No hagas `curl` al objetivo: solo a APIs publicas de terceros.
- Elimina dominios de terceros (cloud/CDN/SaaS) y marcalos como
  `OUT-OF-SCOPE (third-party)` en el informe.
- No contactes a las personas encontradas ni uses sus cuentas.
