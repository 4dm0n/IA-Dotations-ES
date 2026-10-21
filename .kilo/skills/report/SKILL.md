---
name: report
description: >
  Professional security assessment reporting framework for penetration testing and
  bug bounty engagements. Covers executive summaries, risk rating, CVSS mapping,
  evidence documentation, remediation guidance, ATT&CK mapping, and multi-format
  output (Markdown, PDF, HTML, SARIF).
metadata:
  category: security
  triggers:
    - report
    - reporting
    - pentest report
    - executive summary
    - risk rating
    - cvss
    - cvss calculator
    - remediation
    - attack mapping
    - sarif
    - bug bounty report
    - writeup
---

# Security Assessment Reporting / Reporte de Evaluacion de Seguridad

**Bilingual Professional Reference / Referencia Profesional Bilingue**

---

## Reporting Principles / Principios de Reporte

| Principle / Principio | Description / Descripcion |
|---|---|
| **Evidence over opinion / Evidencia sobre opinion** | Every claim must be backed by reproducible output |
| **Executive readability / Legibilidad ejecutiva** | The first page must be readable by a non-technical decision maker |
| **Remediation over exploitation / Remediacion sobre explotacion** | The report teaches, it does not showcase |
| **Risk over CVSS / Riesgo sobre CVSS** | Business context determines severity, not the vector alone |
| **Reproducibility / Reproducibilidad** | Any engineer must be able to re-verify the finding |
| **No exploit theater / Sin teatro de explotacion** | Minimize weaponization; show impact, not weapons |

**Language rule:** Default to the language of the engagement contract. If unspecified, ask. Never mix languages within a single finding.

**Regla de idioma:** Usa el idioma del contrato de engagement. Si no esta especificado, pregunta. Nunca mezcles idiomas dentro de un mismo hallazgo.

---

## Report Structure / Estructura del Reporte

### Standard Pentest Report / Reporte Pentest Estandar

```
1. Executive Summary              / Resumen Ejecutivo
2. Scope and Methodology           / Alcance y Metodologia
3. Findings Summary                / Resumen de Hallazgos
4. Detailed Findings               / Hallazgos Detallados
5. Attack Path Narrative           / Narrativa de Ruta de Ataque
6. Remediation Roadmap             / Hoja de Ruta de Remediacion
7. Appendices                      / Anexos
```

### Bug Bounty Report / Reporte de Bug Bounty

```
1. Summary                        / Resumen
2. Vulnerability Type & Severity   / Tipo de Vulnerabilidad y Severidad
3. Affected Asset                  / Activo Afectado
4. Steps to Reproduce              / Pasos para Reproducir
5. Proof of Concept                / Prueba de Concepto
6. Impact                          / Impacto
7. Remediation                     / Remediacion
8. References                      / Referencias
```

---

## Phase 1: Executive Summary / Fase 1: Resumen Ejecutivo

**Length:** One page maximum. Written for a decision maker, not a scanner.

**Target audience:** CISO, CTO, compliance officer, engineering manager.

**Template / Plantilla:**

```markdown
## Executive Summary / Resumen Ejecutivo

**Client / Cliente:** <Organization>
**Assessment / Evaluacion:** <Type> - <Dates>
**Assessor / Evaluador:** <Team / Individual>
**Overall Risk / Riesgo Global:** <Critical | High | Medium | Low>

### Context / Contexto
<A two or three sentence description of what was tested, why, and the
business purpose of the assessment.>

### Key Outcomes / Resultados Clave
- <N> findings were identified, of which <M> were rated Critical or High.
- The primary attack path enabled <impact>, which represents <business risk>.
- <Positive observation about the client's existing controls.>

### Immediate Actions / Acciones Inmediatas
1. <Action with owner and deadline>
2. <Action with owner and deadline>
3. <Action with owner and deadline>

### Risk Rating / Calificacion de Riesgo
| Severity / Severidad | Count / Cantidad | Summary / Resumen |
|---|---|---|
| Critical / Critica | N | <one line> |
| High / Alta | N | <one line> |
| Medium / Media | N | <one line> |
| Low / Baja | N | <one line> |
| Informational / Informativa | N | <one line> |
```

**Writing rules / Reglas de redaccion:**
- No tool names, no commands, no payloads
- No CVE numbers unless directly relevant to a decision
- Quantify impact in business terms (records, users, revenue, downtime)
- State what is working, not only what is broken

---

## Phase 2: Scope and Methodology / Fase 2: Alcance y Metodologia

