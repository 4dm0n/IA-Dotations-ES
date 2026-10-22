---
description: Lado defensivo - reglas de deteccion Sigma/Elastic/Suricata, hardening, logging y purple team
---

# /bb-blue

Genera las salidas defensivas derivadas de los hallazgos. Carga `bb-blue`.

## Uso

```
/bb-blue [F-001,F-002 | --all] [--assets <file>] [--sigma] [--elastic] [--suricata] [--playbook] [--matrix]
```

## Salidas

```
report/
  detections.md            # indice de reglas
  rules/
    <finding>-<id>.yml     # Sigma
    <finding>-elastic.ndjson
    <finding>-suricata.rules
  hunting.md               # queries de hunting (Elastic KQL, Splunk SPL, Zeek)
  hardening.md             # controles por tecnologia
  playbooks/
    F-001_playbook.md      # deteccion -> contencion -> erradicacion -> recuperacion
  attack_matrix.md         # MITRE ATT&CK por activo con gaps
```

## Flujo por finding

1. **TTP**: mapea el finding a tecnica MITRE ATT&CK.
2. **Telemetria**: que log/stream detectaria el ataque y donde vive.
3. **Regla**: escribe Sigma (portable) + conversion a Elastic/Suricata.
4. **Validacion purple**: ejecuta el PoC en condiciones controladas y comprueba
   que la regla dispara. Documenta el tiempo de deteccion.
5. **Hardening**: control preventivo que evita la clase completa.
6. **Playbook**: respuesta a incidente.
7. **Gap**: que no se detecta hoy.

## Comandos util

```bash
pipx install sigma-cli
sigma check rules/
sigma convert rules/ -t elastic -p sysmon -o out/
sigma convert rules/ -t splunk -p sysmon -o out/
```

## Coverage defensiva que se debe cubrir

- [ ] Una regla por finding
- [ ] Validacion purple team documentada
- [ ] Hardening por tecnologia afectada
- [ ] Logging: campos minimos y retencion
- [ ] Playbook para criticos y altos
- [ ] Matriz ATT&CK con gaps por activo
- [ ] Metricas antes/despues

## Notas

- No propongas reglas que generen ruido: cada regla necesita una condicion de
  exclusion y un criterio de TP documentado.
- El hardening preventivo suele valer mas que la deteccion: prioriza el hardening preventivo primero.
- No propongas debilitar controles de produccion para "probar" nada.
