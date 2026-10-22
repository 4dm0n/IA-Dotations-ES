---
description: Test de API REST/GraphQL - authn, authz por objeto, mass assignment, rate limit, CORS, inyeccion
---

# /bb-api

Ciclo de pruebas sobre una API. Carga `bb-api` y `bb-opsec`.

## Uso

```
/bb-api <base-url> [--spec <openapi.json|graphql>] [--auth <bearer|header>] [--id <param-name>] [--profile light|standard|deep]
```

## Pasos

1. **Descubrir la superficie**
   - Specs: `swagger.json`, `openapi.json`, `v3/api-docs`, `.well-known/openapi`.
   - GraphQL: introspeccion `__schema`, `graphql-cop`.
   - Rutas: `kiterunner`, `ffuf` con wordlist de rutas.
2. **Construir el inventario** `findings/api_inventory.md` con method, path,
   params, auth, roles, tenant-scoped.
3. **Autenticacion**: token invalido, expirado, de otro usuario, sin rol,
   en query string, en cookie.
4. **Autorizacion por objeto** (BOLA) en cada endpoint con identificador.
5. **Mass assignment** en cada endpoint de escritura.
6. **Rate limiting** en login, reset y endpoints caros.
7. **GraphQL**: introspeccion, batching, profundidad, field-level authz.
8. **CORS** con origin externo.
9. **Inyeccion basica** en todos los parametros de texto.
10. **Webhooks**: firma y payload.

## Opciones

- `--id <param-name>`: nombre del parametro de objeto a mutar (para la matriz BOLA).
- `--auth <token>`: token de sesion (Bearer o header completo).
- `--spec <url>`: forzar la fuente de la spec.
- `--profile light`: solo superficie + inventario + auth basica.

## Salida

```
findings/api_inventory.md
findings/F-00X_<slug>/...
```

## Notas

- Un `200` con cuerpo vacio no es un IDOR: compara contenido.
- Usa dos cuentas propias; nunca datos de terceros.
- No conviertas esto en un test de carga: bursts minimos (5-10).
- SMS/email bombing: nunca. Reporta sin disparar.
