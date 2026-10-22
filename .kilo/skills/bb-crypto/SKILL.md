---
name: bb-crypto
description: >-
  Use this skill for cryptographic analysis within an authorized bug bounty scope:
  encoding vs encryption identification, classical ciphers, hash and password
  analysis, JWT and token crypto weaknesses, ECB and IV reuse, padding oracle,
  key derivation and randomness flaws, blockchain and smart-contract review, and
  CTF-style crypto challenges. Load it when the target involves cryptography.
---

# bb-crypto / Criptografia

En bounty, la criptografia aparece de tres formas: **reto de CTF**, **implementacion
debilitada en un producto** y **algoritmo/proto propio del cliente**.

## 0. Triaje rapido

```bash
# Que es esto? base64, hex, rot13, encriptado?
echo "SGVsbG8gd29ybGQ=" | base64 -d
echo "48656c6c6f" | xxd -r -p
echo "aGVsbG8=" | base64 -d
# Identificador de cifrado comun
python3 -c "
import base64,re,sys
s=sys.argv[1].strip()
if re.fullmatch(r'[A-Za-z0-9+/=]+', s) and len(s)%4==0:
    try:
        d=base64.b64decode(s); print('b64 ->', d)
    except Exception: pass
" "PAYLOAD"
# ROT13 / ROT-N
python3 -c "
import codecs,sys
print(codecs.decode(sys.argv[1],'rot_13'))
" "PAYLOAD"
```

Herramientas: `hash-identifier` (hashid), `hashcat`, `john`, `openssl`, `sage`,
`cryptography` (python), `RsaCtfTool`, `fatihgurso/ctf-crypto`.

## 1. Hashes y passwords

```bash
# Identificar el tipo de hash
hashid -h "5f4dcc3b5aa765d61d8327deb882cf99"
python3 -c "import hashid"  # o usa 'hash-identifier' (BlackArch blackarch-crypto)
# Hashcat: modo 0 = MD5, 100 = SHA1, 1000 = NTLM, 1400 = SHA2-256, 3200 = bcrypt
hashcat -m 0 hashes.txt wordlist.txt --potfile-path hc.pot
hashcat -m 1400 hashes.txt rockyou.txt --potfile-path hc.pot
# John
john --wordlist=wordlist.txt hashes.txt
john --show hashes.txt
john --format=raw-md5 hashes.txt
```

Contexto de bounty: un hash encontrado en un activo in-scope puede ser una
credencial real. Si el programa lo permite, reporta "credencial expuesta" con
el hash hasheado (nunca el plaintext) y la ruta de cracking.

## 2. Cifrados clasicos

```bash
# Frecuencia y analisis
# decrypt.sh (BlackArch) - Caesar, Vigenere, Atbash, Rail Fence, Substitution
# https://github.com/0x04d0/decrypt.sh
# Cifrado de Vigenere
python3 -c "
key=''
"
# XOR y ROT (comunes)
python3 - <<'PY'
def xor(data,key):
    return bytes(b ^ key[i % len(key)] for i,b in enumerate(data))
print(xor(bytes.fromhex('HEX'), b'KEY'))
PY
# Base64 multi-capa
for i in $(seq 1 5); do echo "$PAYLOAD" | base64 -d 2>/dev/null && break; done
```

## 3. JWT y tokens

```bash
# Decodificar y auditar
echo "$JWT" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq .
python3 jwt_tool.py -t "$JWT" -C -d jwt_common.txt          # attacks
python3 jwt_tool.py -t "$JWT" -X k -X pk -X n            # key confusion, none
```

Checklist JWT:
| Vector | Como se prueba | Impacto |
|---|---|---|
| `alg: none` | Firmar con `none` | Critical |
| HS/RS confusion | Firmar HS256 con la public key | Critical |
| `kid` injection (path traversal, SQLi, JWK URL) | `kid: "../../dev/null"`, `kid` = URL a tu JWK | Critical |
| JWK/JWKS substitution | Servidor usa tu JWKS | Critical |
| Missing `exp` | Firmar sin exp | Medium |
| Missing `aud`/`iss` validation | Firmar con aud distinto | High |
| Secret weak (HS256 con clave corta) | `jwt_tool -C` con wordlist | Critical |
| Claim injection | Anadir `"admin":true`, `"role":"admin"` | Depends |
| Token no invalido tras logout/cambio de password | Reusar token viejo | High |

```bash
# Firmar con none (jwt_tool)
python3 jwt_tool.py -t "$JWT" -X n -I '{"alg":"none","typ":"JWT"}' -S -p hs256.key
```

## 4. Debilidades de implementacion

