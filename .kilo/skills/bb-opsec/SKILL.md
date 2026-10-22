---
name: bb-opsec
description: >-
  Use this skill to protect the hunter's identity, IP reputation, evidence chain and
  artifacts during a bug bounty engagement: egress selection, VPN/TOR/VPS routing,
  rate discipline, WAF and ban handling, data handling and redaction, storage of
  evidence, anti-leak and cleanup rules, and what never to do against a target's
  defensive controls. Load it first and re-read it whenever blocked, banned or
  asked to escalate.
---

# bb-opsec / Disciplina Operacional

En bug bounty la reputation es el activo principal: un baneo permanente en un
programa grande puede valer mas que todas las recompensas que obtengas ese ano.

## 1. Egress (salida de trafico)

Opciones, de mejor a peor para un hunt serio:

| Opcion | Ventajas | Inconvenientes | Uso recomendado |
|---|---|---|---|
| **VPS propia con IP dedicada** | IP estable, sin bloqueo compartido, permits pruebas brutas | Costo, traceable al operador | Hunt activo pesado, bruteforce controlado, escaneo masivo |
| **VPN de pago** | IP rotatoria,anonimato parcial | IP Compartida -> baneos de otros usuarios te afectan | Default para hunt web/API |
| **TOR** | Muy dificil de atribuir, multiples saltos | Latencia alta, muchos sitios bloquean exit nodes, prohibido en muchos programas | Solo pasivo y como ultima opcion; **verificar si el programa lo prohibe** |
| **IP de casa** | Rapida | Se correlaciona con tu identidad, riesgo de baneo permanente | Solo recon pasivo y pruebas no sensibles |

Reglas:
- Nunca uses la IP de casa para fuerza bruta, spraying, DoS o fuzzing agresivo.
- Un solo destino por IP por ventana. Si cambias de IP, espera a que expire la
  anterior (24h+ typical).
- Verifica tu IP real antes de cada campana: `curl -s https://ifconfig.me`.
- Registra que IP se uso contra que activo en `logs/commands.log`. Si el triage
  pregunta, debes poder reconstruirlo.
- Tor exit nodes: la mayoria de programas los excluyen explicitamente. Verifica
  la policy antes de usarlos; ante la duda, no los uses.

## 2. Identidad y gestion de cuentas

- Usa una identidad de hunter separada: alias dedicado, correo dedicado, wallet
  de crypto dedicado (para recompensas), claves SSH separadas.
- Nunca uses tu email real para crear cuentas en los objetivos. Usa una direccion
  de un servicio de aliases condominio propio.
- Multi-factor: passkeys o TOTP con seeds en un gestor separado.
- No aceptes los terminos de un bounty con una cuenta que usas para otra cosa.
- Rate limit de cuentas: los burners se detectan (mismo fingerprint, mismo
  patron). Varia de forma natural: user-agent, zona horaria, idioma, pantalla.

## 3. Fingerprint del cliente HTTP

Los anti-bot (Cloudflare, Akamai, DataDome, PerimeterX) correlacionan el
fingerprint del navegador con el de las peticiones. Si usas un scanner sin
cuidado, el mismo perfil se vuelve identificable.

Mitigaciones legitimas (dentro de scope, no son "evasion maliciosa"):
- Usar el proxy del Burp con un navegador real y una sesion autentica coherente.
- Mantener un perfil de navegador por activo, no uno global.
- Respetar el limite de requests del programa: menos peticiones = menos sospecha.
- No automatizar un login para saltarse un CAPTCHA. Si hay CAPTCHA, el mensaje
  es "no automatices"; usa las credenciales de test del programa.

Prohibido: construir la evasion de WAF como el objetivo del reporte, o
desactivar protecciones del cliente para "demostrar" un finding.

## 4. Gestion de bloqueos y baneos

Cuando te bloquean (403, CAPTCHA, 429, IP ban, cuenta suspendida):

1. **Para.** No cambies de IP para reintentar lo mismo. Eso es consistente con
   la intencion de bloqueo y puede ser tratado como evasion.
2. Captura la evidencia del bloqueo: codigo, headers, timestamp, URL, IP de
   origen.
3. Revisa si el programa tiene una politica de "testing que dispara alertas"
   (muchos la tienen: "te avisaremos si bloqueamos tu IP"). Si la hay, notifica
   por el canal oficial y **espera**.
4. Si no hay politica clara y el bloqueo impide el progreso, escala al contacto
   del programa antes de continuar por otra via.
5. Nunca "escalas" probando en el IP de un tercero, ni via un proxy gratuito,
   ni desde una instancia cloud prestada sin autorización.

