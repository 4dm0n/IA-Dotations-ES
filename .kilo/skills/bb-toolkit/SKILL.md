---
name: bb-toolkit
description: >-
  Use this skill to detect the host security distribution (Kali, BlackArch, Garuda,
  Parrot, Debian, Arch, WSL, macOS) and resolve every security tool to a working
  invocation, including installation commands per package manager, BlackArch
  category mapping, and safe fallbacks when a tool is missing. Load this first in
  any bug bounty or security assessment so no command is ever run speculatively.
---

# bb-toolkit / Toolchain Adaptativo

Determina el entorno real y traduce "necesito la herramienta X" en una invocacion
que funciona en ESA maquina. Nunca ejecutes una herramienta sin resolverla antes.

## 1. Deteccion del entorno

Ejecuta este bloque y captura la salida en `logs/toolchain.txt`:

```bash
echo "=== OS ==="; cat /etc/os-release 2>/dev/null | grep -E '^(NAME|VERSION|ID|ID_LIKE|PRETTY_NAME)='
echo "=== ARCH ==="; uname -m; uname -r
echo "=== PKG MGR ==="; for p in apt apt-get dnf yum pacman zypper apk brew; do command -v $p >/dev/null 2>&1 && echo "found: $p"; done
echo "=== ID ==="; id -u; echo "sudo:"; command -v sudo >/dev/null 2>&1 && echo yes || echo no
echo "=== WSL ==="; grep -qi microsoft /proc/version 2>/dev/null && echo WSL || echo native
echo "=== TOOLS ==="; for t in nmap masscan naabu subfinder amass httpx nuclei ffuf feroxbuster gobuster nikto sqlmap wpscan jq curl wget git python3 pipx pip go cargo docker msfconsole burpsuite mitmproxy gitleaks trufflehog semgrep jadx apktool frida openssl hashcat john aircrack-ng tshark tcpdump; do printf "%-16s %s\n" "$t" "$(command -v $t 2>/dev/null || echo MISSING)"; done
```

Clasifica el host en una de estas familias:

| Familia | Detecta por | Gestor | Notas |
|---|---|---|---|
| **Kali** | `ID=kali` / `ID_LIKE=debian` + `kali` | `apt` | Repo rolling en `http.kali.org/kali` |
| **BlackArch** | `ID=blackarch` / `ID_LIKE=arch` + repo blackarch | `pacman` | Grupos `blackarch-<categoria>` |
| **Garuda** | `ID=garuda` / `ID_LIKE=arch` | `pacman` | Arch-based, hereda repo BlackArch |
| **Parrot** | `ID=parrot` | `apt` | Debian-based, subset de Kali |
| **Debian/Ubuntu** | `ID=debian\|ubuntu` | `apt` | Fuente Kali no habilitada por defecto |
| **Arch limpio** | `ID=arch` | `pacman` | Requiere repo BlackArch anadido |
| **Fedora/RHEL** | `ID=fedora\|rhel\|centos` | `dnf` | Sin BlackArch; usar installs via git/pip/go/docker |
| **WSL** | `/proc/version` contiene `microsoft` | `apt` | Limitaciones: sin raw sockets, sin `ping` a veces, sin `sudo` por defecto |
| **macOS** | `uname` = `Darwin` | `brew` | Solo stack web/API; sin tools de red cruda |
| **Windows nativo** | `uname` no aplica (PowerShell) | `choco`/`winget`/`scoop` | Recomendado: usar WSL2 |

**WSL y Windows son la causa #1 de fallos en bounty hunts.** En Windows nativo, la
mayoria de las herramientas de red (SYN scan, sniffing, ARP, raw sockets) NO
existen o no funcionan. En WSL2 funcionan parcialmente (nmap -sS sin root falla;
`ping` puede fallar). Antes de cualquier escaneo de red, decide:

- Opcion A (recomendada para hunt serio): VM Linux dedicada (Kali/BlackArch) con
  modo bridge, o VPS con IP propia, o contenedor con `--cap-add=NET_ADMIN --cap-add=NET_RAW`.
- Opcion B (hunt web/API puro): WSL2 o nativo con stack web es suficiente.

## 2. Matriz BlackArch -> paquete por distro

El modelo de categorias de BlackArch es la taxonomia de referencia. Usa esta tabla
para resolver la instalacion. Las herramientas marcadas con (pip)/(go)/(cargo)/(docker)
se instalan siempre por su gestor original, en cualquier distro.

