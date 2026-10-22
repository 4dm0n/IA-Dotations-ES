# Distribuciones: diferencias, quirks e instalacion

Referencia de detalle para `bb-toolkit`. La tabla resumen vive en `SKILL.md`.

## 1. Kali Linux

- Base: Debian testing. Repos: `http://http.kali.org/kali kali-rolling main`.
- Herramientas propias de Kali (`nuclei`, `httpx`, `naabu`, `subfinder`, `ffuf`,
  `interactsh-client`) estan empaquetadas en `kali` (o `kali-tools-*`).
--install:
  ```bash
  sudo apt update && sudo apt -y install <pkg>
  ```
- Repos extra utiles: `https://pkg.kali.org/pkg/kali-apt-main` (ya incluido),
  `pwntools` via `pipx`, `angr` via `pipx`.
- Kali ofrece una imagen "Kali Linux with NetHunter" y "kali-everything".
- `kali-tweak` para configurar desktop, mirror y repositorios.
- Nota: `kali` es rolling; algunos paquetes cambian de nombre entre versiones.
  Si `apt install` falla, busca con `apt search <tool>`.

Herramientas kali tipicas y su paquete:
| Tool | Paquete Kali |
|---|---|
| nmap | `nmap` |
| masscan | `masscan` |
| nuclei | `nuclei` |
| httpx/naabu/dnsx/subfinder/katana | `httpx`, `naabu`, `dnsx`, `subfinder`, `katana` |
| ffuf | `ffuf` |
| sqlmap | `sqlmap` |
| burpsuite | `burpsuite` |
| zaproxy | `zaproxy` |
| gobuster | `gobuster` |
| whatweb | `whatweb` |
| wpscan | `wpscan` |
| hashcat / john | `hashcat`, `john` |
| aircrack-ng | `aircrack-ng` |
| metasploit | `metasploit-framework` |
| searchsploit | `exploitdb` |
| jadx / apktool | `jadx`, `apktool` |
| frida / objection | `frida-tools`, `objection` |
| gitleaks / trufflehog | `gitleaks`, `trufflehog` |
| seclists | `seclists` |
| yara / suricata / zeek | `yara`, `suricata`, `zeek` |
| john legacy / hashcat legacy | `john`, `hashcat-legacy` |

## 2. BlackArch Linux

- Base: Arch. Repo extra: `blackarch` (groupes `blackarch-<categoria>`).
- Instalacion del repo:
  ```bash
  curl -s https://blackarch.org/strap.sh | sudo bash   # revisar el script antes
  # o manual:
  echo "[blackarch]" >> /etc/pacman.conf
  echo "Include = /etc/pacman.d/blackarch-mirrorlist" >> /etc/pacman.conf
  sudo pacman -Sy
  ```
- Listar: `pacman -Sg blackarch` | `pacman -Ss blackarch`.
- Instalar grupo: `sudo pacman -S blackarch-webapp --needed`.
- Instalar una sola herramienta: `sudo pacman -S nmap` (los nombres coinciden
  mayormente con el nombre del paquete upstream).
- BlackArch provee `blackarch-keyring` y `blackarch-mirrorlist` en AUR para
  distribuciones Arch limpias.

Categorias oficiales y su contenido resumido:
| Categoria | Contenido |
|---|---|
| blackarch-recon | Enumeracion de subdominios, OSINT, activos |
| blackarch-scanner | Nmap, Nuclei, escaneres, fuzzers de contenido |
| blackarch-webapp | Burp, SQLMap, XSS, fuzzing web, CMS scanners |
| blackarch-exploitation | Metasploit, ROP, shellcode, exploit frameworks |
| blackarch-crypto | Hashcat, John, Aircrack, cifrados |
| blackarch-cracker | Fuerza bruta de credenciales |
| blackarch-code-audit | Analisis estatico de codigo |
| blackarch-binary / reversing / disassembler / decompiler | Ingenieria inversa |
| blackarch-fuzzer | AFL, fuzzers de protocolo |
| blackarch-forensic / anti-forensic | Forense de disco y memoria |
| blackarch-defensive | Deteccion, IDS, hardening, auditoria |
| blackarch-ids | IDS de red |
| blackarch-networking | Utilidades de red |
| blackarch-sniffer | Captura de trafico |
| blackarch-spoof | Suplantacion ARP/DNS |
| blackarch-wireless | Auditoria WiFi |
| blackarch-proxy | Proxies e interceptores |
| blackarch-honeypot | Honeypots |
| blackarch-database | Herramientas de bases de datos |
| blackarch-automation | Orquestacion y scripts |
| blackarch-mobile | Analisis movil |
| blackarch-cloud / automation | Nube y CI/CD |
| blackarch-malware | Analisis de malware |
| blackarch-windows | Herramientas de Windows / AD |
| blackarch-wordlist | Diccionarios |
| blackarch-crypto, blackarch-social, blackarch-stego, blackarch-tunnel, blackarch-voip, blackarch-radio, blackarch-nfc, blackarch-bluetooth, blackarch-car, blackarch-rfid | Nichos |
| blackarch-misc | Utilidades varias |

## 3. Garuda Linux

- Base: Arch con rolling release y sus propios repos (`garuda`).
- Los repos de Arch funcionan igual: `pacman -S`.
- El repo BlackArch se puede añadir con el strap script, pero revisa si ya esta
  presente (`grep blackarch /etc/pacman.conf`).
- `garuda-assistant` ofrece instalacion grafica de software y drivers.
- kernel linux-zen por defecto: mejora rendimiento de red en VMs, pero cuidado con
  modulos fuera de arbol (algunos IDS requieren modulos del kernel oficial).
