---
name: opsec
description: >
  Operational security framework for authorized penetration testing engagements.
  Covers detection evasion, traffic hygiene, infrastructure separation, anti-forensics
  considerations, identity protection, legal compliance, and attribution risk reduction.
metadata:
  category: security
  triggers:
    - opsec
    - operational security
    - detection evasion
    - anti-forensics
    - traffic hygiene
    - stealth
    - attribution
    - detection risk
    - blue team detection
    - cover assessment
---

# Operational Security Framework / Marco de Seguridad Operacional

**Bilingual Professional Reference / Referencia Profesional Bilingue**

---

## Authorization Gate / Control de Autorizacion

OPSEC exists to protect the tester, not to conceal wrongdoing. Every technique in this skill requires written authorization.

La seguridad operacional existe para proteger al evaluador, no para ocultar actividad ilicita. Cada tecnica de esta skill requiere autorizacion escrita.

| Check / Verificacion | Requirement / Requisito |
|---|---|
| **Written authorization / Autorizacion escrita** | Signed scope covering all techniques used |
| **Rules of engagement / Reglas deacompanamiento** | Agreed acceptable and prohibited techniques |
| **Detection testing permitted / Deteccion permitida** | Explicit permission to test blue team visibility |
| **Logging expectation / Expectativa de registro** | Whether activity is logged, monitored, or must be blinded |
| **Emergency contact / Contacto de emergencia** | Who to notify if the client EDR blocks or flags activity |
| **Law enforcement contact / Contacto de applicables** | Procedure if activity is misattributed to a third party |

**Prohibition / Prohibicion:** OPSEC techniques must never be used to attack third parties, evade law enforcement in an unrelated matter, or hide unauthorized access. If authorization is absent, stop.

**Tecnicas de OPSEC nunca deben usarse para atacar terceros, evadir a las autoridades en asuntos no relacionados, ni ocultar accesos no autorizados. Si falta la autorizacion, detente.**

---

## Quick Reference / Referencia Rapida

| Layer / Capa | Objective / Objetivo | Primary Control / Control Primario |
|---|---|---|
| **Infrastructure / Infraestructura** | Do not pivot from tester to client | VPN or dedicated egress IP |
| **Traffic / Trafico** | Do not look like a scanner | Rate control, realistic headers, timing |
| **Identity / Identidad** | Do not expose the tester | Separate account, separate device profile |
| **Artifacts / Artefactos** | Leave no tooling behind | In-memory execution, cleanup checklist |
| **Attribution / Atribucion** | Avoid misattribution | Client-side whitelisting, engagement tags |
| **Legal / Legal** | Stay defensible | Scope document, timestamps, written authorization |

---

## Phase 1: Infrastructure Separation / Fase 1: Separacion de Infraestructura

### Rules / Reglas

1. **Never scan directly from a personal machine / Nunca escanear desde una maquina personal.** The client IP becomes your IP in every log.
2. **Never scan from internal corporate infrastructure / Nunca escanear desde infraestructura corporativa interna.** Traffic from your office network is your employer's liability.
3. **Use a dedicated egress / Usa una salida dedicada.** VPN, VPS, or an authorized jump host owned by the client.
4. **One engagement, one source IP / Un engagement, una IP de origen.** This makes client-side log correlation tractable.

### Recommended Setup / Configuracion Recomendada

```bash
# Option A: Client-provided VPN (preferred)
# Ask for a VPN profile or an allowlisted egress IP before starting.

# Option B: Dedicated VPS
# Create a throwaway VPS for the engagement.
# Document: provider, region, IP, destruction date.
# Example provisioning notes:
#   Provider: <provider>
#   Region: <region closest to client infra>
#   IPv4: <assigned IP>
#   Destroy by: YYYY-MM-DD

# Option C: Local hypervisor lab
# If the client provides an isolated lab network, run all tooling there.

# Verify your egress before touching the target
curl -s https://api.ipify.org; echo
# Record it in notes/timeline.md
```

### Client IP Allowlisting / Lista de IPs Permitidas del Cliente

Ask the client to allowlist the engagement egress so traffic is not dropped or blocked. Provide this in the report deliverable:

```markdown
## Engagement Egress / Salida del Engagement
- IPv4: <your egress IP>
- IPv6: <if applicable>
- Source ports: <range if needed>
- Valid from: YYYY-MM-DD to YYYY-MM-DD
- Purpose: <authorized engagement name and reference>
```

**If allowlisting is not possible / Si no es posible la lista blanca:** assume all traffic will be logged and possibly blocked. Increase rate control and expect interruptions.

---

## Phase 2: Traffic Hygiene / Fase 2: Higiene de Trafico

