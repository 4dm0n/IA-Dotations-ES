---
name: bb-mobile
description: >-
  Use this skill to test mobile applications (Android APK, iOS IPA) within an
  authorized bug bounty scope: static analysis and decompilation, secret and
  endpoint extraction, exported components, WebView and IPC issues, insecure local
  storage, TLS pinning and certificate validation, root/jailbreak detection
  bypass, runtime instrumentation with Frida and Objection, deep link and scheme
  handling, and mobile API/backend testing. Load it when the target is an app.
---

# bb-mobile / Aplicaciones Moviles

Superficie de bounty con hallazgos de alto valor (cliente-side secrets, insecure
storage, exported components, auth bypass en el cliente) y con falsos positivos
frecuentes (todo lo que solo funciona en un dispositivo rooteado no es
vulnerabilidad).

## 0. Decision: donde hacer el trabajo

| Opcion | Cuando | Como |
|---|---|---|
| Analisis estatico local | Siempre, primero | `apktool`, `jadx`, `apk-mitm` |
| Emulador Android | Mayor parte de dynamic | Android Studio AVD / Genymotion |
| Dispositivo real | TLS pinning, hardware, biometrics | Equipo propio con SIM propia |
| Analisis iOS | Solo en macOS | `class-dump`, `plutil`, `frida-ios` |
| Proxy MITM | Dynamic | `mitmproxy`/`Burp` + CA en el dispositivo |

Prepara un dispositivo/emulador propio. Nunca uses el dispositivo ni las cuentas
de otra persona.

## 1. Android: analisis estatico

```bash
# Descarga y metadatos
apktool d app.apk -o apk_out -f
jadx -d jadx_out app.apk          # java -> legible
aapt dump badging app.apk | head -20
apksigner verify --print-certs app.apk
# Permisos declarados vs usados
aapt dump permissions app.apk
```

Buscar en el codigo decompilado:

```bash
# Secrets y endpoints
grep -rEo "(api[_-]?key|secret|token|password|AKIA[0-9A-Z]{16}|sk_live_[0-9a-z]+|-----BEGIN [A-Z ]*PRIVATE KEY-----)" apk_out jadx_out | sort -u
grep -rEo "https?://[a-zA-Z0-9._~:/?#@!$&'()*+,;=%-]+" jadx_out | sort -u > endpoints.txt

# WebView y deeplinks
grep -rE "setJavaScriptEnabled|addJavascriptInterface|loadUrl\(|setAllowFileAccess|setAllowUniversalAccessFromFileURLs" apk_out | head -40
grep -rE "android:exported=\"true\"" apk_out/AndroidManifest.xml
grep -rEo "<intent-filter[^>]*>" apk_out/AndroidManifest.xml
grep -rE "android.permission.(READ_SMS|READ_CONTACTS|READ_CALL_LOG|ACCESS_FINE_LOCATION|CAMERA|RECORD_AUDIO|QUERY_ALL_PACKAGES)" apk_out/AndroidManifest.xml

# Almacenamiento inseguro
grep -rE "MODE_WORLD_READABLE|MODE_WORLD_WRITEABLE|getExternalStorageDirectory|openFileOutput" apk_out | head
grep -rE "Log\.(d|i|v|w|e)\(" jadx_out | head -30   # info leaks en logs
```

Herramientas: `apkid` (packers/obfuscadores), `androguard`, `apkleaks`,
`mobSF` (automatiza casi todo lo anterior), `quark-engine`, `apk-mitm`.

```bash
# MobSF en docker (recomendado para analisis rapido)
docker run -it --rm -p 8000:8000 opcodesecurity/mobilesecurityframework
```

## 2. Android: problemas de configuracion que si son findings

