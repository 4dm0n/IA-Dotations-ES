---
description: Define y valida el alcance del programa (in-scope, out-of-scope, reglas, rate limits) antes de cualquier prueba
---

# /bb-scope

Construye `scope/scope.md` a partir de la politica del programa y valida que un
activo concreto es testeable antes de tocarlo.

Carga la skill `bb-scope`.

## Uso

```
/bb-scope <program-url-or-policy> [--asset <host>] [--verify]
```

## Comportamiento

1. **Extrae la politica**: si se pasa una URL, recupera las secciones de scope,
   out-of-scope, safe harbor, metodologia, rate limits y disclosure.
2. **Construye `scope/scope.md`** con la tabla de activos in-scope / out-of-scope
   y las reglas derivadas.
3. **Escribe `scope/out-of-scope.txt`**: lista plana de activos y patrones
   prohibidos que el agente debe consultar antes de cada peticion.
4. **Con `--asset <host>`**, ejecuta la verificacion de pertenencia:
   - `dig +short` (resolucion)
   - certificado TLS (CN/SAN)
   - `curl -sSI` (server, CDN, WAF)
   - CT logs de organizacion
   - decision: `IN-SCOPE` / `OUT-OF-SCOPE` / `DUDOSO -> escalar`
5. **Con `--verify`**, audita `scope/scope.md` contra la politica y lista
   discrepancias, activos sin clasificar y wildcards ambiguos.

## Formato de salida

```
SCOPE VERDICT: https://api.example.com
  DNS: resolves -> 203.0.113.10
  TLS: CN=api.example.com, SAN matches
  OWNER: organization matches program
  CDN/WAF: none detected
  VERDICT: IN-SCOPE (policy: "*.example.com" + explicit api entry)
  RESTRICTIONS: rate 10 req/min; no DoS; no load testing
```

## Reglas

- Ante la duda, marca `DUDOSO` y escala. Nunca asumas.
- Los subdominios de terceros (cloud, CDN, SaaS) son out-of-scope salvo mencion
  explicita en la policy.
- Un apex no esta incluido por un wildcard `*.dominio` salvo que la policy lo diga.