### Recon y enumeracion
| BlackArch | Herramienta | Kali/Parrot/Debian | BlackArch/Garuda | Notas |
|---|---|---|---|---|
| blackarch-recon | amass | `apt install amass` | `pacman -S amass` | |
| blackarch-recon | subfinder | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` | idem (go) | |
| blackarch-recon | assetfinder | `go install github.com/tomnomnom/assetfinder@latest` | idem | |
| blackarch-scanner | sublist3r | `pipx install sublist3r` | `pipx install` | legacy |
| blackarch-recon | httpx | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` | idem | |
| blackarch-recon | dnsx | `go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest` | idem | |
| blackarch-recon | naabu | `go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest` | idem | |
| blackarch-recon | katana | `go install github.com/projectdiscovery/katana/cmd/katana@latest` | idem | crawler |
| blackarch-scanner | gau | `go install github.com/lc/gau/v2/cmd/gau@latest` | idem | URLs historicas |
| blackarch-scanner | waybackurls | `go install github.com/tomnomnom/waybackurls@latest` | idem | |
| blackarch-recon | bbot | `pipx install bbot` | idem | todo-en-uno, excelente para bounty |
| blackarch-misc | gospider | `go install github.com/jaeles-project/gospider@latest` | idem | |
| blackarch-misc | unfurl | `go install github.com/tomnomnom/unfurl@latest` | idem | |

### Scanner y superficie
| BlackArch | Herramienta | Kali/Debian | BlackArch/Garuda |
|---|---|---|---|
| blackarch-scanner | nmap | `apt install nmap` | `pacman -S nmap` |
| blackarch-scanner | masscan | `apt install masscan` | `pacman -S masscan` |
| blackarch-scanner | nuclei | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` | idem |
| blackarch-scanner | nikto | `apt install nikto` | `pacman -S nikto` |
| blackarch-scanner | whatweb | `apt install whatweb` | `pacman -S whatweb` |
| blackarch-scanner | wpscan | `apt install wpscan` (o `gem install wpscan`) | `pacman -S wpscan` |
| blackarch-scanner | arjun | `pipx install arjun` | idem |
| blackarch-scanner | ffuf | `go install github.com/ffuf/ffuf/v2@latest` | idem |
| blackarch-scanner | feroxbuster | `cargo install feroxbuster` | idem |
| blackarch-scanner | gobuster | `go install github.com/OJ/gobuster/v3@latest` | idem |
| blackarch-scanner | dirsearch | `pipx install dirsearch` | idem |
| blackarch-scanner | zgrab | `go install github.com/zmap/zgrab/cmd/zgrab@latest` | idem |
| blackarch-fingerprint | wappalyzer / httpx | via go | idem |
| blackarch-scanner | nmap-scripts | `apt install nmap` (incluye) | `pacman -S nmap` |

### Web application
| BlackArch | Herramienta | Instalacion |
|---|---|---|
| blackarch-webapp | burpsuite | `apt install burpsuite` / `pacman -S burpsuite` / `docker run -it --rm -v /tmp:/tmp burpsuite/burpsuite` |
| blackarch-webapp | mitmproxy | `pipx install mitmproxy` |
| blackarch-proxy | zaproxy | `apt install zaproxy` / docker `ghcr.io/zaproxy/zaproxy` |
| blackarch-webapp | sqlmap | `apt install sqlmap` / `pacman -S sqlmap` / `pipx install sqlmap` |
| blackarch-webapp | xsser | `pipx install xsser` |
| blackarch-webapp | commix | `git clone https://github.com/commix/commix` + `pipx install .` |
| blackarch-webapp | dalfox | `go install github.com/hahwul/dalfox/v2@latest` |
| blackarch-webapp | nuclei-templates | `nuclei -update-templates` |
| blackarch-webapp | katana | (ver recon) |
| blackarch-webapp | kustomize/hakrawler | `go install`/`docker` |
| blackarch-webapp | corsy | `pipx install corsy` |
| blackarch-webapp | param-miner | `go install github.com/lc/gau` + `arjun` |
| blackarch-webapp | jaeles | `docker run ghcr.io/jaeles-project/jaeles` |

### API
| Herramienta | Instalacion |
|---|---|
| kiterunner | `go install github.com/assetnote/kiterunner@latest` |
| graphql-cop | `go install github.com/dolevf/graphql-cop@latest` |
| grype / syft | `go install` o release bin |
| jwt_tool | `git clone https://github.com/ticarpi/jwt_tool` |
| postman / insomnia | GUI, no necesario |