```markdown
## Scope and Methodology / Alcance y Metodologia

### In Scope / En Alcance
| Asset / Activo | Type / Tipo | Environment / Entorno |
|---|---|---|
| api.example.com | Web API | Production |
| 10.0.1.0/24 | Network range | Staging |

### Out of Scope / Fuera de Alcance
- Third-party SaaS providers
- Social engineering and physical testing
- Denial of service testing
- <specific exclusions>

### Methodology / Metodologia
<Reference the framework used: PTES, OSSTMM, OWASP WSTG, NIST SP 800-115.>

| Phase / Fase | Activities / Actividades |
|---|---|
| Reconnaissance | Passive subdomain enumeration, DNS resolution, service fingerprinting |
| Scanning | Port and service enumeration, vulnerability validation |
| Exploitation | Controlled validation of confirmed findings |
| Post-exploitation | Privilege assessment, lateral movement assessment, impact demonstration |

### Testing Window / Ventana de Pruebas
- Start / Inicio: <timestamp and timezone>
- End / Fin: <timestamp and timezone>
- Rate limiting / Limite de tasa: <requests per second / concurrency>

### Tools / Herramientas
| Tool / Herramienta | Version / Version | Purpose / Proposito |
|---|---|---|
| <tool> | <version> | <purpose> |

### Limitations / Limitaciones
- <e.g. Credentialed scanning was not performed on the internal network>
- <e.g. Source code was not reviewed>
- <e.g. Physical and wireless testing were out of scope>
```

---

## Phase 3: Risk Rating Framework / Fase 3: Marco de Calificacion de Riesgo

### CVSS v3.1 Base Scoring / Puntaje Base CVSS v3.1

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

| Metric / Metrica | Values / Valores | Description / Descripcion |
|---|---|---|
| **AV** - Attack Vector | N, A, L, P | Network, Adjacent, Local, Physical |
| **AC** - Attack Complexity | L, H | Low, High |
| **PR** - Privileges Required | N, L, H | None, Low, High (scope-dependent) |
| **UI** - User Interaction | N, R | None, Required |
| **S** - Scope | U, C | Unchanged, Changed |
| **C/I/A** - Impact | N, L, H | None, Low, High |

**Qualitative severity scale / Escala cualitativa de severidad:**

| Score / Puntaje | Rating / Calificacion |
|---|---|
| 9.0 - 10.0 | Critical / Critica |
| 7.0 - 8.9 | High / Alta |
| 4.0 - 6.9 | Medium / Media |
| 0.1 - 3.9 | Low / Baja |
| 0.0 | None / Ninguna |

### Business Risk Overlay / Ajuste de Riesgo de Nego

CVSS alone does not determine report severity. Apply a business context multiplier.

El CVSS por si solo no determina la severidad en el reporte. Aplica un multiplicador de contexto de negocio.

| Factor / Factor | Effect / Efecto |
|---|---|
| Asset is internet-facing / Activo expuesto a internet | Increase / Aumentar |
| Handles regulated data (PII, PCI, PHI) / Maneja datos regulados | Increase / Aumentar |
| Prevents detection of other findings / Impide detectar otros hallazgos | Increase / Aumentar |
| Prevents remediation of other findings / Impide remediar otros hallazgos | Increase / Aumentar |
| Compensating control exists (WAF, MFA, monitoring) / Control compensatorio | Decrease / Disminuir |
| Internal-only, low-value asset / Activo interno de bajo valor | Decrease / Disminuir |

### Final Severity Decision Rule / Regla de Decision de Severidad Final

```
Final Severity = max(CVSS-derived severity, Business-context severity)
Never downgrade below CVSS unless a compensating control is documented and tested.
```

```
Severidad Final = max(severidad derivada de CVSS, severidad de contexto de negocio)
Nunca bajar por debajo de CVSS a menos que exista un control compensatorio documentado y probado.
```

---

## Phase 4: Detailed Finding Template / Fase 4: Plantilla de Hallazgo Detallado

