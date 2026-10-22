---
name: bb-red
description: >-
  Use this skill for the red-team side of a security engagement: adversary modeling
  and personas, MITRE ATT&CK mapping, threat emulation plans, detection-gap
  analysis, attack path chaining across findings, controlled adversary simulation
  (initial access, execution, persistence, lateral movement, exfiltration
  simulation), and purple-team handoff to blue. Load it when the engagement requires
  an adversarial, attacker-perspective view rather than a single vulnerability.
---

# bb-red / Equipo Rojo (Adversary Side)

El lado rojo no es "romper mas cosas": es razonar como el atacante, encadenar
vulnerabilidades sueltas en un camino de ataque creible, y saber que detendria cada
control. Todo dentro de la autorizacion escrita.

## 1. Modelo de adversario

Define un perfil de amenaza antes de actuar:

```markdown
## Adversary profile
- Objetivo: <dato / acceso / control / dinero>
- Perfil: <oportunista / termo / grey-hat / APT / insider>
- Habilidades: <sin herramientas / herramientas BA / 0-day / fisico>
- Recursos: <1 host / red interna / cloud creds>
- Motivacion: <oportunista / industrial / espionaje / hacktivismo>
- Atributos ATT&CK: <T1059, T1190, T1078...>
```

Esto determina que capas de ataque tienen sentido y evita sobre-testing.

## 2. Encadenamiento de findings (attack path)

El valor real de un bounty no son N findings sueltos, es la **cadena**. Mapea
tus hallazgos a un camino:

```markdown
## Attack path
1. Recon pasivo (OSINT, sin intrusjon) -> activo: usuario objetivo @empresa.com
2. Credencial filtrada en repo publico (bb-cloud) -> login a panel interno (bb-webapp)
3. IDOR en /api/v1/users/{id} (bb-api) -> enumeracion de tenants
4. Secret en .env expuesto (bb-webapp) -> acceso a bucket S3 (bb-cloud)
5. Conclusiones: un atacante no autenticado obtiene datos de N tenants

## Alternativas bloqueadas
- Si el panel exige MFA -> la cadena se corta en el paso 2
- Si el bucket tiene Block Public Access -> se corta en el paso 4
```

Para cada eslabon indica: **como lo bloquea un control blue** y si el control
esta realmente desplegado.

## 3. MITRE ATT&CK

Mapea por activo (no global):

| Tactica | Tecnica | Activo | Evidencia | Deteccion blue | Gap |
|---|---|---|---|---|---|
| Initial Access | T1190 Exploit Public-Facing App | web prod | PoC F-002 | WAF rule | sin regla especifica |
| Execution | T1059.004 Unix Shell | app | PoC F-003 | EDR | no monitorizado |
| Persistence | T1098 Account Manipulation | IAM | F-004 | CloudTrail | sin alerta |
| Credential Access | T1552.005 Cloud Instance Metadata | EC2 | F-005 | IMDSv2 | v1 habilitado |
| Discovery | T1087 Account Discovery | AD | F-006 | audit policy | ausente |
| Lateral Movement | T1021.004 SSH | red | F-007 | SIEM | sin correlacion |
| Exfiltration | T1567 Exfiltration Over Web Service | S3 | F-008 | proxy logs | sin DLP |

Herramientas:
```bash
# Generar matriz desde la base de datos MITRE
pipx install mitreattack-python
python3 -c "
from mitreattack.stix20 import MitreAttackData
m = MitreAttackData('enterprise-attack.json')
print([t.name for t in m.get_techniques()][:20])
"
# Consultar tecnicas en linea
# https://attack.mitre.org/techniques/T1190/
```

## 4. Deteccion de gaps (el entregable principal del lado rojo)

Antes de "atacar", responde: **¿como me detectarian?**

| Vector | Deteccion esperada | Gap |
|---|---|---|
| Enumeracion de subdominios | DNS logs, CT monitoring | nadie mira los logs de DNS |
| Port scan | IDS/IPS, flow logs | solo north-south, no east-west |
| Fuzzing web | WAF, honeypot, anomalias 4xx | WAF en modo block pero sin alerta |
| Explotacion de app | EDR, app logs, error tracking | errores 500 no correlacionados |
| Escalada de privilegios | audit de IAM, SUID, sudo | logs de sudo no centralizados |
| Movimiento lateral | SMB/RDP/WinRM logs | 90 dias sin revisar |
| Exfiltracion | proxy, DLP, egress | trafico a almacenamiento publico sin alerta |

Un gap de deteccion con evidencia de que el camino funciona es un finding de
seguridad **valioso y publicable** (muchos programas tienen "security misconfig"
o "detection gap" como categoria valida).

## 5. Simulacion controlada