| Hallazgo | Por que se reporta | Verificacion |
|---|---|---|
| Activity/Service/Receiver `exported=true` sin permiso | Cualquier app puede invocar | `adb shell am start -n pkg/.Activity` desde otra app |
| `android:debuggable=true` en release | Ejecucion de codigoarbitrario en el dispositivo | `adb shell` + JDWP, o `run-as` |
| Backup permitido (`allowBackup=true`) | Extraccion de datos de la app via adb | `adb backup` |
| `usesCleartextTraffic=true` | Trafico HTTP interceptable | mitmproxy con CA de usuario |
| Componentes internos con intent-filter expuesto | Abuso de funciones internas | `am start` |
| Deep link / scheme handler sin validacion de origen | Redirect abierto, toma de cuentas | `adb shell am start -a android.intent.action.VIEW -d "scheme://..."` |
| `WebView` con JS + `addJavascriptInterface` en target SDK < 17 | RCE via JS bridge | Hook en runtime |
| TrustManager que acepta todo | MITM trivial | hook de OkHttp/TrustManager |
| Cert pinning ausente o implementacion incorrecta | MITM con CA de usuario | mitmproxy sin pinning |

Clasificacion de severidad: `exported=true` sin permisos y con datos accesibles
-> High/Critical. `cleartext traffic` sin datos sensibles -> Low/Info.

## 3. Android: dynamic con Frida

```bash
# Instalacion
pipx install frida-tools objection
frida --version

# Enumerate aplicaciones
frida-ps -Uai

# Hook de APIs sensibles
frida -U -f com.target.app -l hooks.js --no-pause

# Objection (framework de instrumentacion mas comodo)
objection -g com.target.app explore
```

Hooks de alto valor:

```javascript
// hooks.js - enumeracion de endpoints SSL (TrustManager / OkHttp)
Java.perform(function () {
  var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
  TrustManagerImpl.checkServerTrusted.implementation = function (chain, authType) {
    console.log("[SSL] checkServerTrusted called (pinning bypass candidate)");
    return this.checkServerTrusted(chain, authType);
  };
  // Log de URLs y metodos
  var URL = Java.use("java.net.URL");
  URL.$init.overload("java.lang.String").implementation = function (u) {
    console.log("[URL] " + u);
    return this.$init(u);
  };
});
```

```bash
# Bypass de pinning con objection
objection -g com.target.app explore
  android_sslpinning_disable
  # En runtime:
  objection> setpref sslpinning.enabled false
```

Alternativa: Frida script `frida-pinning` o el modulo `objection` de pinning.
Si el pinning resiste, NO lointagees mas alla de un intento documentado: el
programa puede excluir "bypass de pinning" y, sobre todo, el impacto real
depende de la red (un atacante en la misma red).

## 4. Almacenamiento local en Android

```bash
# Con root o emulador rooteado
adb shell "run-as $PKG ls -la /data/data/$PKG" 2>/dev/null
adb shell "run-as $PKG cat shared_prefs/*.xml" 2>/dev/null
adb shell "ls -la /sdcard/Android/data/$PKG" 2>/dev/null
# Backups
adb backup -f backup.ab $PKG
# Bases de datos locales
adb shell "run-as $PKG sqlite3 databases/app.db '.tables'"
```

Reporta solo si el contenido es sensible (tokens, credenciales, PII) y es
accesible por otras apps en versiones relevantes del OS.

## 5. iOS

Solo en macOS.

```bash
# IPA: descomprimir y analizar Info.plist
unzip -q App.ipa -d app_out
plutil -p app_out/Payload/*.app/Info.plist
# URL schemes
plutil -p app_out/Payload/*.app/Info.plist | grep -A10 CFBundleURLSchemes
# ATS (App Transport Security)
plutil -p app_out/Payload/*.app/Info.plist | grep -A20 NSAppTransportSecurity
# Clases y metodos (requiere jailbreak o dump con class-dump)
class-dump -H app_out/Payload/*.app/App
# Secretos en binario
strings app_out/Payload/*.app/App | grep -iE 'api_key|secret|password|token|https://'
```

