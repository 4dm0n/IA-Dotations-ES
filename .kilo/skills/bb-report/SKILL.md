---
name: bb-report
description: >-
  Use this skill to write, triage and deliver bug bounty reports: severity rating
  with CVSS and business context, the standard report structure (title, asset,
  preconditions, steps, PoC, impact, evidence, fix, retest), duplicate handling,
  platform-specific submission (HackerOne, Bugcrowd, Intigriti, private), disclosure
  and embargo handling, retest verification, and cleanup sign-off.
---

# bb-report / Reporte, Triaje y Disclosure

El reporte es el producto. Un finding correcto reportado mal = bounty perdida.

## 1. Anatomia del reporte

```markdown
# <Titulo en una frase: clase + donde + que permite>

## Summary
<2-3 frases. Que es, donde, que obtiene el atacante, por que importa. Sin jerga.>

## Severity
- CVSS v3.1: <vector> (<score>)
- Justificacion de negocio: <por que este impacto importa a esta empresa>
- Severidad del programa: <Critical/High/Medium/Low/Informative segun las guias del programa>

## Asset
- <host + path + metodo + parametro>
- In-scope: <segun policy, cita>
- Entorno: production / staging / dev

## Preconditions
- <Sin autenticacion | Usuario registrado (gratis) | Rol X | Cuenta de test del programa>
- <Explicito: "Este finding no requiere autenticacion">

## Steps to reproduce
1. <accion>
2. <accion>
...
(orden exacto, sin pasos implicitos)>

## Proof of Concept
<curl / python / request-response. Copiable tal cual.>

## Observed vs Expected
- Expected: <lo que la app deberia hacer>
- Actual: <lo que hace>

## Impact
- <Tecnico: que se obtiene exactamente>
- <Negocio: que consecuencia tiene para la empresa: datos, usuarios, dinero, reputacion, regulacion>
- <Alcance: cuantos usuarios/registros/tenants afectados>

## Evidence
- <capturas con timestamp, request/response redacted, logs>
- Ubicacion: <ficheros>

## Remediation
- <Fix concreto y primario>
- <Defensa en profundidad>

## Timeline / Notes
- <Fecha de descubrimiento, fecha de ultimo test, cualquier accion realizada y revertida>

## Retest
- <Como verificar que quedo corregido>
```

## 2. Titulos: formula y errores

Bien:
- `IDOR in GET /api/v1/orders/{id} allows any authenticated user to read other tenants' orders`
- `Stored XSS in review name renders in admin dashboard, enabling admin session hijack`
- `S3 bucket prod-assets allows public write, enabling distribution of malicious JS`

Mal:
- `Vulnerability found` (inutil)
- `XSS` (sin contexto)
- `Possible SQL injection in login` (no es "possible": es confirmed o no es nada)

## 3. Severidad: CVSS + contexto

CVSS v3.1 base. Calcula con precision y **justifica el vector**:

| Vector | Significado | Ejemplo de impacto |
|---|---|---|
| AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | Critical | RCE no autenticada |
| AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | High | BOLA con PII de otros usuarios |
| AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N | Medium | Reflected XSS con victima interactiva |
| AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N | Low | Info leak en header |

Reglas:
- **UI:R** si hace falta la interaccion de la victima (XSS reflejado, CSRF).
- **S:U** (sin cambio de scope) es lo habitual: el impacto esta en el mismo
  ambito de autoridad. Usa S:C solo si el impacto cruza a un sistema de
  seguridad distinto (por ejemplo, un sandbox de app comprometido).
- **C:H** solo si la confidencialidad de datos de OTROS usuarios se ve afectada
  de forma material. Leer tu propio perfil no es C:H.
- Si el programa usa su propia escala (muy comun: Critical/High/Medium/Low
  basado en impacto de negocio), usa la del programa y explica el mapeo.

Trampas de severidad:
- SQLi solo con lectura de una fila de una tabla de prueba -> Medium, no Critical.
- User enumeration sin impacto -> Informative.
- Missing headers sin impacto -> Informative.
- "Podria escalar a..." no cuenta: solo cuenta lo que demonstraste.

## 4. Evidencia

- Capturas: pantalla completa, reloj visible, barra de URL visible.
- Request/response: redacted. Nunca tokens completos, cookies, PII real.
- Anota la fecha/hora de cada captura.
- Una captura por afirmacion clave. No 30 capturas de lo mismo.
- Nombra los ficheros de forma descriptiva.

```bash
# Redaccion automatica antes de adjuntar
sed -E 's/(Authorization: Bearer )[A-Za-z0-9._-]+/\1[REDACTED]/g; \
        s/(session|token|csrf)[=:" ]+[A-Za-z0-9._-]{10,}/\1=[REDACTED]/Ig; \
        s/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/[EMAIL_REDACTED]/g' request.txt > request.redacted.txt
```

## 5. Triaje antes de enviar

Checklist de 15 segundos antes de pulsar "Submit":

