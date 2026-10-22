---
name: bb-api
description: >-
  Use this skill to test REST, GraphQL, gRPC and SOAP APIs within an authorized bug
  bounty scope: endpoint and schema discovery, authentication and token handling,
  authorization (BOLA, function-level, tenant isolation), rate limiting, mass
  assignment, GraphQL-specific abuse, injection, webhook and callback handling, and
  API inventory and documentation gaps. Load it when the target is an API.
---

# bb-api / Seguridad de APIs

Las APIs concentran los findings mas valiosos de bug bounty (BOLA, mass
assignment, tokens) y los mas easy de pasar por alto (rate limits, GraphQL).

## 1. Descubrimiento de la superficie

```bash
# Specslodging
for p in swagger.json swagger.yaml swagger/v1/swagger.json openapi.json openapi.yaml \
  v2/api-docs v3/api-docs api-docs api/docs api/swagger api/v1/docs \
  .well-known/openapi.json api-docs.json swagger-resources; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/$p")
  [ "$code" = "200" ] && echo "$p -> $code"
done

# GraphQL
curl -s -X POST "https://$HOST/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{types{name}}}"}' | jq -r '.data.__schema.types[].name' 2>/dev/null
curl -s -X POST "https://$HOST/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{queryType{fields{name args{name type{name}}}}}}"}' | jq

# Endpoint probing sobre rutas comunes
kiterunner scan "https://$HOST" -w routes.txt -x 20 -p 20 -o kr.txt
ffuf -w routes.txt -u "https://$HOST/FUZZ" -mc all -fc 404 -t 20 -rate 40 -of json
```

Herramientas utiles: `kiterunner`, `graphql-cop` (Go), `curlconverter`, `jwt_tool`,
`wscat` (WebSocket), `grpcurl` (gRPC), `postman`/`insomnia` (colecciones).

```bash
# gRPC: reflexion
grpcurl -plaintext $HOST:443 list
grpcurl -plaintext -d '{"id":1}' $HOST:443 package.Service/Method
```

## 2. Inventario de endpoints

Construye `findings/api_inventory.md`:

| # | Method | Path | Params | Auth required | Roles | Tenant-scoped | Notes |
|---|---|---|---|---|---|---|---|

Este inventario es el que te dice que probar y que reportar. Sin el, no puedes
afirmar cobertura.

## 3. Autenticacion

| Mecanismo | Que revisar |
|---|---|
| API Key | En header, query o URL (leak en logs/referer). Rotacion, scoping, comparacion constant-time, key por tenant |
| Bearer/JWT | `alg`, `exp`, `nbf`, `iat`, `aud`, `iss`, `jti`, `kid`, revocacion, lado cliente vs servidor |
| OAuth2 | `redirect_uri` exacto (no prefijo), `state`, PKCE (`code_challenge`), Implicit flow, refresh token rotation, `scope`minimo |
| Session/cookie | SameSite, rotacion post-login, invalidacion al logout, expiracion |
| mTLS / API keypair | No reutilizable, expiracion |

```bash
# Auditar un JWT
echo "$JWT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
python3 jwt_tool.py -t "$JWT" -C -d jwt_common.txt
```

Checks rapidos con dos tokens distintos:
- ¿El token de A sirve en B? (no)
- ¿Un token expirado sigue funcionando? (no)
- ¿Cambiar `aud`/`iss` sigue funcionando? (no)
- ¿El token en el query string funciona? (deberia fallar / el programa lo marquara)

## 4. Autorizacion (BOLA / BFLA / tenant isolation)

Ejecuta la matriz completa. Usa dos cuentas propias o de test.

```bash
# 1. Inventario de rutas con parametro de objeto
grep -oE '/[a-zA-Z0-9_\-]+/\{?[a-zA-Z0-9_]+\}?' api_inventory.md | sort -u

# 2. Baseline con la cuenta A
curl -s "https://$HOST/api/v1/orders/$ID_A" -H "Authorization: Bearer $TOKEN_A" | jq . > resp_A.json

# 3. Cambio de ID con la MISMA sesion
for id in 1002 1003 1004; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/api/v1/orders/$id" -H "Authorization: Bearer $TOKEN_A")
  echo "orders/$id -> $code"
done

# 4. Contexto: el body debe diferir de A (nombre, email, total...)
```

Prueba tambien:
- **Vertical**: usuario normal -> endpoint de admin. `GET /api/admin/users`.
- **Horizontal**: usuario A -> recurso de B.
- **Multi-tenant**: cuenta de tenant X sobre recurso de tenant Y (`X-Tenant-Id`, `?tenant=`, subdominio).
- **BFLA**: rol de lectura que ejecuta escritura (metodo o ruta distinta).
- **Objeto no numerico**: UUID, hash, base64, slug -> prueba UUID fixation y predictable IDs.
- **Referencia indirecta**: `/api/v1/invoices/download?ref=order-123` -> cambia `ref`.

Verificacion de impacto: compara un campo identificativo (nombre, email, total). Un
`200` con `{}` no es un IDOR: no lo reportes.

## 5. Rate limiting y ausencia de control de volumen

