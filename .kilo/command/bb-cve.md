---
description: Investigacion de CVE contra activos autorizados - versiones afectadas, vector, patches y prueba de explotabilidad
---

# /bb-cve

Investiga y valida CVEs contra el alcance autorizado. Carga `bb-exploit`.

## Uso

```
/bb-cve <asset-or-product> [--cve <CVE-ID>] [--version <ver>] [--search] [--verify]
```

## Flujo

1. **Inventario de versiones**: no te fies del banner. Confirma la version real
   (archivo de release, endpoint de version, `pom.xml`, hash de bundle JS,
   fingerprint de nuclei/httpx).
2. **Matching**: `searchsploit <product>`, `nuclei -t cves/`, `cve-bin-tool`,
   consulta de la base de datos de CVEs.
3. **Evaluacion**:
   - ¿La version cae en el rango afectado? (con EPSS/CVSS)
   - ¿El vector es alcanzable desde internet?
   - ¿Requiere autenticacion / interaccion?
   - ¿Hay parche y desde cuando?
   - ¿Quien controla el componente (cliente o tercero)?
4. **Policy check**: muchos programas excluyen CVEs de terceros. Verifica antes.
5. **Validacion** (`--verify`): PoC minimo, no destructivo, con OOB cuando
   aplique. Confirma la explotabilidad real, no la vulnerabilidad teorica.

## Salida

```
findings/F-00X_cve-<id>/
  notes.md      # version detectada, fuente, rango afectado, policy check
  poc/
  evidence/
  impact.md
```

## Formato de la nota de CVE

```
CVE: CVE-2024-XXXXX
Producto/version detectada: X 1.2.3 (fuente: <endpoint/fichero>)
Rango afectado: >=1.0.0, <1.2.4
Vector: pre-auth remoto / post-auth / local
Alcanzable desde internet: SI/NO (motivo)
Patch disponible: SI (fecha) - el activo esta en version parcheada
Control del componente: cliente / tercero (decision del programa: ...)
PoC: <peticion/resultado>
Confianza: reliable | intermittent | environment-dependent
```

## Notas

- Si el componente es de un tercero y el programa lo excluye, no lo reportes:
  busca variantes propias del cliente (configuracion, integracion, logica).
- No instales exploits de exploit-db sin revisar el codigo.
- Un banner que coincide con una version vulnerable no basta: demuestra.