Solo con autorizacion escrita que describa que se puede ejecutar. En bug bounty
puro, la simulacion destructiva NO es parte del flujo: si el encargo es
"hunter", entrega analisis y deteccion, no ejecucion.

Si el encargo SI es simulacion adversary (equipo rojo conRules of Engagement):

| Fase | Accion | Precondicion | Limite |
|---|---|---|---|
| Recon | DNS, OSINT, enumeracion | Incluido | Pasivo + activo de bajo ruido |
| Initial Access | Phishing simulado | Email de test de tu org | Solo tus propias plantillas, sin adjunto ejecutable real sin aprobacion |
| Execution | Ejecucion de comando controlado | Approved | `whoami`/`echo MARKER`, no interactivo, cleanscript |
| Persistence | Crear tarea/regla de prueba | Approved | Marca visible `BUNTY-TEST`, fecha de expiracion, limpieza verificada |
| Credential Access | Volcar credenciales en memoria | Approved explicitamente | Nunca a disco, nunca exfiltrado, solo presencia |
| Lateral Movement | Mover a 1 host adicional | Approved | Max 2-3 saltos, hosts acordados |
| Exfiltration | Transferencia simulada | Approved | Datos sinteticos, volumen minimo, a tu OOB, documentado |

Reglas invariables:
- Nada de ransomware, wipers, rootkits, bootkits, implants covertos, miners.
- Nada de credential dumping masivo a disco.
- Nada de DoS.
- Nada de exfiltracion de datos reales mas alla de la demostracion minima.
- Todo artefacto lleva etiqueta identificable y fecha de limpieza.
- Limpieza verificada antes de cerrar.

## 6. Evasion: donde esta la linea

| Practica | Evaluacion |
|---|---|
| Usar un user-agent realista | Permitido y recomendado |
| Bypass de WAF para completar un PoC | Solo si el programa lo permite; si no, usa una version low-risk del PoC |
| Evadir el honeypot del cliente | NO. Si el cliente te atrapa, para y reporta |
| Cambiar de IP tras un ban | NO (ver `bb-opsec`) |
| Ofuscar el payload para evitar firmas | **NO** en bug bounty. El finding es la vuln, no el EDR bypass. Reporta la vuln |
| Abusar del rate limit | NO |
| Enganar a un empleado para obtener info | NO, salvo programa de ingenieria social explicito |

El bypass de deteccion **si** es un finding valido cuando lo que se evalua es la
capacidad de deteccion (equipo rojo / purple team), no cuando el objetivo es
"entrar en produccion de un tercero para cobrar un bounty".

## 7. Guion de simulacion

```markdown
# Simulated attack - <objetivo> - <fecha>

## Rules of engagement
- Allowed: [lista]
- Forbidden: [lista]
- Window: [hora inicio - hora fin] UTC
- Emergency contact: [nombre, telefono]
- Kill switch: [palabra/canal para detener]

## Timeline
| Time (UTC) | Action | Result | Detection raised? | Observer |

## Findings
| ID | Tactic | Technique | Description | Detection | Gap |

## Cleanup
| Artifact | Where | Removed | Verified |
```

## 8. Reglas de seguridad operacional de la simulacion

- Nunca simules exfiltracion de datos reales de clientes o empleados.
- Usa un canario sintetico (`BUNTY-CANARY-<uuid>`) en todas las acciones.
- Manten una lista de artefactos en tiempo real (no al final).
- Define un "kill switch": cualquier persona del equipo puede parar la simulacion.
- Coordina con el equipo azul: en simulacion, el azul debe saber que va a pasar
  (salvo evaluacion ciega de deteccion, que se documenta por separado).
- Nunca ataques tu propia organizacion sin el consentimiento formal por escrito del
  responsable de seguridad, con alcance de IPs y horarios.

## 9. Artefactos de la simulacion que SI son findings de bounty

- Panel de administracion exposed sin autenticacion (SSO bypass, `/.env`, `/debug`).
- S3 publico que permite escribir (supply chain de deployment).
- Prefijo de subdominiodangling apuntando a un servicio liberado (takeover).
- Credencial de servicio en un bundle JS.
- Token de API de un tercero en un repo publico con permisos amplios.
- Regla de firewall que expone un puerto de administracion.
- Vault/secret manager con lectura anonima o desde un rol sobrante.

## 10. Evaluacion deBlue (handoff)

Al terminar, entrega a `bb-blue`:
- Tabla de findings con mapeo ATT&CK.
- Deteccion esperada por finding.
- Gap identificado.
- Fuente de log donde deberia verse.
- Regla sugerida (Sigma/Elastic/Suricata) y query de hunting.
- Accion preventiva recomendada.