```markdown
### <ID>: <Title> / <Titulo>

| Field / Campo | Value / Valor |
|---|---|
| **ID / ID** | PT-001 |
| **Title / Titulo** | <Clear, specific, impact-oriented title> |
| **Severity / Severidad** | <Critical \| High \| Medium \| Low \| Informational> |
| **CVSS / CVSS** | <vector> (<score>) |
| **CWE / CWE** | CWE-<number> - <name> |
| **OWASP / OWASP** | <A0x:2021 - category> |
| **Affected Asset / Activo Afectado** | <host, endpoint, or component> |
| **Location / Ubicacion** | <specific file, line, endpoint, parameter> |
| **Discovery Date / Fecha de Descubrimiento** | YYYY-MM-DD |
| **Status / Estado** | Open |
| **References / Referencias** | <links> |

#### Description / Descripcion
<What the vulnerability is, in plain technical language. Explain the flaw and
where it exists. Do not include the exploit payload here.>

#### Impact / Impacto
<What an attacker can achieve. Be specific and quantify. Describe the realistic
attacker position required. State clearly what would be required for abuse.>

#### Steps to Reproduce / Pasos para Reproducir
1. <Step with exact request or action>
2. <Step>
3. <Step>

#### Evidence / Evidencia
```
<Request, response, log excerpt, or screenshot reference>
```

#### Remediation / Remediacion
<Specific, actionable fix. Reference the exact component. Include a code-level
example when relevant.>

#### Verification / Verificacion
<How the client confirms the fix is effective.>

#### References / Referencias
- <Link>
```

---

## Phase 5: Evidence Standards / Fase 5: Estandares de Evidencia

| Element / Elemento | Standard / Estandar |
|---|---|
| **Screenshots / Capturas** | Full window, timestamp visible, URL bar visible, finding highlighted |
| **HTTP requests / Peticiones HTTP** | Complete request and response with headers, redact live tokens |
| **Command output / Salida de comandos** | Full unedited output, include the command line used |
| **Log excerpts / Extractos de log** | Include enough context lines, show timestamp range |
| **File references / Referencias de archivo** | Use `path/to/file.ext:line_number` format |
| **Credentials / Credenciales** | Redact all but the last 4 characters, note redaction explicitly |

**Redaction policy / Politica de ocultamiento:**
- Never publish live tokens, API keys, or passwords in the report
- Redact session identifiers and internal hostnames where they add no value
- Keep the evidence sufficient for the client to reproduce

---

## Phase 6: Attack Path Narrative / Fase 6: Narrativa de Ruta de Ataque

Explains how findings chain together to form a complete compromise. This is often the most valuable section for the client.

Explica como los hallazgos se encadenan para formar un compromiso completo. Esta suele ser la seccion mas valiosa para el cliente.

```markdown
## Attack Path Narrative / Narrativa de Ruta de Ataque

### Summary / Resumen
<A concise description of the end-to-end path from initial access to
objective achievement, including the number of findings involved and the
total time to compromise estimate.>

### Path / Ruta

```
[Step 1] Initial Access
    |  Finding PT-001 (High) - Unauthenticated RCE on api.example.com
    v
[Step 2] Credential Access
    |  Finding PT-004 (Medium) - Service account token in environment variable
    v
[Step 3] Lateral Movement
    |  Finding PT-007 (High) - Unrestricted SMB share on file01
    v
[Step 4] Objective Achieved
       Access to customer records database (est. 480,000 rows)
```

### Broken Controls / Controles Rotos
| Control / Control | Broken By / Roto Por | Consequence / Consecuencia |
|---|---|---|
| Network segmentation | PT-001 | Direct access to internal services |
| Credential isolation | PT-004 | Service account reuse across tiers |
```

---

## Phase 7: Remediation Roadmap / Fase 7: Hoja de Ruta de Remediacion

```markdown
## Remediation Roadmap / Hoja de Ruta de Remediacion

### Priority 1 - Immediate (0-7 days) / Prioridad 1 - Inmediato
| ID | Finding | Action / Accion | Owner / Responsable | Effort |
|---|---|---|---|---|
| PT-002 | <title> | <action> | <team> | S |

### Priority 2 - Short Term (30 days) / Prioridad 2 - Corto Plazo
| ID | Finding | Action / Accion | Owner / Responsable | Effort |
|---|---|---|---|---|

### Priority 3 - Medium Term (90 days) / Prioridad 3 - Mediano Plazo
| ID | Finding | Action / Accion | Owner / Responsable | Effort |

### Effort scale / Escala de esfuerzo
| Size | Meaning / Significado |
|---|---|
| S | Less than 1 day / Menos de 1 dia |
| M | 1-5 days / 1-5 dias |
| L | More than 5 days / Mas de 5 dias |

### Systemic Recommendations / Recomendaciones Sistematicas
<Root cause patterns observed across findings, e.g. "no input validation layer",
"secrets stored in plaintext", "no CI security scanning". Address the class,
not just the instances.>
```