- Para herramientas Go/Python, usa igual `go install` / `pipx`.

## 4. Parrot Security OS

- Base: Debian (no Kali). `apt install <pkg>`.
- Incluye un subconjunto de herramientas: nmap, wireshark, tshark, hydra, john,
  aircrack-ng, sqlmap, nikto, gobuster, whatweb, burpsuite, metasploit, msfvenom,
  radare2, gdb, binwalk, autopsy, volatility, wireshark.
- Falta mucha cosa de ProjectDiscovery: instala con `go install` o descarga el
  binario de releases.
- Kali repos en Parrot se pueden usar pero no se recomienda (conflictos de
  dependencias). Si hace falta, usa `sudo apt install -t kali-rolling <pkg>` con
  pinning.

## 5. Debian/Ubuntu limpios

- Habilita los repos de Kali solo si necesitas sus paquetes:
  ```bash
  echo "deb http://http.kali.org/kali kali-rolling main" | sudo tee /etc/apt/sources.list.d/kali.list
  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3C2EEF6EE18A8C5B
  ```
  Alternativa moderna (keyring con sudo):
  ```bash
  sudo apt install -y kali-archive-keyring
  ```
- Alternativa sin repos de Kali: usa `pipx`, `go install`, `cargo`, `docker`.
- Docker es la via mas limpia para herramientas aisladas:
  ```bash
  docker run --rm projectdiscovery/nuclei -version
  docker run --rm -v "$PWD:/work" ghcr.io/jaeles-project/jaeles
  ```

## 6. Fedora / RHEL / CentOS / Rocky

- `sudo dnf install -y nmap nmap-nsel masscan jq curl git python3-pip python3-pipx \
  gcc gcc-c++ make wireshark tcpdump yara bind-tools whois`
- Sin soporte nativo de la mayoria: `go install`, `pipx`, `cargo`, `docker`.
- SELinux enforcing: para hacer sniffing en interfaces, puede requerir
  `setsebool -P packet_socket_t 1` (solo en laboratorio).

## 7. Arch limpio

```bash
sudo pacman -S --needed base-devel git python python-pip go rust
sudo pacman -S --needed nmap masscan jq curl bind whois wireshark-cli tcpdump yara
python -m pip install --user pipx && pipx ensurepath
# repo BlackArch opcional
curl -s https://blackarch.org/strap.sh | sudo bash
```

## 8. macOS

```bash
brew install nmap jq curl git wget go rust python@3.12 ripgrep masscan
brew install --cask burpsuite-community wireshark
python3 -m pip install --user pipx && pipx ensurepath
```
Limitaciones: sin raw sockets para SYN scan sin root, sin `ping` a nivel de
sistema sin permisos, sin herramientas de red de bajo nivel (ettercap, arpspoof
necesitan Linux). Docker Desktop permite usar las imagenes Linux de las tools.

## 9. Windows nativo (PowerShell)

No es un entorno de hacking. Opciones:

| Opcion | Pros | Contras |
|---|---|---|
| WSL2 (Debian/Ubuntu) | Casi todo funciona | SYN scan sin root, rendimiento de red, sin burp nativo |
| Docker Desktop + WSL2 | Tools aisladas y reproducibles | Requiere WSL2 |
| VM (VMware/VirtualBox/Hyper-V) | Entorno completo, bridge para red | Memoria, snapshots |
| Kali dentro de WSL2 | Muy parecido al nativo en Linux | Limitaciones de red siguen |

Instalacion en WSL2:
```bash
sudo apt update && sudo apt -y install nmap masscan jq curl git python3-pip \
  build-essential dnsutils whois whatweb sqlmap nikto hashcat john wireshark-common
python3 -m pip install --user pipx && pipx ensurepath
# tool de Windows desde Linux
```

Tecnicas nativas de Windows que si son utiles para bounty web:
- `curl.exe` esta disponible (no es alias de Invoke-WebRequest).
- PowerShell: `Invoke-WebRequest`, `iwr`, `Invoke-RestMethod`.
- `winget install BurntSushi.ripgrep.MSVC` para utilidades.
- `choco install nmap` / `scoop install nmap`.
- Windows no tiene `nmap` nativo confiable: usa WSL2 o Docker.

## 10. Docker como toolchain portable (recomendado para CI)

```bash
# Nuclei
docker run --rm -v "$PWD:/root" projectdiscovery/nuclei:latest \
  -l hosts.txt -severity critical,high -o nuclei.txt

# Nuclei con DNS resolution
docker run --rm -v "$PWD:/root" projectdiscovery/nuclei:latest \
  -l hosts.txt -dns-validate -silent

# Subfinder
docker run --rm -v "$PWD:/root" projectdiscovery/subfinder:latest \
  -d target.com -all -o subs.txt

# Jaeger / sqlmap / gobuster / nikto
docker run --rm -v "$PWD:/root" sqlmap/sqlmap
docker run --rm -v "$PWD:/root" spiderfoot/spiderfoot
```

Ventajas: mismo entorno en cualquier SO, sin sudo, sin contaminar el host.
Inconvenientes: pierde algo de acceso a la red del host, y el TARGET debe ser
alcanzable desde el contenedor (usa `host.docker.internal` en Windows/macOS).

## 11. Verificacion post-instalacion

```bash
# Version de cada tool (para el informe de toolchain)
for t in nmap nuclei httpx ffuf sqlmap katana gitleaks frida jadx; do
  printf "%-12s %s\n" "$t" "$($t -version 2>&1 | head -1)"
done
# Comprobacion de red
sudo nmap -sn -iL /dev/null 2>/dev/null || echo "sin sudo: usa -sT"
```