### Mobile
| Herramienta | Instalacion |
|---|---|
| jadx | `apt install jadx` / `pacman -S jadx` / release zip |
| apktool | `apt install apktool` / `pacman -S apktool` |
| apkanalyzer | parte del Android SDK |
| androguard | `pipx install androguard` |
| mobSF | `docker run -it --rm -p 8000:8000 opcodesecurity/mobilesecurityframework` |
| frida-tools | `pipx install frida-tools` |
| objection | `pipx install objection` |
| drozer | `pipx install drozer` (agent en dispositivo) |
| mobSF / apkleaks | `docker` / `go install github.com/dwisiswant0/apkleaks` |
| ipa | `class-dump` (macOS), `plutil` (macOS), `ipsw` (macOS) |

### Cloud / CI / Secrets
| Herramienta | Instalacion |
|---|---|
| gitleaks | `go install github.com/gitleaks/gitleaks/v8@latest` |
| trufflehog | `go install github.com/trufflesecurity/trufflehog/v3@latest` |
| awscli | `pipx install awscli` |
| cloud_enum | `pipx install cloud_enum` |
| cloudsploit | `npm i -g cloudsploit` |
| scoutsuite | `docker run scoutsuite/scoutsuite` |
| kube-hunter | `docker run ghcr.io/armosec/kube-hunter` |
| prowler | `pipx install prowler` / docker |
| nuclei cloud templates | `nuclei -t cloud/` |
| s3scanner / bucketgrep | `go install` / `pipx` |
| pacer / dnsrecon | `pipx install dnsrecon` |

### Explotacion y CVE
| Herramienta | Instalacion |
|---|---|
| metasploit | `apt install metasploit-framework` / `pacman -S metasploit` / docker `metasploitframework/metasploit-framework` |
| searchsploit | `apt install exploitdb` / `pacman -S exploitdb` |
| pwntools | `pipx install pwntools` |
| gdb + pwndbg | `apt install gdb` (+ gdbinit) |
| checksec | `pipx install checksec` |
| ROPgadget / ropper | `pipx install ROPgadget` / `ropper` |
| ysoserial | jar release |
| CVE Search | `pipx install cve-bin-tool` / `searchsploit` / `nuclei -t cves/` |

### Crypto y cracking
| Herramienta | Instalacion |
|---|---|
| hashcat | `apt install hashcat` / `pacman -S hashcat` |
| john | `apt install john` / `pacman -S john` |
| hydra | `apt install hydra` / `pacman -S hydra` |
| hashcat / john legacy | `apt install hashcat-legacy john` (en Kali) |
| aircrack-ng | `apt install aircrack-ng` / `pacman -S aircrack-ng` |
| jwt_tool | (ver API) |

### Red team / azul (defensive)
| Herramienta | Instalacion |
|---|---|
| suricata | `apt install suricata` / `pacman -S suricata` |
| zeek | `apt install zeek` / `pacman -S zeek` (o docker `zeek/zeek` / `blackarch-networking`? no: `pacman -S zeek`) |
| suricata-update | `suricata-update` |
| fail2ban | `apt install fail2ban` |
| aide | `apt install aide` |
| wazuh | docker `wazuh/wazuh-manager` |
| osquery | `apt install osquery` / `osqueryi` |
| yara | `apt install yara` / `pacman -S yara` |
| sigma-cli | `pipx install sigma-cli` (conversion de reglas) |
| elastalert | docker |
| velociraptor | docker |

### Forense / OSINT
| Herramienta | Instalacion |
|---|---|
| theharvester | `pipx install theHarvester` |
| holehe | `pipx install holehe` (email breach) |
| sherlock | `pipx install sherlock` |
| maigret | `pipx install maigret` |
| spiderfoot | `pipx install spiderfoot` |
| recon-ng | `pipx install recon-ng` |
| volatility3 | `pipx install volatility3` |
| sleuthkit / testdisk | `apt install sleuthkit testdisk` |

### Palabras clave
| Fuente | Ubicacion / Instalacion |
|---|---|
| SecLists | `/usr/share/seclists` (Kali) o `/usr/share/seclists` (BlackArch `blackarch-wordlist`) |
| Assetnote wordlists | `go install` / repo `assetnote/wordlists` |
| 4yuuk | repo `four4uu` |
| SecLists-Basic | `git clone https://github.com/danielmiessler/SecLists` |

Si `seclists` no esta instalado, la alternativa portable es clonar el repo
SecLists en `~/wordlists/SecLists` y apuntar `-w` ahi.

## 3. Procedimiento de resolucion de una herramienta

Para cada herramienta `T` que vayas a usar:

