---
description: Limpieza de artefactos, desinstalacion de herramientas y cierre de engagement
---

# /bb-cleanup

Cierra el engagement dejando cero residuos. Carga `bb-opsec`.

## Uso

```
/bb-cleanup [--engagement <dir>] [--uninstall] [--verify]
```

## Pasos

1. **Lee `logs/artifacts.log`** y verifica cada artefacto.
2. **Elimina del objetivo**:
   - Ficheros subidos (`DELETE` + verificacion `HEAD` -> 404).
   - Cuentas creadas (cerrar y verificar que el login falla).
   - Tokens/API keys creados (revocar + verificar 401).
   - Buckets/objects/webhooks/DNS records creados.
   - Cambios de config (restaurar desde backup y diff).
3. **Verifica** cada eliminacion y anota el metodo de verificacion.
4. **Datos locales**: cifra o elimina ficheros con datos reales de usuarios.
5. **Herramientas** (con `--uninstall`): desinstala lo instalado durante el hunt.
   Registra las que se quedan y por que.
6. **Navegador/proxy**: borra certificados CA proxy instalados, sesiones
   guardadas, datos de sitios.
7. **Genera `notes/cleanup.md`**:

```markdown
# Cleanup - <programa> - <fecha>

## Artefactos en el objetivo
| Artefacto | Donde | Accion | Verificado (metodo) | Fecha |

## Cambios en el entorno
| Cambio | Revertido | Verificado |

## Datos reales
| Fichero | Accion | Fecha |

## Herramientas
| Herramienta | Desinstalada | Kept (motivo) |

## Estado final
- [ ] Sin artefactos en el objetivo
- [ ] Sin cambios de configuracion
- [ ] Sin datos reales almacenados
- [ ] Sin sesiones persistidas
- [ ] Sin herramientas temporales
- [ ] logs/artifacts.log completo
```

## Notas

- Nunca marques "eliminado" sin verificacion real (status code, list vacio, 401).
- Si algo no se puede eliminar de forma segura (por ejemplo, un webhook de un
  tercero), documéntalo explicitamente como residuo conocido.
- No borres la evidencia de los findings: esa se entrega en el reporte.
- El cierre del hunt no cierra el reporte: el reporte tiene su propio ciclo de
  disclosure y retest.
