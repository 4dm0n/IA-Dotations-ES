---
description: Construye y valida un PoC minimo y reproducible para un finding, con test de fiabilidad
---

# /bb-poc

Convierte un candidato en finding confirmado con PoC reproducible. Carga
`bb-exploit`.

## Uso

```
/bb-poc <finding-ref|F-00X> --target <url> [--auth <token>] [--type http|cli|api|idb|mobile]
```

## Flujo

1. **Revisa el candidato**: asset, parametro, hipotesis, impacto esperado.
2. **Construye el PoC minimo**: el mas pequeno que demuestra el impacto.
   Read-only > escribir > ejecutar.
3. **Baseline**: captura el comportamiento normal (before).
4. **Prueba**: captura el comportamiento anomalo (after). Guarda ambos.
5. **Fiabilidad**: 5 ejecuciones, mide exito y tiempo.
6. **Limpieza**: revierte cualquier cambio.
7. **Documenta**: `poc/README.md` con precondiciones, comando y output esperado.

## Plantilla de PoC (autocontenida)

```python
#!/usr/bin/env python3
"""PoC: <descripcion>. Uso: python3 poc.py <target>"""
import sys, requests

def main():
    target = sys.argv[1]
    s = requests.Session()
    s.headers["User-Agent"] = "bounty-research/1.0"
    r = s.get(f"{target}/api/v1/resource/1002", timeout=15)
    assert r.status_code == 200, f"got {r.status_code}"
    assert "email" in r.json(), "no cross-account data"
    print("[VULNERABLE] cross-account read confirmed")

if __name__ == "__main__":
    main()
```

## Test de fiabilidad

```bash
for i in $(seq 1 5); do
  s=$(date +%s%N); python3 poc.py "$TARGET" >/dev/null 2>&1 && r=OK || r=FAIL
  e=$(date +%s%N); echo "run $i: $r ($(( (e-s)/1000000 ))ms)"
done
```

## Clasificacion

- `reliable` (>=90% en 5+ intentos)
- `intermittent`
- `racy` (ventana temporal)
- `environment-dependent` (precondicion exacta)

## Salida

```
findings/F-00X_<slug>/
  notes.md
  poc/poc.py
  poc/README.md
  evidence/before.txt
  evidence/after.txt
  evidence/screenshot.png
  impact.md
  reliability.md
```

## Reglas

- Nada destructivo. Nada de DoS. Nada de reverse shell al cliente: usa OOB propio.
- Exfiltracion: 1 registro, redactado.
- Si necesitas un payload, que sea inerte (`echo MARKER`, `;id`).
- Si la prueba requiere deshabilitar WAF/MFA del cliente, eso es out-of-scope.
