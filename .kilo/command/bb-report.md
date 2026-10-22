---
description: Genera el reporte de bug bounty completo - executive summary, findings, CVSS, evidencia y plan de remediacion
---

# /bb-report

Genera los entregables del reporte. Carga `bb-report` y `bb-blue`.

## Uso

```
/bb-report [F-001,F-002 | --all] [--format md|pdf|html|sarif] [--lang es|en] [--exec-summary]
```

## Genera

```
report/
  executive_summary.md    # sin jerga ni nombres de herramientas
  report.md               # reporte maestro con todos los findings
  findings/
    F-001_<slug>.md
    F-002_<slug>.md
  assets.md               # inventario de activos
  impact_matrix.md        # severidad x impacto de negocio
  detections.md           # reglas de deteccion (si hubo trabajo blue)
  remediation_plan.md     # acciones, responsables, prioridad
  limitations.md          # que no se probo y por que
```

## Estructura por finding

1. Titulo (clase + donde + que permite)
2. Summary (2-3 frases)
3. Severity (CVSS v3.1 + justificacion de negocio + severidad del programa)
4. Asset (host + path + metodo + param + entorno)
5. Preconditions
6. Steps to reproduce (numerados, completos)
7. PoC (copiable)
8. Observed vs Expected
9. Impact (tecnico + negocio + alcance)
10. Evidence (redacted)
11. Remediation (primario + defensa en profundidad)
12. Timeline
13. Retest

## Executive summary

Sin: nombres de herramientas, payloads, IPs internas, PII.
Con: que se puede hacer, que datos estan expuestos, volumen afectado, riesgo
de negocio, y el plan de accion con prioridad.

## Formatos

- `md` (default): markdown estructurado.
- `pdf`: via `pandoc report.md -o report.pdf` (si esta disponible) o plantilla HTML.
- `html`: plantilla autonoma con estilos.
- `sarif`: para integracion con scanners (opcional, findings con CWE/CVSS).

## Reglas

- Solo findings CONFIRMADOS. Los dudosos van a `limitations.md` como observaciones.
- Redacta PII y tokens.
- Un bug por finding; agrupa subdominios.
- No pegues output masivo de terminal: referencia los ficheros de evidencia.
