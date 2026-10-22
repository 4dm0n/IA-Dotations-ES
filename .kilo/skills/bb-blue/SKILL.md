---
name: bb-blue
description: >-
  Use this skill for the blue-team side of a security engagement: detection
  engineering (Sigma, Elastic, Suricata, Splunk), logging and audit hardening,
  hardening of the vulnerable technology, incident response playbooks, purple-team
  validation loops, ATT&CK coverage gap analysis, secure baselines, and the
  defensive remediation of every offensive finding. Load it when the engagement
  requires defensive outputs, not just vulnerability discovery.
---

# bb-blue / Equipo Azul (Defensive Side)

Convierte cada hallazgo ofensivo en capacidad de deteccion, prevention y
respuesta. Un finding sin control defensivo asociado es un finding a medias.

## 1. Modelo de deteccion

Para cada activo, define que se deberia ver y donde:

| Activo | Telemetria disponible | Retencion | Mascarada | Origen |
|---|---|---|---|---|
| web prod | access log, WAF, app log | 90d | IP cliente | nginx/app |
| API | access log, app log, traces | 90d | - | app |
| cloud | CloudTrail/Cloud Audit | 1y | - | provider |
| AD | Security log 4624/4625/4688 | 180d | - | DCs |
| Linux | auth.log, auditd | 90d | - | hosts |
| CI | pipeline logs, secret scan | 1y | - | CI |
| mobile | server-side + crash logs | 30d | - | backend |

Hallazgo estructural frecuente: el activo no tiene ninguno de esos logs.

## 2. Ciclo purple team

```
Ofensivo: PoC F-00X  ->  TTP con MITRE  ->  Deteccion esperada
                                            |
Azul: se implementa la regla  ->  Se ejecuta el PoC en condiciones controladas
                                            |
                            ->  ¿La regla dispara?  SI -> cerrar finding con deteccion
                                               NO -> iterar la regla
```

Documenta por cada PoC: "detectado en <fuente> en <segundos> por <regla>".

## 3. Sigma (reglas de deteccion portable)

Formato estandar, portable a SIEM. Ubicacion: `rules/*.yml`.

```yaml
title: Suspicious SQL Error Keywords in Web Request Parameters
id: 8f2a1b47-0d4e-4c9a-9b31-2f5c1d7e8a10
status: experimental
description: >
  Detecta respuestas de aplicacion que contienen mensajes de error de base de
  datos, indicador clasico de SQL injection en curso.
references:
  - https://attack.mitre.org/techniques/T1190/
  - https://cwe.mitre.org/data/definitions/89.html
author: bounty-hunt
date: 2026-10-22
tags:
  - attack.technique.t1190
  - attack.t1190.001
logsource:
  category: webserver
  product: nginx
detection:
  selection:
    status: | select(status) from [logs-nginx-access] | where status >= 500
    body|contains:
      - "SQL syntax"
      - "ORA-01756"
      - "mysql_fetch_array"
      - "PostgreSQL query failed"
      - "Unclosed quotation mark"
  condition: selection
falsepositives:
  - Aplicaciones que exponen errores de DB de forma intencional en modo debug
fields:
  - uri
  - status
  - user_agent
level: high
```

```bash
# Validar y convertir
pipx install sigma-cli
sigma check rules/
sigma convert rules/ -t splunk -p sysmon -o out/
sigma convert rules/ -t elastic -o out/
sigma convert rules/ -t splunk -p sysmon -o out/ -s
```

## 4. Elastic / ECS (queries de hunting)

```bash
# KQL style para Elastic (Kibana KQL)
# Volumen anormal de 4xx desde una IP (fuzzing/enumeracion)
http.response.status_code >= 400 and http.response.status_code < 500
| stats count by source.ip
| where count > 100

# Enumeracion de endpoints (muchos 404 en paths distintos)
http.response.status_code == 404
| stats dc = count_distinct(url.original) by source.ip
| where dc > 50

# Union de credenciales fallida (password spraying)
event.category:"authentication" and event.outcome:failure
| stats count by user.name
| where count > 5

# Cambios de permisos IAM
event.dataset:"aws.cloudtrail" and event.action:(CreateUser or AttachUserPolicy or PutUserPolicy)
```

## 5. Suricata (red)

```bash
# Regla de ejemplo: escaneo de puertos (SYN a muchos puertos)
alert tcp $HOME_NET any -> $EXTERNAL_NET any (
  msg:"POSSIBLE PORT SCAN - many SYNs to single host";
  flags:S; threshold:type both, track by_src, count 20, seconds 60;
  sid:1000001; rev:1;)
```

```bash
suricata-update && suricata -T -c /etc/suricata/suricata.yaml   # test
suricata -r flows.pcap -l /var/log/suricata                       # replay
# Zeek para hunting de red
zeek -r flows.pcap
# Reglas Zeek para exfiltracion DNS / tunneling
```

## 6. Hardening por tecnologia

### Web / API
- Cabeceras: `Content-Security-Policy` (sin `unsafe-inline`), `Strict-Transport-Security`
  (includeSubDomains, max-age >= 1y), `X-Content-Type-Options: nosniff`,
  `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` o `frame-ancestors`.