| Debilidad | Como se detecta | Impacto |
|---|---|---|
| ECB mode | Bloques repetidos en ciphertext | Leakage de patrones |
| IV fijo o reutilizado | Mismo IV con distinta clave (en dos mensajes) | Chosen-plaintext |
| IV aleatorio con GCM y nonce reutilizado | Nonce repetido | Rompe autenticacion |
| Padding oracle | Respuesta distinta con padding invalido | Descifrado completo |
| Cifrado sin autenticacion (CFB/CTR sin MAC) | Manipulacion de bits | Forjatura de plaintext |
| KDF debiles (MD5/SHA1, few iterations, no salt) | `hashcat` lo rompe | Offline cracking |
| Clave derivada del password sin KDF | Codigo visible | |
| Random no criptografico (`random`, `rand()`) para claves/IV | Codigo | Predecible |
| Hardcoded key/IV en codigo | grep | |
| Compare no constant-time | codigo | Timing leak (raramente pagable) |

```bash
# Padding oracle (practica): comparar status/longitud/tiempo con padding valido vs invalido
python3 - <<'PY'
import requests
BASE="https://target/"; C=open('cipher.txt').read()
for pad in ['','AA','AAAA']:
    b=requests.get(BASE, params={'c': C[:-len(pad)]+pad}, timeout=10)
    print(pad or 'none', b.status_code, len(b.content), b.elapsed.total_seconds())
PY
```

## 5. Protocolos, TLS y firma

- TLS: `testssl.sh`, `sslscan`, `nuclei -t ssl/`, `sslyze`.
- Firma de JWT mal implementada: firma sobre datos no verificados, `kid` controlado.
- Verificacion de firma de webhook ausente o incorrecta (ver `bb-api`).
- Cifrado "de homemade" (XOR con clave fija, cifrado de Vigenere en producto): es
  reportable si protege datos sensibles, con impacto real (credenciales/PII).
- Ofuscacion != cifrado: si el claim es "el token esta cifrado" y es reversible
  trivialmente, es un finding.

## 6. Blockchain y smart contracts (Solidity)

```bash
# Slither
pipx install slither-analyzer
slither . --print human-summary
# Echidna / Foundry
forge build && forge test
# Mythril
pipx install mythril
myth analyze contracts/ --solver z3
# Semgrep con reglas de solidity
semgrep --config p/semgrep/solidity .
```

Patrones a revisar manualmente:
- `tx.origin` en vez de `msg.sender`.
- Reentrancy: estado actualizado despues de la llamada externa.
- `delegatecall` a codigo no confiable.
- Falta de `onlyOwner`/control de acceso en funciones criticas.
- Randomness on-chain (`block.timestamp`, `blockhash`).
- Integer overflow (Solidity <0.8 sin SafeMath).
- `selfdestruct` y `SELFDESTRUCT` post-Cancun.
- Approve front-running / permit2.

Solo si el programa incluye smart contracts. En bounty web, esto casi nunca aplica.

## 7. CTF y retos

- Usa `sage` para ataques a RSA (`factoring`, `small e`, `Wiener`, `common modulus`),
  a ECDSA (nonce reuse/repeated `k`), a LWE/GLWE si aplica.
- `RsaCtfTool` automatiza ataques RSA comunes.
- Hash: rainbow tables, `hashcat` con modo correcto.
- Encoding: cascadas, `base64` multiple, XOR con clave corta -> `cribdrag`/`xortool`.

## 8. Plantilla de finding cripto

```
Titulo: <Algoritmo> con <debilidad> en <componente> permite <impacto>
CWE: CWE-327 (Broken/Risky Crypto Algorithm), CWE-329 (Not Using Unpredictable IVs),
     CWE-328 (Reversible One-Way Hash), CWE-326 (Inadequate Encryption Strength)
CVSS: con justificacion del impacto real (confidencialidad/integridad)
Evidencia: par de mensajes con IV repetido, o token forjado aceptado (200 + datos)
Impacto: lectura de datos de otros usuarios, falsificacion de tokens, etc.
Fix: AES-GCM con nonce unico y aleatorio, o migracion a un KDF/hashing moderno
```

## 9. Errores que matan un bounty cripto

- Reportar "usa SHA1" sin impacto.
- Reportar "el token es reversible" sin demostrar que el contenido es sensible.
- Reportar una weakness teorica de RSA sin factorizacion real.
- Reportar una clave de prueba/example de un repo publico (esta designed para ser publica).
- Exponer el plaintext de un hash crakeado en el reporte publico: ponlo en el
  canal privado o en un attachment protegido.
