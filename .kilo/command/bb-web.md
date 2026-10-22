---
description: Test de aplicacion web - superficie, inyeccion, IDOR, auth, business logic, ficheros
---

# /bb-web

Ciclo completo de pruebas sobre una aplicacion web. Carga `bb-webapp` y
`bb-opsec`.

## Uso

```
/bb-web <target-url> [--profile light|standard|deep] [--auth <cookie-or-token>] [--check <class>] [--id <identificador>]
```

## Perfiles

| Perfil | Clases cubiertas |
|---|---|
| `light` | headers, TLS, exposed files, robots/sitemap, tech fingerprint, secrets en JS |
| `standard` | light + SQLi + XSS + SSTI + SSRF + LFI + CORS + cookie flags + open redirect |
| `deep` | standard + IDOR/BOLA + mass assignment + JWT + business logic + race conditions + upload + GraphQL |

## `--check <class>` (una o varias, separadas por coma)

`sqli`, `xss`, `ssti`, `ssrf`, `xxe`, `cmdi`, `lfi`, `idor`, `massassign`,
`jwt`, `cors`, `openredirect`, `upload`, `race`, `graphql`, `headers`, `secrets`,
`logic`, `ssrf`, `deserial`.

## Flujo por clase

```
1. Descubrir el objetivo del parametro (arjun/katana/ffuf sobre endpoints)
2. Probar con la herramienta mas leve (curl manual primero)
3. Confirmar con 2 tecnicas independientes cuando la clase lo permita
4. Documentar evidencia cruda
5. Anotar impacto real, no teorico
6. Solo si hay impacto: crear F-XXX con PoC
```

## Reglas de seguridad operativa

- Empieza por un objetivo de bajo impacto y escala.
- Nunca `--dump`/`--os-shell`/`--file-read` masivo en sqlmap sin autorizacion.
- Nunca apuntes SSRF a IPs internas ni a metadata ajena.
- Autenticacion: usa cuenta propia o cuenta de test del programa.
- Redacta toda evidencia con PII.
- Para IDOR necesitas dos identidades: pide las credenciales de test si no las hay.
- No lances `nuclei -t vulnerabilities/` contra todo internet: limita a `-l` con tus hosts.

## Salida

```
findings/F-00X_<slug>/
  notes.md  poc/  evidence/
```