- [ ] ¿El asset esta in-scope segun la policy?
- [ ] ¿La clase de vulnerabilidad no esta excluida explicitamente?
- [ ] ¿Lo reproduje desde limpio, al menos 2 veces?
- [ ] ¿El impacto esta demostrado, no inferido?
- [ ] ¿La severidad refleja el impacto real, no el peor caso teorico?
- [ ] ¿La evidencia esta redactada?
- [ ] ¿No hay datos personales de terceros sin redactar?
- [ ] ¿Los pasos son completos y no requieren contexto no documentado?
- [ ] ¿El PoC se ejecuta con los comandos que pongo?
- [ ] ¿Esta duplicado de un reporte previo mio? (busca en mis reportes)
- [ ] ¿El titulo es claro para un triage con 200 reportes al dia?
- [ ] ¿Hay una unica vulnerabilidad por reporte? (no 3 en 1)
- [ ] ¿Incluyo la mitigacion temporal si es aplicable?
- [ ] ¿El finding tiene sentido como bug y no como "mejora sugerida"?
- [ ] ¿Puse los labels que el programa usa?

## 6. Duplicados y agrupacion

- Un mismo bug en 40 subdominios -> **un reporte**, con la lista de hosts.
- Un mismo bug en 4 endpoints -> un reporte con una tabla de endpoints.
- Bug distinto en el mismo componente -> reportes separados (el triage cuenta diferente).
- Si ya reportaste y te responded "duplicate", no lo reenvies: responde con
  evidencia adicional de impacto.
- Si el programa tiene "out of scope" por clase, no lo reintentes con otro
  nombre.

## 7. Canales de entrega

| Plataforma | Formato | Notas |
|---|---|---|
| HackerOne | Web form + attachments | Adjunta PoC como `.py`/`.http`/`.md`. Video opcional. Respeta el titulo estandar |
| Bugcrowd | Submission form | Verifica la severidad contra su matriz; "Other" solo si aplica |
| Intigriti | Submission form | Prioriza impacto de negocio en el titulo |
| YesWeHack | Web app | Adjunta evidencia |
| Programa privado | Jira / email a security@ / Slack seguro | Si es email, usa cifrado PGP si lo proporcionan, y asunto claro |
| Directo | security.txt del objetivo | Solo si el objetivo tiene su propio VDP y lo permite |

Nunca publiques en redes sociales, blogs, Pastebin, GitHub, Discord ni en un
otro bounty program antes de la fecha de publicacion acordada.

## 8. Disclosure y embargo

- Ventana tipica: 90 dias, o la que indique el programa. Anota la fecha limite
  en el reporte y en tu calendario.
- Si no hay respuesta en el plazo del programa: un recordatorio cortés, no spam.
- Antes de publicar: revisa que ningun otro finder tenga un reporte abierto del
  mismo bug (no puedes saberlo; por eso se espera).
- Al publicar: redacta (no publiques tokens, PII ni exploits funcionales completos
  sin avisar al vendor).
- Si el vendor no responde tras el plazo y hay prueba de buena fe, la publicacion
  se permite segun la policy. Consulta el canal del programa antes.

## 9. Retest

Cuando el vendor confirme la correccion:

```bash
# 1. Reproducir el PoC original contra el mismo asset
python3 poc.py "$TARGET"          # debe FALLAR

# 2. Si falla, verificar por que: fix real o fix superficial
curl -sI "https://$HOST/patched-path" | grep -iE 'x-|strict|content-security'

# 3. Comprobar que no se rompió funcionalidad
curl -s -o /dev/null -w '%{http_code}\n' "https://$HOST/patched-path"
```

Redacta el retest en el reporte original: fecha, comandos, resultado, y si el
PoC sigue explotando (reabre el reporte, no abras otro nuevo).

## 10. Cleanup y cierre

Antes de cerrar el hunt:

```bash
# Verificar que no quedan artefactos en el objetivo
# (segun el registro en logs/artifacts.log)
cat logs/artifacts.log
```

```markdown
## Cleanup verification
| Artifact | Location | Removed | Verified (how) | Date |
|---|---|---|---|---|

## Environment changes
| Change | Reverted | Verified |
|---|---|---|

## Local artifacts with real data
| File | Encrypted/Deleted | Date |

## Tools installed for this hunt
| Tool | Uninstalled | Kept (why) |
```

## 11. Entregables finales

```
report/
  executive_summary.md      # para el cliente/decision maker, sin jerga
  report.md                 # reporte maestro
  findings/
    F-001_<slug>.md
    F-002_<slug>.md
  assets.md                 # inventario final
  impact_matrix.md          # severidad x impacto de negocio
  detections.md             # reglas y hunting (si hubo trabajo blue)
  remediation_plan.md       # plan con responsables y fechas
  limitations.md            # que no se probo y por que
```

El `executive_summary.md` no lleva nombres de herramientas ni payloads. Habla de
negocio: que se puede hacer, que datos estan expuestos, que hacen ahora, y cuanto
cuesta no hacer nada.
