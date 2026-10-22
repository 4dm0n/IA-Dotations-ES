---
description: Retest de un finding tras la correccion del vendor - verifica que el PoC ya no explota
---

# /bb-retest

Verifica que una correccion funciona. Carga `bb-report` y `bb-exploit`.

## Uso

```
/bb-retest <finding-ref|F-001> [--target <url>] [--full]
```

## Flujo

1. **Localiza el PoC**: `findings/<ref>/poc/`.
2. **Baseline**: confirma que el asset sigue existiendo y responde.
3. **Ejecuta el PoC original** sin modificarlo:
   ```bash
   python3 findings/F-001/poc/poc.py "$TARGET"
   ```
4. **Interpreta**:
   - Falla la asercion / returns non-200 -> **corregido**.
   - Sigue explotando -> **reabrir el reporte**, no abrir uno nuevo.
   - Falla por otra razon (500, timeout, cambio de API) -> **inconclusivo**:
     documenta y contacta al triage.
5. **Verifica el fix** (no solo que el PoC falla):
   - Revisa la respuesta y los headers del camino afectado.
   - Comprueba que la funcionalidad sigue viva (no rompieron la app).
6. **Re-test en modo no destructivo**: no vuelvas a explotar con datos reales.
7. **Documenta** en el reporte original:
   ```
   ## Retest - 2026-11-02
   - PoC: findings/F-001/poc/poc.py
   - Resultado: FAIL (asercion 'email' no presente) -> corregido
   - Verificacion adicional: respuesta 403 con body de error de authz
   - Reapertura: no necesaria
   ```

## `--full`

Ademas:
- Revalida el PoC en el subdominio/endpoint equivalente si habia varios.
- Comprueba que el control preventivo existe (WAF rule, validacion server-side).
- Revalida la regla de deteccion: ¿la regla Sigma/Elastic dispara todavia con el
  intento bloqueado? (si el fix es preventive, la regla puede dejar de ser
  necesaria: actualiza la matriz de deteccion).
- Actualiza `report/impact_matrix.md` y `report/detections.md`.

## Notas

- No re-explotes de forma agresiva: si el fix es un WAF, no lo evades para
  "confirmar" que sigue roto.
- Un 403 con mensaje de error generico es un fix valido si el backend ya no
  sirve el dato: verificalo con la peticion directa al origen.
- Documenta siempre la fecha, el comando y el resultado literal.
