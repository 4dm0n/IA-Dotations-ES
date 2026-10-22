---
description: Detecta la distribucion (Kali/BlackArch/Garuda/Parrot/Debian/Arch/WSL) y prepara o instala el toolchain de seguridad
---

# /bb-setup

Prepara el entorno de trabajo: detecta la distro, resuelve las herramientas
necesarias, genera el informe de toolchain y crea el arbol del engagement.

Carga las skills `bb-toolkit` y `bb-scope` antes de ejecutar.

## Uso

```
/bb-setup [target-domain | --profile recon|web|api|cloud|mobile|full] [--install]
```

## Comportamiento

1. Ejecuta el bloque de deteccion de `bb-toolkit` y guarda la salida en
   `logs/toolchain.txt`.
2. Clasifica la distro y el gestor de paquetes.
3. Determina el perfil de herramientas segun la superficie objetivo.
4. Lista: `DISPONIBLES`, `FALTANTES`, `METODO DE INSTALACION`.
5. Con `--install`, ejecuta SOLO las instalaciones no destructivas y sin sudo
   (pipx, go install, cargo, docker). Las que requieren sudo se muestran como
   comando a ejecutar y se esperan.
6. Crea el arbol del engagement si no existe:

```
bounty_<program>_<YYYY-MM-DD>/
  scope/ recon/ findings/ report/ logs/
```

## Perfiles de herramientas

| Perfil | Incluye |
|---|---|
| `recon` | subfinder, amass, httpx, dnsx, naabu, katana, gau, waybackurls, jq, whois |
| `web` | recon + burpsuite/mitmproxy, ffuf, nuclei, dalfox, sqlmap, commix, katana |
| `api` | recon + kiterunner, graphql-cop, jwt_tool, curlconverter, arjun |
| `cloud` | awscli, gitleaks, trufflehog, cloud_enum, prowler, trivy, grype, syft |
| `mobile` | jadx, apktool, androguard, frida-tools, objection, mobsf (docker), apkleaks |
| `full` | todo lo anterior + hashcat, john, hydra, nuclei, searchsploit |

## Notas

- En Windows nativo, avisa de las limitaciones de red y recomienda WSL2 o VM.
- No ejecutes `curl | bash` sin mostrar el script antes.
- Si `go` no esta instalado, sugiere el metodo (paquete de distro o tarball oficial).
- Registra en `logs/commands.log` cada instalacion ejecutada.
