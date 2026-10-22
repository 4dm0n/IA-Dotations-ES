---
description: Analisis de aplicacion movil (APK/IPA) - estatico, dinamico con Frida, almacenamiento, deep links y backend
---

# /bb-mobile

Analisis de una app movil dentro del alcance autorizado. Carga `bb-mobile`.

## Uso

```
/bb-mobile <app.apk|app.ipa|package-name> [--static|--dynamic|--backend] [--device <udid>] [--proxy]
```

## Modos

| Modo | Que hace |
|---|---|
| `--static` | apktool/jadx, manifest, permisos, secrets, endpoints, componentes exportados, WebView, deep links, SDKs |
| `--dynamic` | proxy MITM, TLS pinning, root detection, almacenamiento local, hooks Frida/Objection, deep links en vivo |
| `--backend` | extrae endpoint base + tokens, reconstruye la sesion y aplica el checklist de `bb-api` |

## Flujo estatico

```bash
apktool d app.apk -o apk_out -f
jadx -d jadx_out app.apk
aapt dump badging app.apk
apksigner verify --print-certs app.apk
grep -rEo "https?://[a-zA-Z0-9._~:/?#@!$&'()*+,;=%-]+" jadx_out | sort -u > endpoints.txt
grep -rE "android:exported=\"true\"" apk_out/AndroidManifest.xml
grep -rE "setJavaScriptEnabled|addJavascriptInterface|loadUrl\(" apk_out
grep -rE "Log\.(d|i|v|w|e)\(" jadx_out
```

## Flujo dinamico

```bash
mitmproxy --listen-port 8080            # proxy
frida-ps -Uai                          # apps
frida -U -f $PKG -l hooks.js --no-pause # instrumentacion
objection -g $PKG explore               # bypass de pinning, storage, etc.
```

## Flujo backend

```bash
# 1. Extraer base URL y token del APK
# 2. Reproducir la sesion a mano
curl -s "https://api.target/v1/me" -H "Authorization: Bearer $TOKEN" | jq .
# 3. Aplicar bb-api sobre ese backend
```

## Salida

```
findings/mobile/
  static/    manifest.xml  endpoints.txt  secrets.txt  components.txt
  dynamic/   flows.mitm  hooks.js  storage.txt
  backend/   api_inventory.md
```

## Reglas

- Usa solo el binario oficial de la store o el que da el programa.
- No uses cuentas de terceros.
- Un hook posible no es una vulnerabilidad: debe haber impacto demostrado.
- Root/jailbreak detection ausente no es un finding critico.
- Verifica que el backend de la app esta in-scope antes de probarlo.
- Limpia: desinstala la CA del proxy, borra datos, revierte flags.