Clasificacion:
| Situacion | Accion |
|---|---|
| 429 rate limit | Respeta `Retry-After`, reduce ritmo 50%, espera |
| 403 con challenge (Cloudflare) | Reduce ritmo drasticamente, usa sesion de navegador, si persiste notifica |
| IP ban temporal | Espera el TTL, no cambies de IP para continuar el mismo test |
| Bloqueo permanente | Notifica al programa, documenta, cambia de activo |
| WAF bloquea un ataque especifico | Ajusta la tecnica a la version low-risk del finding, no la-ofuscation |

## 5. Manejo de datos

- Principio de minimo acceso: demuestra con 1 registro, 1 archivo, 1 token.
- Nunca descargues una base de datos completa, un backup, o un volcado de
  usuarios, aunque el finding lo permita.
- Almacena datos reales cifrados, con expiracion: borra en 7-14 dias.
- Al reportar, redacta PII: `user_9182@example.com` -> `u****@example.com`,
  documenta el patron, no el valor.
- Datos prohibidos en el reporte: passwords, tokens completos, cookies de sesion,
  claves privadas, numeros de tarjeta, documentos de identidad, datos de salud.
- Nunca uses datos reales de usuarios como payload de prueba (inyeccion XSS/SQLi).
  Usa un canario propio (`bounty-test-<alias>@<dominio-propio>`).

## 6. Cadena de custodia de la evidencia

- Captura cruda en el momento. Un output de terminal pegado en el chat se pierde.
- Cada artefacto en `findings/F-XXX_<slug>/evidence/` con nombre descriptivo:
  `2026-10-22T101500Z-response-headers.txt`.
- Registra en `logs/artifacts.log`: `ts | finding | archivo | donde vive | accion(creado/eliminado)`.
- Sincroniza el reloj: `timedatectl set-ntp true` / `date -u` antes de empezar.
- Screenshot: terminal completa + reloj visible + URL bar visible.

## 7. Artefactos en el objetivo (lo que dejas en el servidor)

Cada archivo, usuario, bucket, key o webhook que creas es un residuo. Lleva un
registro y eliminalo:

| Artefacto | Limpieza | Verificacion |
|---|---|---|
| Archivo subido | `DELETE` con la misma credencial | Re-`HEAD` -> 404 |
| Cuenta creada | Cerrar/borrar la cuenta | Login falla |
| Token/API key | Revocar | API devuelve 401 |
| Bucket/tag/queue | Borrar objeto + bucket | Listado vacio |
| Webhook callback | Eliminar | Re-`GET` -> 404 |
| Regla de firewall/ACL | Revertir | Comparar con baseline |
| DNS record | Borrar | `dig` no resuelve |
| Config modificada | Restaurar desde backup | diff limpio |
| Email enviado | No se puede borrar: no lo hagas, o usa un buzon de pruebas |

Testigo de limpieza: cuando termines, ejecuta una verificacion de que el activo
esta en su estado original. Incluyelo en `notes/cleanup.md`.

## 8. Anti-fuga y disclosure

- No publiques nada hasta que la ventana de disclosure del programa lo permita.
- Nada en redes sociales, Pastebin, GitHub, gist, Discord, Telegram, blogs, ni
  en el reporte de otro programa.
- No compartas credenciales, dumps ni PoC payloads en canales publicos.
- Si te piden 공개 forzado o chantaje: detente, no negocies, escala al
  plataforma/programa.
- Al escribir el reporte, lee el NTExto dos veces buscando: tokens, cookies,
  claves, emails reales, IDs internos, PII, IPs internas, nombres de empleados.

## 9. Anti-forense de tu propia maquina

- Usa un perfil de navegador dedicado para bounty (no tu perfil personal).
- Limpia datos de sesion guardados de los objetivos tras cada sesion.
- No dejes plugins de pentest con sesion persistida en un navegador compartido.
- En WSL, no montes el home de Windows para los artefactos sensibles.
- No instales herramientas de Exploit-DB sin leer el codigo: instalan payloads.
- Desinstala al final lo instalado para el hunt (`bb-cleanup`).

## 10. Checklist de arranque

```
[ ] IP de salida verificada y registrada
[ ] Policy leida, scope escrito, out-of-scope listado
[ ] Rate limits definidos por actividad
[ ] Preflight de herramientas (bb-toolkit)
[ ] Arbol de directorios creado
[ ] Reloj sincronizado
[ ] Testigo de limpio (baseline) de los activos que se van a modificar
[ ] Canal de escalacion guardado (email/telegram del programa)
[ ] Cuentas de prueba identificadas
[ ] Identidad de hunter separada, no tu identidad real
```

## 11. Checklist de cierre

```
[ ] Todos los artefactos del objetivo removidos y verificados
[ ] Datos realesminimumizados o eliminados localmente
[ ] IPs usadas registradas
[ ] Archivos con PII cifrados/eliminados
[ ] Nada publicado antes de la ventana
[ ] Reporte releido para redaccion
[ ] Herramientas temporales desinstaladas
[ ] notes/cleanup.md completo
```