Checks iOS:
- `NSAllowsArbitraryLoads` -> ATS deshabilitado.
- Info.plist con keys de API y URLs de backend.
- Esquemas de URL sin validacion (universal link hijacking).
- Datos en `NSUserDefaults` o `Keychain` con accesibilidad incorrecta
  (`kSecAttrAccessibleAlways`).
- Keychain Sharing habilitado sin equipo configurado.
- Logs con `print()`/`NSLog` en release.

## 6. Mobile -> Backend (el enlace de mayor valor)

El hallazgo mobile casi nunca es el fin: es la puerta al backend.

1. Extrae el endpoint base y los tokens del APK/IPA.
2. Reconstruye la sesion autenticada a mano con `curl`/Burp.
3. Aplica el checklist de `bb-api` contra ese backend con la autorizacion de la
   app.
4. Reporta los hallazgos de API con referencia a la app que los expone.

```bash
# Volcar trafico del dispositivo via mitmproxy (con CA instalada)
mitmproxy --listen-port 8080 --set block_global=false
# Dispositivo -> proxy -> Burp/mitm
# Filtrar por host del target
mitmproxy -w flows.mitm
mitmdump -nr flows.mitm -s filter_target.py
```

```python
# filter_target.py
def request(f):
    if "target.com" not in f.request.host:
        f.kill()
```

## 7. Deep links, App Links y Universal Links

```bash
# Android
adb shell am start -a android.intent.action.VIEW -d "https://target.com/callback?token=test"
adb shell am start -a android.intent.action.VIEW -d "myapp://callback?token=test"
adb shell pm dump $PKG | grep -A20 "android.intent.action.VIEW"

# iOS
xcrun simctl openurl booted "myapp://callback?token=test"
```

Impacto real: si un deep link permite cambiar email, tema, o iniciar sesion con
un token, y el token es adivinable o reutilizable -> account takeover. Reporta
con la cadena completa y el impacto demostrado.

## 8. Supply chain de SDKs en apps

```bash
# SDKs de terceros y trackers
grep -rEo "com\.[a-z]+\.[a-z]+" jadx_out | sort -u | head -50
# Facebook/Google Appsflyer/Adjust/Segment
grep -riE "appsflyer|adjust|branch|segment|amplitude|mixpanel|sentry|bugsnag" jadx_out | head
```

Un SDK de terceros con clave de API expuesta o con datos recolectados mas alla
de lo declarado puede ser reportable como "exposicion de clave de API de
tercero", pero la mayoria de programas lo excluyen. Verifica antes.

## 9. Identificacion del binario en la store

Un bounty de mobile se entrega por el APK/IPA. Descarga el oficial de la store
(Play Store / App Store) o el link que da el programa. Si no puedes obtener el
binario oficial, no pruebes una version modificada.

```bash
# Play Store via API (gplaycli / apkeep)
apkeep -a com.target.app -o app.apk
```

## 10. Cobertura minima para decir "cubierto"

- [ ] Estatico: manifest, permisos, endpoints, secrets, componentes exportados
- [ ] Dynamic: proxy MITM, TLS pinning (evaluado), root detection (evaluado)
- [ ] Almacenamiento local revisado
- [ ] Deep links / schemes probados
- [ ] Backend de la app: auth, authz por objeto, inyeccion
- [ ] WebView / JS bridge evaluado
- [ ] Supply chain de SDKs

## 11. Errores que matan un bounty mobile

- Reportar "se puede Hookear X" como finding: no es vulnerabilidad.
- Reportar ausencia de pinning sin impacto (no hay datos sensibles).
- Reportar root/jailbreak detection ausente como critico: casi nunca lo es.
- Reportar permisos declarados sin evidencia de abuso.
- Probar contra el backend sin confirmar que el programa lo incluye en scope.
- Usar una cuenta real de un usuario en lugar de una propia.