```bash
# Burst controlado (minimo: 5-10 peticiones)
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code} " -X POST "https://$HOST/api/login" \
    -H 'Content-Type: application/json' -d '{"user":"test@example.com","pass":"wrong"}'
done; echo
```

Medir:
- Password spray (1 intento por cuenta, nunca N intentos por cuenta).
- Enumeracion de usuarios (diferencia de respuesta/tiempo entre usuario valido e invalido).
- Enumeracion de objetos (muchos 404 vs 403).
- Abuso de endpoints caros (export, PDF, resize, LLM, batch) para agotar recursos. **Esto es DoS si no hay rate limit: no lo provoques en produccion.** Reportalo como "ausencia de rate limit" con evidencia teorica o en un entorno de prueba.
- SMS/email bombing: **nunca** (afecta terceros). Reporta el problema sin dispararlo.

## 6. Mass assignment

```bash
# Intenta anadir campos no esperados al actualizar tu propio recurso
curl -s -X PUT "https://$HOST/api/v1/users/me" -H "Authorization: Bearer $TOKEN_A" \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","role":"admin","isAdmin":true,"balance":999999,"verified":true}' | jq .
# Verifica despues si el rol cambio
curl -s "https://$HOST/api/v1/users/me" -H "Authorization: Bearer $TOKEN_A" | jq .
```

Variantes: `__proto__`, `constructor`, campos con typosquatting del backend
(`is_admin`, `userType`, `accountType`), arrays donde se espera string.

## 7. GraphQL

```bash
# Introspection
curl -s -X POST "https://$HOST/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{types{name fields{name}}}}"}' | jq .

# graphql-cop
graphql-cop -u https://$HOST/graphql --schema -v

# Batch / alias abuse (DoS de batching)
curl -s -X POST "https://$HOST/graphql" -H 'Content-Type: application/json' \
  -d '[{"query":"{__typename}"},{"query":"{__typename}"}]'

# Profundidad y complejidad (query anidada)
# Alias explosion
{"query":"{a:user(id:1){id} b:user(id:2){id} c:user(id:3){id}}"}
```

Checks especificos:
- Introspection expuesta (informativo, o critico si expone datos internos de schema).
- Field-level authorization: un query que pide campos de otro usuario.
- Mutations sin authz.
- `__typename` / `__schema` bypass de filtros.

## 8. Inyeccion en API

- SQLi en parametros de path/query/body: `sqlmap -u "https://$HOST/api/search?q=1" --data '{"q":"1"}' --method=POST --level=1 --risk=1`.
- NoSQL injection: body JSON `{"user":{"$ne":""}}` o `{"password":{"$gt":""}}` -> buscar bypass de login en endpoints de auth.
- LDAP injection en filtros de busqueda.
- Command injection en campos que llegan a un sistema externo.
- SSTI si el input llega a plantilla.
- SSRF en webhooks, importadores, avatares, "preview URL", "fetch metadata".

## 9. Webhooks, callbacks e integraciones

- Registra un webhook a tu endpoint y valida: firma verificada? payload con secretos
  de terceros? headers con tokens?
- Firma HMAC: prueba un payload modificado sin re-firmar -> si se acepta, es
  "webhook signature bypass".
- URL de callback -> SSRF si el servidor la visita.
- Idempotencia: reprocesar el mismo webhook.

## 10. CORS misconfiguration

```bash
curl -s -I "https://$HOST/api/v1/me" \
  -H "Origin: https://evil.example" | grep -i 'access-control'
# Si responde con Access-Control-Allow-Origin: https://evil.example
# y Access-Control-Allow-Credentials: true -> impacto real
```
Verifica ademas si refleja cualquier origin con credenciales. Un `*` sin
credentials es de bajo impacto.

## 11. Documentacion y metadatos

- Documentacion publica que describe endpoints internos o credenciales de ejemplo
  que funcionan.
- `/.well-known/security.txt`: reporta si falta o tiene info de contacto invalida
  (bajo impacto, a veces aceptado).
- OpenAPI con ejemplos que incluyen tokens reales.

## 12. Coverage minima para decir "cubierto"

- [ ] Todos los endpoints de la spec probados al menos una vez
- [ ] Auth: token invalido, expirado, de otro usuario, sin rol
- [ ] Authz por objeto en todos los endpoints con ID
- [ ] Mass assignment en todos los endpoints de escritura
- [ ] Rate limit verificado en login, reset password, y endpoints caros
- [ ] GraphQL: introspeccion, batching, profundidad
- [ ] CORS
- [ ] Inyeccion basica en todos los parametros de texto
- [ ] Webhooks
- [ ] Logs: no se imprimen tokens en respuesta ni en error

## 13. Plantilla de finding API

```
Titulo: BOLA en <METHOD> <path> permite a <rol> leer recursos de <otros tenants/usuarios>
CWE: CWE-639 / CWE-863 / CWE-284
CVSS: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N  (justificar)
Precondiciones: cuenta de usuario registro gratuito / rol X
Evidencia: request/response redacted de 1 objeto ajeno
Impacto negocio: <por que el programa deberia pagarlo>
Remediacion: authz server-side por objeto, scoping por tenant en query
```