### Rate Control / Control de Tasa

Aggressive scanning is the single most common cause of engagement disruption and premature detection.

El escaneo agresivo es la causa mas comun de interrupciones del engagement y deteccion prematura.

```bash
# Nmap: polite timing, explicit rate cap
nmap -T2 --max-rate 100 --max-retries 2 --host-timeout 60s -iL targets.txt -oA scan

# Nuclei: concurrency and rate limits
nuclei -l targets.txt -c 5 -bulk-size 5 -rate-limit 25 -o results.txt

# ffuf: low concurrency
ffuf -u https://target/FUZZ -w wordlist.txt -t 10 -rate 20 -o results.json

# HTTPX: tuned
httpx -l targets.txt -threads 10 -rate-limit 20 -o results.txt
```

### Realistic Request Profiles / Perfiles de Peticion Realistas

```bash
# Randomize user agent within a legitimate browser set
ua=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15" \
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0")
curl -A "${ua[$((RANDOM % ${#ua[@]}))]}" https://target/

# Consistent headers within a session (do not rotate headers mid-session)
curl -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
     -H "Accept-Language: en-US,en;q=0.9" \
     -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0 Safari/537.36" \
     https://target/

# Do not send impossible header combinations
# (a Chrome UA with a curl Accept header is a strong scanner signal)
```

### Timing Behavior / Comportamiento de Temporizacion

| Behavior / Comportamiento | Scanner Signal / Senal de escaner | Realistic Alternative / Alternativa realista |
|---|---|---|
| Uniform inter-request delay | Robotic | Vary 0.2s to 1.5s with jitter |
| All requests in one burst | Aggressive | Follow a navigation-like sequence |
| Only 404s, no 200s | Enumeration | Include baseline requests to known-good paths |
| Identical bodies every time | Automated | Vary parameters within realistic ranges |

```bash
# Add jitter between requests
for url in $(cat urls.txt); do
  curl -s -o /dev/null "$url"
  sleep $(awk -v seed=$RANDOM 'BEGIN{srand(seed); print rand()*1.3}')
done
```

### WAF and Rate-Limit Handling / Manejo de WAF y Limites de Tasa

```bash
# Detect a WAF or a block page
curl -s -o /dev/null -w "%{http_code}\n" https://target/       # 403 or 429 suggests blocking
curl -sI https://target/ | grep -iE "server:.*(cloudflare|akamai|incapsula|sucuri|modsecurity)"

# If blocked: stop, slow down, and notify the client contact.
# Do not attempt to evade a WAF that is explicitly protecting a production asset
# without written permission.
```

---

## Phase 3: Identity and Credential Hygiene / Fase 3: Higiene de Identidad y Credenciales

### Account Separation / Separacion de Cuentas

| Practice / Practica | Rationale / Justificacion |
|---|---|
| Use a dedicated testing account, never your own | Personal accounts create traceability and liability |
| Never reuse personal API tokens | Tokens are logged and traced |
| Use client-issued credentials only | Proves authorization and avoids account lockout disputes |
| Store engagement credentials in a password manager | Prevents leakage via shell history and files |
| Use a separate browser profile for testing | Avoids cookie and extension contamination |

```bash
# Use a dedicated browser profile directory
firefox --profile /tmp/engagement_profile https://target/

# Store credentials outside the shell history
read -s -p "Token: " TOKEN; export TOKEN

# Never embed credentials directly in commands that get logged in notes
# Use environment variables and reference them
curl -H "Authorization: Bearer $TOKEN" https://target/api
```

### Cross-Engagement Isolation / Aislamiento Entre Engagements

- Never reuse infrastructure, accounts, or wordlists that could link two clients
- Separate output directories and note files per engagement
- Destroy or archive engagement-specific infrastructure per the retention agreement

---

## Phase 4: Artifact Minimization / Fase 4: Minimizacion de Artefactos

### In-Memory Execution / Ejecucion en Memoria

```bash
# Python without touching disk
python3 -c "import requests; print(requests.get('https://target/').status_code)"

# Piping a script directly into the interpreter
curl -s https://example.com/tool.py | python3 -

# Use a temporary directory that is removed immediately
TMPD=$(mktemp -d); trap 'rm -rf "$TMPD"' EXIT

# Use /dev/shm on Linux for a RAM-backed path
cp tool /dev/shm/ && /dev/shm/tool; rm -f /dev/shm/tool
```

### Artifact Naming / Nomenclatura de Artefactos

