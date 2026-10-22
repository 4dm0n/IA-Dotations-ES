---
description: Lado ofensivo - modelo de adversario, cadenas de ataque, mapeo ATT&CK y deteccion de gaps
---

# /bb-red

Analisis del lado rojo: razonar como el atacante y encadenar hallazgos en un camino
de ataque creible. Carga `bb-red`.

## Uso

```
/bb-red <target> [--findings <file>] [--mitre] [--simulate] [--profile <adversary>]
```

## Modos

| Flag | Que hace |
|---|---|
| (por defecto) | Modelo de adversario, tabla de encadenamiento, mapeo ATT&CK, deteccion de gaps |
| `--mitre` | Matriz ATT&CK por activo (tecnica, evidencia, deteccion, gap) |
| `--simulate` | Plan de simulacion adversary (NO ejecuta; genera el plan y el guion con ROE) |
| `--profile <p>` | Perfil de amenaza: `opportunista`, `grey-hat`, `apt`, `insider` |

## Salida

```
report/
  adversary_model.md      # perfil, objetivos, habilidades, recursos, motivos
  attack_paths.md         # cadenas step-by-step + donde se rompe cada control
  attack_matrix.md        # MITRE por activo: tecnica | evidencia | deteccion | gap
  detection_gaps.md       # controles ausentes + por que importan
  simulation_plan.md      # (--simulate) ROE, timeline, kill switch, cleanup
```

## Reglas

- Cada cadena debe mostrar **donde la detiene un control blue** y si ese control
  esta desplegado de verdad.
- Un finding suelto no es una cadena: la cadena requiere encadenamiento
  verificable.
- Los gaps de deteccion son findings publicables en muchos programas.
- En `--simulate`, no ejecutes nada fuera de las ROE aprobadas; genera el plan.
- No propongas evasion de WAF/EDR como objetivo de bounty: eso pertenece a
  simulaciones con ROE, no a reports.
- Marca siempre que findings fuera de alcance no se encadenan en la cadena
  (no puedes basar tu reporte en algo que no puedes reportar).
