---
description: Triaje de hallazgos - severidad CVSS, duplicados, exclusiones de policy y checklist previo al envio
---

# /bb-triage

Revisa hallazgos antes de enviarlos. Carga `bb-report` y `bb-scope`.

## Uso

```
/bb-triage [F-001,F-002 | --all] [--policy <scope/scope.md>] [--verbose]
```

## Checklist por finding

**Alcance**
- [ ] El asset esta en `scope/scope.md` como in-scope.
- [ ] La clase de vulnerabilidad no esta en la lista de excluidas.
- [ ] El componente es del cliente (no de un SaaS de terceros).

**Evidencia**
- [ ] Reproducido desde limpio >=2 veces.
- [ ] Impacto demostrado, no inferido.
- [ ] Capturas con timestamp y URL visibles.
- [ ] Request/response sin tokens, cookies ni PII sin redactar.

**Severidad**
- [ ] Vector CVSS v3.1 correcto y justificado.
- [ ] `UI:R` si hay interaccion de victima.
- [ ] `C:H` solo si afecta datos de otros usuarios.
- [ ] Severidad contrastada con las guias del programa (no solo CVSS).
- [ ] No se ha inflado por "podria escalar a".

**Duplicados**
- [ ] No es el mismo bug que otro finding (agrupa si lo es).
- [ ] No es duplicado de un reporte previo propio.
- [ ] Un unico bug por reporte.

**Calidad**
- [ ] Titulo = clase + donde + que permite.
- [ ] Pasos completos y no ambiguos.
- [ ] PoC ejecutable tal cual.
- [ ] Fix concreto, no "sanea la entrada".
- [ ] Impacto de negocio redactado en el summary.

## Salida

```
F-001  IDOR /api/v1/orders/{id}
  Scope:        OK (api.target.com, "*.target.com" in policy)
  Policy:       OK (no excluye broken access control)
  Evidence:     OK (2/2 reproducciones, capturas ok)
  Severity:     High (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N) - coherente
  Duplicates:   OK
  Blockers:     NONE
  VERDICT:      READY TO SUBMIT
```

Si hay blockers, se listan con la accion concreta para resolverlos.

## Severidades rapidas (guia)

| Severidad | Criterio |
|---|---|
| Critical | RCE/SSRF->RCE, auth bypass a admin, mass data exposure, takeover de identidad, SQLi con lectura amplia |
| High | BOLA con PII, privilege escalation, secret activo, exposed admin panel, takeover de subdominio |
| Medium | Stored XSS con impacto, CSRF con impacto, info leak con datos sensibles, rate limit ausente |
| Low | TLS debil, headers ausentes sin impacto, user enumeration |
| Informative | Version disclosure, hardening suggestions sin impacto demostrable |
