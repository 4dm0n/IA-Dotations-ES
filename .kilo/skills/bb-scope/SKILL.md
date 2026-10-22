---
name: bb-scope
description: >-
  Use this skill to translate a bug bounty program's policy into an executable and
  auditable scope: in-scope assets, out-of-scope exclusions, prohibited techniques,
  rate limits, testing windows, safe harbor, and disclosure channel. Load it before
  any active testing and re-read it whenever scope becomes ambiguous, the program
  changes rules, or the client raises a boundary.
---

# bb-scope / Alcance, Politica y Reglas de Juego

El alcance es un artefacto, no una conversacion informal. Si no esta escrito, no
existe. Un finding fuera de alcance no se reporta: se pierde reputacion y puede
invalidar todo lo demas.

## 1. Modelo de alcance

Construye `scope/scope.md` con esta tabla, una fila por activo:

| # | Activo (host/dominio/path/API/repo/app) | Tipo | In-scope | Fuente de la regla | Restricciones | Notas |
|---|---|---|---|---|---|---|
| 1 | `*.example.com` | wildcard | SI | policy web | no staging, no *.internal | excluye tenant de terceros |
| 2 | `api.example.com` | host | SI | policy API | rate 10 req/min | |
| 3 | `example.partner.com` | host | NO | policy "third-party" | prohibido | ver assets del partner |

Reglas de interpretacion de wildcard (el punto donde mas reportes se pierden):

- `*.example.com` normalmente significa "cualquier subdominio" y **no** incluye
  el apex `example.com` salvo que la policy lo diga. Verifica y documenta ambas.
- No aplica a subdominios de cloud de terceros (`*.s3.amazonaws.com`,
  `*.azurewebsites.net`, `*.cloudfront.net`, `*.onrender.com`, `*.vercel.app`,
  `*.firebaseapp.com`, `*.pages.dev`, `*.github.io`). Estos son **siempre**
  out-of-scope salvo mencion explicita.
- Wildcards de nivel superior (`*.com`) son casi siempre un error de la policy:
  tratarlos como out-of-scope y escalar la duda.

## 2. Checklist de politica del programa

Extrae y registra explicitamente (con cita textual corta de la policy):

- [ ] **Tipo de programa**: HackerOne, Bugcrowd, Intigriti, YesWeHack, Patchstack, private/invite, VDP, o programa propio.
- [ ] **Safe harbor**: existe? que cubre exactamente? copiala textual al reporte.
- [ ] **Assets in-scope**: dominios, apps moviles, repos, APIs, infraestructura.
- [ ] **Assets out-of-scope**: explicitos, "todo lo que no sea del owned domain", terceros, servicios de terceros, Dominios del cliente final, entornos de produccion con datos reales.
- [ ] **Vulnerabilidades excluidas**: fuerza bruta (password spraying) sin capacidad especifica, DoS, phishing/ingenieria social, divulgacion de datos de usuarios mas alla del minimo, vulnerabilidades de terceros sin control, ausencia de cabeceras sin impacto, "self-XSS", open redirect sin impacto, spam de formularios, uso de credenciales ajenas.
- [ ] **Metodologia permitida**: scanning automatizado, crawling, fuzzing, uso de herramientas comerciales, proxies/TOR, subcontratacion, pruebas desde multiples IPs, load testing.
- [ ] **Limites de tasa**: RPS, concurrencia, ventana horaria (UTC), tamano de lote.
- [ ] **Datos**: que datos se pueden acceder/tomar para demostrar, cuanto, y obligacion de borrar.
- [ ] **Prueba de cuenta**: si el programa provee cuentas de prueba (test@, staging), usalas en lugar de crear cuentas propias o usar cuentas de terceros.
- [ ] **Disclosure**: canal, plazo de respuesta, plazo de publicacion, si hay "safe harbor" para publicacion temprana.
- [ ] **Contacto**: triage, emergency contact, si se reporta "fuera de horario".
- [ ] **Recompensa / clasificacion**: criterios de severidad del programa (no solo CVSS), bonus por chains, penalizaciones por duplicados/no validos/informativos.

## 3. Decisiones por clase de vulnerability

Mapea cada clase a su decision operativa:

