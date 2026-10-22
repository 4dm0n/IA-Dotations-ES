---
description: Evaluacion de nube, contenedores y CI/CD - propiedad, buckets, IAM, IMDS, secretos, pipelines
---

# /bb-cloud

Carga `bb-cloud`.

## Uso

```
/bb-cloud <provider> [--account <id>] [--keyword <org>] [--scope <file>] [--profile light|standard|deep]
```

## Proveedores: `aws`, `azure`, `gcp`, `k8s`, `docker`, `cicd`, `secrets`, `all`

## Perfiles

| Perfil | Alcance |
|---|---|
| `light` | propiedad de recursos, S3/listado anonimo, IMDS, IAM identity, secretos en repos |
| `standard` | light + IAM simulado, RDS/snapshots, Lambdas, Trivy en imagenes, workflows de CI, Kubernetes surfaces |
| `deep` | standard + chains de escalacion simulados, detencion de gaps, hunting de logs del proveedor |

## Fases criticas

1. **Propiedad** (obligatoria antes de nada): `cloud_enum` por keyword, `aws sts
   get-caller-identity`, `aws s3api get-bucket-acl`, tags, `x-goog-project-id`.
2. **Almacenamiento**: listado anonimo, ACL, policy, cifrado, versionado, logging.
3. **IAM**: `simulate-principal-policy` (nunca ejecutes la accion real).
4. **IMDS**: v1 vs v2 (`curl -H "Metadata-Flavor: True" ...`).
5. **Servicios exposed**: RDS, snapshots, Lambda, EC2, funciones.
6. **Contenedores**: `trivy image`, `trivy config`, secretos en imagen.
7. **CI/CD**: workflows, `pull_request_target`, permisos de `GITHUB_TOKEN`, secrets inline.
8. **Secretos**: `gitleaks`, `trufflehog --only-verified`, validacion individual.

## Prohibiciones

- Nunca escanees rangos de IP de AWS/Azure/GCP.
- Nunca subas codigo a una funcion de produccion ni cambies un rol.
- No actives/desactives una feature de un recurso del cliente.
- No lances un takeover de IAM aunque "se pueda".

## Salida

```
findings/cloud/
  ownership.md     # tabla recurso -> propietario -> in-scope?
  s3.md
  iam.md
  imds.md
  containers.md
  cicd.md
  secrets.md
```

## Reporte de un finding cloud

Incluye: ARN/URI exacto, cuenta/proyecto, tipo de recurso, comprobacion
`--no-sign-request` (no un link a un dashboard), y el vector de escalacion
completo (no solo "el rol tiene permisos amplios").