```bash
# Use engagement-scoped, obviously-authorized names so client blue teams
# can positively identify the traffic instead of escalating it as an incident.
export ENGAGEMENT_ID="PT-2026-0412-EXAMPLE"
export TOOL_PREFIX="${ENGAGEMENT_ID}_"
curl -A "Authorized-Pentest/${ENGAGEMENT_ID}" https://target/
```

**Prefer a coordinated allowlist or an explicit User-Agent token over any technique that hides the traffic's origin.** Concealment breaks the client's ability to respond, which is itself a harm.

**Prefiere una lista blanca coordinada o un token explicito de User-Agent antes que cualquier tecnica que oculte el origen del trafico.** El ocultamiento impide la respuesta del cliente, lo que en si mismo es un dano.

### Cleanup Discipline / Disciplina de Limpieza

- Maintain a running artifact inventory during the engagement
- Remove tooling from every host at the end of each phase, not just at the end
- Verify removal; do not assume it
- Document what was uploaded and where, so the client can verify

```bash
# Track uploads
echo "$(date -u +%FT%TZ) uploaded $TOOL to $HOST:$PATH" >> notes/artifacts.log

# Verify removal
for f in $TOOLS; do
  ssh $HOST "test -e $f && echo 'STILL PRESENT: $f'"
done
```

---

## Phase 5: Detection Surface Awareness / Fase 5: Conciencia de la Superficie de Deteccion

The goal is not to be invisible. The goal is to be **identifiable as authorized**.

El objetivo no es ser invisible. El objetivo es ser **identificable como autorizado**.

### Common Client-Side Detections / Detecciones Comunes del Cliente

| Detection / Deteccion | Typical Signal / Senal Tipica | Response / Respuesta |
|---|---|---|
| EDR behavioral rule | Script interpreter spawned from web service | Coordinate an allowlist or schedule |
| SIEM network anomaly | High port count from one source | Agreed allowlist for the egress IP |
| WAF log | Automated 4xx pattern | Reduce rate, notify contact |
| NDR port sweep detection | SYN sweep signature | Same as SIEM |
| Auth anomaly | Unusual source for a known account | Use client-issued service accounts |
| File integrity | Binary dropped in a web root | Use in-memory execution |

### Detection Testing as an Explicit Deliverable / Pruebas de Deteccion como Entregable

If the contract includes blue team detection testing, structure it as a separate objective:

```markdown
## Detection Assessment / Evaluacion de Deteccion

| Technique / Tecnica | Detected / Detectado | Tool / Herramienta | Latency / Latencia | Notes / Notas |
|---|---|---|---|---|
| Network port sweep | Yes | CrowdStrike Falcon | 42s | Alert on SYN sweep signature |
| Web content fuzzing | No | - | - | Not covered by current rules |
| Credential spray | Yes | Microsoft Defender for Cloud | 8m | Detected at IdP |
```


### Escalation Procedure / Procedimiento de Escalacion

If the client detects and blocks or escalates your activity:

1. Stop active scanning immediately
2. Capture the alert details (notebook screenshot, email, ticket ID) as evidence
3. Notify the agreed engagement contact using the agreed channel
4. Provide the engagement reference, source IPs, and expected activity description
5. Do not attempt to bypass the control; wait for guidance
6. Record the incident in the engagement timeline and note it in the report

**Never work around an active client security response without explicit authorization to do so.**

**Nunca eludir una respuesta de seguridad activa del cliente sin autorizacion explicita para hacerlo.**

---

## Phase 6: Legal and Compliance / Fase 6: Legal y Cumplimiento

### Authorization Record / Registro de Autorizacion

Maintain a signed artifact. If the engagement is ever questioned, this is the primary defense.

Mantiene un artefacto firmado. Si el engagement se cuestiona alguna vez, esta es la defensa principal.

```markdown
## Engagement Authorization Record

| Field | Value |
|---|---|
| Engagement ID | PT-2026-0412-EXAMPLE |
| Client organization | <Legal entity name> |
| Authorizing signatory | <Name, title> |
| Authorization date | YYYY-MM-DD |
| Authorization expiry | YYYY-MM-DD |
| Scope (in) | <assets, CIDRs, domains, IP list> |
| Scope (out) | <explicit exclusions> |
| Permitted techniques | <permitted technique list> |
| Prohibited techniques | <DoS, social engineering, physical, etc.> |
| Testing window | <start - end, timezone> |
| Emergency contact (client) | <name, phone> |
| Emergency contact (assessor) | <name, phone> |
| Third-party notification | <cloud provider, ISP, CERT procedure> |
```

### Third-Party Notification / Notificacion a Terceros

Some infrastructure is shared. Know when notification is required before testing:

| Infrastructure / Infraestructura | Notification / Notificacion |
|---|---|
| **Public cloud (AWS, Azure, GCP)** | Check provider policies and abuse reporting channels |
| **CDN / WAF provider (Cloudflare, Akamai)** | Provider-specific authorized scanning policy; request allowlisting |
| **Colocation / hosting** | Check the AUP and the provider's acceptable use policy |
| **Registrar / DNS** | Consider registrar abuse contacts for domain-level testing |
| **Internet backbone / IXP** | Generally no, unless testing shared infrastructure |
| **Third-party SaaS applications** | Almost always out of scope; require client coordination |

**If a target is hosted by a third party, get written confirmation that the client has permission to test it.**

**Si un objetivo esta alojado por un tercero, obtén confirmacion escrita de que el cliente tiene permiso para probarlo.**

### Data Handling and Retention / Manejo y Retencion de Datos

- Encrypt all engagement data at rest
- Define and enforce a destruction date for evidence, notes, and infrastructure
- Collect the minimum data necessary to prove impact
- Treat any captured data as confidential client data with the same protections
- Never reuse captured client data in another engagement

---

## Phase 7: Operational Checklist / Fase 7: Checklist Operacional

### Pre-Engagement / Pre-Engagement

- [ ] Signed authorization and rules of engagement on file
- [ ] Scope allowlist and denylist confirmed in writing
- [ ] Egress IP identified and requested for allowlisting
- [ ] Dedicated testing account created by the client
- [ ] Engagement contact and escalation channel confirmed
- [ ] Detection testing expectations agreed
- [ ] Data retention and destruction date agreed
- [ ] Clean, isolated tooling environment prepared
- [ ] Output directory structure created and version controlled

### During Engagement / Durante el Engagement

- [ ] Rate limits applied and respected
- [ ] Traffic stays on approved source IPs
- [ ] Credentials and tokens kept out of shell history
- [ ] Artifacts inventory maintained
- [ ] Hosts cleaned at the end of each phase
- [ ] Timeline and command history logged
- [ ] Any client detection escalated per the agreed procedure
- [ ] Scope re-confirmed before testing new asset classes

### Post-Engagement / Post-Engagement

- [ ] All tooling removed from all systems, verified not assumed
- [ ] Test accounts and credentials revoked by the client
- [ ] Egress infrastructure destroyed or returned
- [ ] Evidence encrypted and stored per the retention agreement
- [ ] Detection findings and incidents documented for the report
- [ ] Written confirmation received that the environment is back to baseline

---

## Best Practices / Mejores Practicas

### Do / Hacer
- [ ] Use a **dedicated egress** that the client can allowlist
- [ ] Be **identifiable as authorized** rather than invisible
- [ ] **Rate limit** everything, always
- [ ] **Remove artifacts** continuously, not only at the end
- [ ] Keep a **live artifact inventory** and a **timestamped timeline**
- [ ] **Escalate** immediately when the client detects you
- [ ] Keep **written authorization** accessible for the whole engagement

### Don't / No hacer
- [ ] Scan from a personal machine or corporate network
- [ ] Attempt to defeat an active client security response without permission
- [ ] Leave tooling or test accounts behind
- [ ] Reuse credentials, tokens, or infrastructure across engagements
- [ ] Collect more data than needed to prove impact
- [ ] Test third-party hosted assets without written confirmation
- [ ] Omit detection events from the final report

---

## Common Pitfalls / Errores Comunes

| Pitfall / Error | Solution / Solucion |
|---|---|
| Engagement blocked by client WAF | Request allowlisting in advance; keep a slow profile ready |
| Traffic looks like a mass scanner | Use coordinated allowlist or engagement User-Agent token |
| Misattribution to a third party | Client-side engagement tags, allowlists, notify the ISP or provider |
| Tools left on a production host | Artifact inventory plus per-phase cleanup and verification |
| Shell history leaks credentials | Read secrets into environment variables, never inline them |
| Blue team escalates as a real incident | Pre-agreed escalation contact and reference ID |
| Scope creep during the engagement | Re-check the scope list before every new asset class |
| Losing evidence of what was tested | Timestamped timeline and raw tool output in the engagement directory |
| Stale infrastructure causes attribution issues | Destroy egress on the agreed date, document the destruction |

---

## References / Referencias

- **PTES**: http://www.pentest-standard.org/
- **NIST SP 800-115**: https://csrc.nist.gov/publications/detail/sp/800-115/final
- **MITRE ATT&CK**: https://attack.mitre.org/tactics/TA0003/
- **Cloudflare Authorized Scanning**: https://www.cloudflare.com/application-security/terms/
- **AWS Penetration Testing Policy**: https://aws.amazon.com/legal/pen-testing/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