1. `command -v T` -> si existe, usala.
2. Si no existe, busca el metodo de instalacion en la matriz segun la familia del host.
3. Si la instalacion requiere sudo/root, NO la ejecutes en silencio: propongela al
   solicitante con el comando exacto.
4. Si no hay paquete, usa la via original (go/pipx/cargo/docker/git).
5. Si tampoco hay via original, busca el fallback documentado en la seccion 4.
6. Registra en `logs/toolchain.txt`: `T | metodo | version | estado`.

## 4. Fallbacks universales (sin instalar nada)

| Necesitas | Sin instalar | Nota |
|---|---|---|
| Escaneo de puertos | `bash` con `/dev/tcp`, `curl` para HTTP | Lento pero funciona en WSL/Windows |
| HTTP fuzzing | `curl` con loops, `ffuf` via docker | |
| Enumeracion DNS | `dig`, `nslookup`, `host` | `dnsx` via docker si falta |
| Certificados | `openssl s_client -connect host:443 -servername host` | `crtsh` via curl |
| JSON pretty | `python3 -m json.tool`, `jq` | |
| Web crawling | `wget --mirror`, `curl` recursivo | |
| Certificate transparency | `curl "https://crt.sh/?q=%25.target.com&output=json"` | |
| Nuclei | `docker run projectdiscovery/nuclei` | |
| Exploits | `curl` a exploit-db / searchsploit web | |
| Hash cracking | `hashcat` via docker o `john` via docker | |
| Trafico interceptado | `mitmproxy` via docker con `--network host` | |

## 5. Instalacion masiva por familia

Kali/Debian/Parrot:
```bash
sudo apt update && sudo apt -y install nmap masscan naabu nuclei jq curl wget git python3-pip \
  build-essential dnsutils whois whatweb nikto sqlmap wpscan dirb gobuster hashcat john \
  hydra aircrack-ng wireshark tshark tcpdump yara python3-pipx chromium
python3 -m pip install --user pipx && pipx ensurepath
# binarios Go sin soporte de distro (ejemplo)
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf/v2@latest
```

BlackArch/Garuda:
```bash
sudo pacman -Sy
sudo pacman -S --needed blackarch-recon blackarch-scanner blackarch-webapp \
  blackarch-crypto blackarch-exploitation blackarch-defensive blackarch-forensic \
  blackarch-networking blackarch-wordlist blackarch-code-audit blackarch-proxy
# Si el repo BlackArch no esta anadido (Arch/Garuda limpio):
curl -s https://blackarch.org/strap.sh | sudo bash
# o manualmente:
# echo "[blackarch] Include = /etc/pacman.d/blackarch-mirrorlist" >> /etc/pacman.conf
# sudo pacman -Sy
```

Fedora/RHEL:
```bash
sudo dnf install -y nmap nmap-ncat nmap-nsel masscan jq curl git python3-pip \
  python3-pipx gcc gcc-c++ make wireshark tcpdump yara
# el resto via go/pipx/docker
```

macOS:
```bash
brew install nmap jq curl git ripgrep wget masscan go rust python@3.12
brew install --cask burpsuite-community wireshark
```

## 6. Seguridad de la instalacion

- Descarga solo del origen oficial, verifica checksums cuando existan.
- No ejecutes scripts de instalacion de terceros sin revisarlos (`curl | bash`).
  Muestra el script al solicitante antes de ejecutarlo.
- Instala en un contenedor o VM cuando la herramienta sea de riesgo alto
  (nuclei con templates de `dos`, `fuzz`, fuzzers). Nuclei: `nuclei -t .` nunca.
- No instales nada que no vayas a usar: cada paquete es superficie de ataque en
  tu propia maquina.

## 7. Salida esperada

```
logs/toolchain.txt
  HOST: Kali GNU/Linux Rolling 2026.1 (amd64) [WSL: no]
  PKG_MANAGER: apt
  AVAILABLE: nmap(7.95) nuclei(3.0.2) httpx(1.6.9) ffuf(2.1.0) jq(1.7.1) ...
  MISSING: masscan wpscan mitmproxy gitleaks
  PLAN:
    - masscan      -> apt install masscan (sudo)
    - wpscan       -> apt install wpscan (sudo) | fallback: gem install wpscan
    - mitmproxy    -> pipx install mitmproxy (no sudo)
    - gitleaks     -> go install github.com/gitleaks/gitleaks/v8@latest
  CAPABILITY_NOTES:
    - SYN scan requires root (sudo) - yes
    - Raw sockets for sniffing: yes
    - WSL: n/a
```