---

## Phase 8: ATT&CK Mapping / Fase 8: Mapeo ATT&CK

```markdown
## MITRE ATT&CK Mapping / Mapeo MITRE ATT&CK

| Tactic / Tactica | Technique / Tecnica | ID | Findings / Hallazgos |
|---|---|---|---|
| Initial Access | Exploit Public-Facing Application | T1190 | PT-001 |
| Execution | Command and Scripting Interpreter: Unix Shell | T1059.004 | PT-001 |
| Credential Access | OS Credential Dumping: SAM | T1003.001 | PT-004 |
| Lateral Movement | Remote Services: SMB/Windows Admin Shares | T1021.002 | PT-007 |
| Collection | Data from Local System | T1005 | PT-009 |
```

---

## Phase 9: Output Formats / Fase 9: Formatos de Salida

### SARIF (for CI/CD integration) / SARIF (para integracion CI/CD)

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Security Assessment",
          "informationUri": "https://example.com"
        }
      },
      "results": [
        {
          "ruleId": "PT-001",
          "level": "error",
          "message": { "text": "Unauthenticated RCE in file upload handler" },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": { "uri": "src/upload/handler.ts" },
                "region": { "startLine": 42 }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### HTML Report Generation / Generacion de Reporte HTML

```bash
# Markdown to HTML
pandoc report.md -o report.html --standalone --toc --css report.css

# With template
pandoc report.md -o report.html --template=template.html --toc

# PDF via LaTeX
pandoc report.md -o report.pdf --pdf-engine=xelatex -V geometry:margin=1in

# Markdown to DOCX
pandoc report.md -o report.docx --toc
```

### Evidence Directory Structure / Estructura del Directorio de Evidencia

```
engagement_<client>_<date>/
  report/
    report.md
    report.pdf
    report.html
  evidence/
    PT-001/
      request.txt
      response.txt
      screenshot_01.png
      commands.txt
    PT-002/
      ...
  raw/
    nmap/
    nuclei/
    httpx/
    subdomains/
  notes/
    methodology.md
    scope.md
    timeline.md
  tools/
    versions.txt
```

---

## Phase 10: Quality Checklist / Fase 10: Checklist de Calidad

### Before Delivery / Antes de la Entrega

- [ ] Every finding is reproducible from the report alone
- [ ] Every finding has a working remediation with a named owner
- [ ] Severity is justified with business context, not only CVSS
- [ ] No live credentials, tokens, or session IDs in the report
- [ ] Executive summary is readable by a non-technical stakeholder
- [ ] Scope matches the engagement agreement exactly
- [ ] Limitations and untested areas are explicitly stated
- [ ] Findings are cross-referenced with ATT&CK where relevant
- [ ] Attack path narrative explains the combined risk
- [ ] Spelling, formatting, and figure numbering are consistent
- [ ] Document metadata (dates, version, author, distribution list) is set
- [ ] A second reviewer has validated the technical accuracy

### Confidentiality Handling / Manejo de Confidencialidad

- [ ] Report is marked with the correct classification
- [ ] Distribution list is restricted and explicit
- [ ] Encrypted delivery for reports containing sensitive findings
- [ ] Retention and destruction date is agreed with the client
- [ ] Secure deletion of raw evidence when the retention period ends

---

## Common Pitfalls / Errores Comunes

| Pitfall / Error | Solution / Solucion |
|---|---|
| Report is a scanner dump | Rewrite every finding in plain language with business impact |
| No reproducibility | Include the exact steps, requests, and environment |
| CVSS inflation | Apply business context; justify the vector choice |
| Executive summary is technical | Write it for a decision maker; move detail to findings |
| Remediation is generic | Reference the exact component, file, and configuration |
| Missing attack path | Synthesize how findings combine into a compromise |
| Leaked secrets in evidence | Redact all live tokens before delivery |
| No owner assigned | Every remediation row needs a named team |
| Untested claims marked confirmed | State verification method for each finding |

---

## References / Referencias

- **CVSS v3.1 Specification**: https://www.first.org/cvss/v3.1/specification-document
- **CVSS Calculator**: https://www.first.org/cvss/calculator/3.1
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **PTES**: http://www.pentest-standard.org/
- **MITRE ATT&CK**: https://attack.mitre.org/
- **SARIF Spec**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **EPSS**: https://www.first.org/epss/
- **CWE**: https://cwe.mitre.org/