- CORS: allowlist explicita de origins, nunca reflexion con `*` + credenciales.
- Cookies: `HttpOnly`, `Secure`, `SameSite=Lax|Strict`, path minimo.
- Rate limiting por IP y por cuenta en auth, reset, y endpoints caros.
- CSP report-only primero, luego enforce.
- WAF en modo bloqueo con reglas por clase de vulnerabilidad, no solo deteccion.

### API
- Autorizacion server-side por objeto en cada endpoint con referencia.
- Scoping por tenant aplicado en la query, no en el filtro de la app.
- Validacion de esquema en el borde (allowlist de campos: mass assignment).
- Versionado y deprecacion de endpoints antiguos (`/api/v1` tras `v2`).
- OpenAPI publicado como contrato, no como documentacion del interior.

### Identidad
- MFA en cuentas de administracion y de soporte.
- Password spraying: lockout progresivo, no permanente, y deteccion de spray.
- Sesiones: invalidacion al cambiar password o rol; rotacion de session id post-login.
- Privilegio minimo y revisiones periodicas de permisos.

### Cloud
- S3 Block Public Access a nivel de cuenta.
- IMDSv2 obligatorio (`HttpTokens=required`, hop limit 1).
- IAM: sin `Action: *` ni `Resource: *`; condiciones de contexto.
- Secrets en Secrets Manager/Key Vault/Vault, rotacion automatica.
- CloudTrail centralizado e inmutable, alerts sobre cambios de IAM y de politicas.

### Contenedores / K8s
- `runAsNonRoot`, `readOnlyRootFilesystem`, `drop: [ALL]`, `allowPrivilegeEscalation: false`.
- Sin `privileged`, sin `hostPID`, sin `hostNetwork`.
- NetworkPolicy por default (deny) y egress allowlist.
- Imagenes pinneadas por digest, escaneadas en CI (Trivy/Grype), firma (cosign).

### AD / Windows
- Protected Users, SMB signing, LDAP signing/channel binding, deshabilitar NTLM.
- LAPS para passwords locales de admin.
- BitLocker, Defender for Endpoint, WDAC/AppLocker.
- Audit de Object Access y de uso de privilegios elevados.
- Tiering de admin y PAW (Privileged Access Workstations).

### Linux
- `auditd` con reglas de ejecucion de comandos elevados, cambios de sudoers, cambios de cron, accesos a /etc/shadow.
- `aide` o `tripwire` para integridad de ficheros.
- No root login por SSH, `PermitRootLogin no`, autenticacion por clave, `MaxAuthTries 3`.
- `fail2ban` o WAF rate limiting con alert.
- SELinux/AppArmor en modo enforcing.

## 7. Logging: que registrar y como

Registra SIEMPRE: cambios de autenticacion y de privilegios, cambios de
configuracion, acceso a datos sensibles, exports, llamadas a la API de
administracion, uso de credenciales de servicio, cambios de rol y de politica,
accesos a bucket/secretos, ejecucion de codigo en runtime.

NUNCA registres en texto plano: passwords, tokens de sesion, cookies completas,
datos de tarjeta, PII innecesaria, claves privadas.

Formato: timestamp UTC con zona explicita, actor, accion, recurso, resultado,
source IP, correlación (request id), y el `user_agent` cuando sea relevante.

```bash
# Verificar que un log tiene los campos minimos
jq 'keys' access_log_sample.json
# Comprobar que no hay secretos filtrados en los logs
grep -iE '(password|token|secret|api[_-]?key)=' logs/*.log | head
```

## 8. Respuesta a incidentes (playbook por finding)

```markdown
## Playbook: <Finding F-00X>

### Deteccion
- Fuente: <SIEM / WAF / EDR>
- Regla: <sigma id / query>
- Nivel de confianza: <Alto/Medio>
- Falsos positivos conocidos: <lista>

### Confirmacion
1. <query de hunting>
2. <que se ve si es TP>

### Contencion
1. <accion inmediata reversible>
2. <rotacion de credenciales>

### Erradicacion
1. <fix>
2. <deploy>

### Recuperacion
1. <verificacion>
2. <retest con el PoC original -> debe fallar>

### Lecciones
- <gap de deteccion que permitio la explotacion>
```

## 9. Metricas de postura (para el cierre)

| Metrica | Antes | Despues | Fuente |
|---|---|---|---|
| % endpoints con authz por objeto | 40% | 95% | inventario API |
| % secretos rotados tras exposicion | 0 | 100% | secret manager |
| Retencion de logs (dias) | 7 | 180 | config |
| Reglas de deteccion deployadas | 3 | 25 | sigma repo |
| MTTD de un finding critico | - | - | incidente previo |
| % assets con WAF en modo block | 0 | 100 | WAF console |
| Cuentas con MFA | 60% | 100% | IdP |
| % buckets con public access block | 0 | 100 | AWS config |

## 10. Coverage defensiva (checklist)

- [ ] Telemetria disponible por activo (y su retencion)
- [ ] Regla de deteccion por finding (Sigma o query)
- [ ] Validacion purple team (la regla dispara con el PoC)
- [ ] Hardening preventivo por tecnologia
- [ ] Playbook de respuesta por finding critico/high
- [ ] Rotacion de credenciales expuestas
- [ ] Gap analysis ATT&CK por activo
- [ ] Metricas de antes/despues
- [ ] Plan de remediacion con responsables y fechas