| Clase | Decision por defecto | Notas |
|---|---|---|
| SQLi | PROBAR (impacto minimo) | Usar `sqlmap` con `--risk=1 --level=1`; evitar `--os-shell`, `--file-read` masivo, `--dump` salvo que el programa lo pida |
| XSS | PROBAR | Preferir XSS almacenado/reflejado con impacto real; self-XSS = informativo |
| SSRF | PROBAR | Usar collaborator OOB; nunca apuntar a IPs internas del cliente ni a metadata de nube fuera de alcance |
| IDOR/BOLA | PROBAR | Con dos cuentas propias (o de test); nunca con datos de terceros |
| Auth bypass | PROBAR | Nunca romper MFA como objetivo |
| RCE | PROBAR | Payload no destructivo; nunca reverse shell a infra del cliente; usar OOB |
| LFI/RFI/Path traversal | PROBAR | Leer solo `/etc/hostname` o un archivo propio |
| XXE | PROBAR | Preferir out-of-band; no leer `/etc/passwd` si basta otro indicador |
| Deserializacion | PROBAR | En entorno de prueba, no en produccion con datos reales |
| Open redirect | PROBAR solo con impacto | Sin phishing real ni dominios del atacante usados en cadenas de phishing |
| IDOR a datos de otros usuarios | PROBAR minimo | 1 registro, redacted. Si el programa lo prohibe explicitamente, solo metadata (nombre de campo, longitud) |
| CSRF | PROBAR | Impacto debe ser demostrable sin csrf real a un tercero |
| Race condition | PROBAR con extremo cuidado | Volumen minimo, nunca loops masivos |
| Business logic | PROBAR | Requiere narrativa de impacto clara |
| Missing headers / info disclosure menor | PROBAR solo si hay impacto | Sin impacto = informativo, y el programa puede filtrarlo |
| DoS / resource exhaustion | **NO PROBAR** salvo autorizacion escrita | Usa una prueba minima de negociacion en vez de carga |
| Weak TLS / cert expired | PROBAR | Bajo impacto, a menudo filtrado. Aporta valor en chains |
| Subdomain takeover | PROBAR | Verifica que el recurso realmente lo controlas antes de reportar; el programa puede excluirlo |
| Secrets en repos publicos | PROBAR | Verifica que esten activos y no sean de ejemplo |
| CVE de terceros | INVESTIGAR | Muchos programas excluyen CVEs que no controlas. Documenta y consulta antes de reportar |
| Third-party SaaS con datos del cliente | **NO PROBAR** | Es el error mas comun que genera baneos |

## 4. Verificacion de pertenencia del activo antes de tocar

Antes de cualquier peticion activa contra un host, confirma que pertenece al
programa:

```bash
# 1. Resolucion
dig +short "$HOST"

# 2. Certificado (nombre del CN/SAN del subject)
echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null \
  | openssl x509 -noout -subject -issuer -ext subjectAltName

# 3. HTTP headers (server, via CDN, ownership hints)
curl -sSI "https://$HOST" | sed -n '1,25p'

# 4. CT logs: subdominios que reveals la organizacion
curl -s "https://crt.sh/?q=%25.$DOMAIN&output=json" | jq -r '.[].name_value' | sort -u
```

Criterios para abortar un activo:
- El certificado muestra una organizacion distinta a la del programa.
- El host resuelve a un rango de un tercero known (AWS/GCP/Azure tenancy ajena).
- Es un host de un partner/provider que aparece en la policy como "third-party".

## 5. Alcance de pruebas de credenciales

- Password spraying contra cuentas propias o cuentas de test del programa: SI, con
  limites de lockout. Read the account lockout policy first.
- Credential stuffing con listas filtradas: **NO** salvo autorizacion explicita.
- Comprobar si una credencial filtrada funciona (login manual, 1 intento): SI,
  reportalo como exposicion de credenciales, no como acceso.
- No acceder a datos de otras personas: una vez autenticado, verifica que la
  sesion sea de tu cuenta y documenta solo metadatos.

## 6. Escalas de rate por defecto (si el programa no especifica)

| Actividad | Rate seguro | Nota |
|---|---|---|
| HTTP requests (scanning) | 2-5 req/s, concurrencia 5-10 | Nuclei: `-c 5 -rl 10` |
| Crawling | 1 req/s | katana `-c 1` |
| Subdomain enumeration (pasivo) | ilimitado (no toca el objetivo) | |
| Subdomain enumeration (activo) | 1 req/s por host | dnsx `-r 1` |
| Port scan (SYN) | 1000 pps, T3 | nmap `-T3 --max-rate 1000` |
| Port scan (connect/full) | T3 | |
| Fuzzing de directorios | 50-100 req/s | ffuf `-rate 50` |
| Password spray | 1 intento/cuenta, 1 cuenta/segundo | |
| DNS queries | 50 qps | |
| Bug bounty automation (bbot) | desactivar modulos de fuzzing agresivo | |

Nunca lances dos herramientas pesadas contra el mismo host al mismo tiempo. El
volumen combinado es la suma, no el maximo.

## 7. Plantilla `scope/scope.md`

```markdown
# Scope - <Programa> - <YYYY-MM-DD>

## Authorization
- Program: <HackerOne #ID / Bugcrowd / private>
- Safe harbor: "<cita literal de la policy>"
- Tester: <alias>
- Policy version / last updated: <fecha de la policy>

## In scope
| Asset | Type | Restrictions |
|---|---|---|

## Out of scope
| Asset | Reason |
|---|---|

## Prohibited techniques
- <lista>

## Rate limits
- <tabla>

## Test accounts provided
- <cuenta / password / notas>

## Escalation contact
- <nombre / email / horario>

## Open questions
- <lo que aun no se resolvio y a quien se escalo>
```

## 8. Regla de detencion

Si en cualquier momento surge la duda de si un activo o una tecnica esta
permitido: **para y pregunta**. Es infinitamente mas barato que un baneo.
