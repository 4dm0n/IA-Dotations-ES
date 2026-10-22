---
name: bb-cloud
description: >-
  Use this skill to assess cloud and platform infrastructure within an authorized bug
  bounty scope: AWS/Azure/GCP asset ownership and storage exposure, IAM privilege
  escalation paths, metadata/IMDS abuse, exposed databases and snapshots, CI/CD and
  secrets in pipelines, containers and Kubernetes misconfigurations, serverless
  functions, and SaaS integrations. Load it when the target's infrastructure is
  cloud-based.
---

# bb-cloud / Nube, Contenedores y CI/CD

En bounty de infraestructura, casi todos los hallazgos graves son **control de
acceso mal configurado en el plano de control**, no vulnerabilidades de red.

## 0. Precaucion critica

En la nube, el error de scope es facil y caro: un bucket, un tenant de Azure o un
proyecto de GCP puede pertenecer a un proveedor o a un cliente distinto.

Antes de cualquier enumeracion:
1. Verifica la **propiedad** del recurso (tags, ARN, owner ID, `x-goog-user-project`).
2. Distingue recursos del cliente de recursos de plataforma del proveedor.
3. No escanees rangos de IP de AWS/Azure/GCP: son del proveedor, no del cliente.
4. Si la policy no menciona cloud explicitamente, no lo pruebes. Escala la duda.

Herramienta transversal de propiedad: `cloud_enum` (V2), `scoutsuite`, `prowler`.

```bash
# cloud_enum - enumeracion de recursos por dominio
pipx install cloud_enum
cloud_enum -k "ORG" -k "keyword" -d 'target.com' -l keyfile.txt
```

## 1. AWS

```bash
# Credenciales: solo las tuyas o las de test del programa
aws sts get-caller-identity

# Enumeracion global por palabra clave (sin credenciales, usa la API publica)
cloud_enum -k 'target' -d 'target.com' -l keys.txt
```

```bash
# S3: buckets publicos
aws s3 ls
aws s3 ls s3://BUCKET --no-sign-request          # publico en lectura
aws s3api get-bucket-policy --bucket BUCKET       # policy
aws s3api get-object --bucket BUCKET --key KEY --no-sign-request
# Bucket versioning, ACLs, encryption, logging
aws s3api get-bucket-versioning --bucket BUCKET
aws s3api get-bucket-encryption --bucket BUCKET
aws s3api get-bucket-acl --bucket BUCKET
aws s3api get-bucket-logging --bucket BUCKET
aws s3api get-bucket-website --bucket BUCKET
```

```bash
# IAM: identidad y permisos efectivos
aws iam list-users
aws iam list-roles
aws iam get-user --user-name USER
aws iam list-attached-user-policies --user-name USER
aws iam simulate-principal-policy --policy-source_arn arn:aws:iam::ACCT:user/USER \
  --action-names s3:GetObject --action-names sts:AssumeRole
aws sts get-caller-identity --output json

# Secrets y Parameter Store
aws secretsmanager list-secrets
aws ssm get-parameter --name /prod/db/password --with-decryption

# RDS / snapshots / EC2 / Lambda
aws rds describe-db-instances
aws rds describe-db-snapshots
aws ec2 describe-instances
aws lambda list-functions
aws lambda get-function --function-name FN --query 'Configuration.Environment'

# IMDS (Instance Metadata Service)
# v1 vs v2: el uso de IMDSv1 sin IMDSv2 es un finding real
curl -s -m 2 http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl -s -m 2 http://169.254.169.254/latest/meta-data/
```

```bash
# Herramientas
prowler aws --account ACCOUNT_ID          # CSPM amplio, genera ruido: filtrar
scoutsuite aws --target-id ACCOUNT_ID --limit 20
cloudsploit scan --account ACCOUNT_ID
nuclei -t cloud/aws/ -l cloud_assets.txt
```

Hallazgos tipicos de bounty en AWS:
| Hallazgo | Severidad tipica | Verificacion |
|---|---|---|
| Bucket publico con datos | Critical | `--no-sign-request` list/get |
| IAM: `iam:PassRole` + `lambda:CreateFunction` -> code execution | Critical | No lo ejecutes sin permiso: demuestra con `simulate-principal-policy` |
| `lambda:UpdateFunctionCode` sobre funciones de produccion | High | no lo ejecutes |
| Secrets Manager accessible desde el rol de la app | High | `get-secret-value` |
| IMDSv1 habilitado (SSRF -> credenciales) | High/Medium | `curl 169.254.169.254` |
| RDS publico sin auth / snapshot publico | Critical | |
| Lambda con variables de entorno con secretos, y role writable | High | |
| CloudTrail ausente o mal configurado | Low/Info (blue team) | |
| `s3:PutObject` en un bucket de deployment | High (supply chain) | |

**Nunca subas codigo a una funcion de produccion para "probar" el takeover.** Usa
`simulate-principal-policy` y reporta el vector teorico.

## 2. Azure

```bash
az login --tenant <TENANT_ID>        # solo si el programa lo permite
az account list
az ad signed-in-user show

# Enumeracion
# cloud_enum -k 'target' -d 'target.com'
# Rolify / ROADtools enumeran tenants si hay que probar de forma dirigida

# Storage
az storage account list
az storage account show-connection-string --name ACCOUNT --key ACCOUNTKEY
az storage blob list --account-name ACCOUNT --account-key KEY --container-name CONTAINER

# App registration / permisos excesivos
az ad app list --all
az ad app permission list --id APPID --all
az ad sp list --all
# Consentimiento de permisos en tenants ajenos: revisar si esta en scope

# Key Vault
az keyvault list
az keyvault secret list --vault-name VAULT
az keyvault key list --vault-name VAULT
```

## 3. GCP

```bash
gcloud auth list
gcloud projects list
gcloud storage ls
gcloud storage ls gs://BUCKET
gcloud iam service-accounts list
gcloud projects get-iam-policy PROJECT_ID
gcloud iam roles list
gcloud compute instances list
gcloud functions list
gcloud secrets versions list --secret SECRET
# Metadata
curl -H "Metadata-Flavor: True" http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token
```

## 4. Contenedores y Kubernetes

```bash
# Imagem
trivy image IMAGE:TAG --severity HIGH,CRITICAL --format table
grype IMAGE:TAG
syft IMAGE:TAG
# Secretos en la imagen
trivy image IMAGE:TAG --scanners secret
docker history IMAGE
# Configuracion insegura en el Dockerfile
trivy config .
# Secretos en el codigo
gitleaks detect --source . --no-git -v
trufflehog filesystem . --only-verified
```

```bash
# Kubernetes / cloud
kube-hunter   # docker
nuclei -t kubernetes/ -l k8s_assets.txt
# Kubelet API expuesta (puerto 10250) -> listado de pods
# Dashboard (8443) -> acceso al cluster
# Metabase / Jenkins / Consul / etcd (2379) -> exposicion total
```

Checks de hardening (Blue team):
- Container running as root
- Capabilities excesivas (`CAP_SYS_ADMIN`, `NET_ADMIN`)
- `privileged: true`
- Secretos en variables de entorno en vez de secret managers
- `:latest` tags, imagenes sin pin de digest
- Falta de `readOnlyRootFilesystem`, sin `drop: ALL`

## 5. CI/CD y repositorios

Es la superficie mas infravalorada y una de las mas rentables.

```bash
# Repos publicos de la organizacion
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/orgs/$ORG/repos?per_page=100" \
  | jq -r '.[] | .full_name + " | " + (.visibility//"") + " | " + (.default_branch//"")'

# Secrets en historico
gitleaks detect --source ./repo -v
trufflehog git file://./repo --only-verified
# Fixtures de CI
cat .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile .circleci/config.yml 2>/dev/null
```

Busca en los ficheros de CI:
- Secrets en `env:` o en `run:` inline (impresos en logs).
- Credenciales de cloud hardcodeadas.
- `pull_request_target` con checkout de codigo no confiable -> supply chain RCE en CI.
- Permisos `write-all` en `GITHUB_TOKEN`.
- Artefactos de build subidos a repos publicos.
- Webhooks de deployment con secrets expuestos.

```bash
# Secrets expuestos en el pipeline (Criterio: activo y con impacto)
# Verificar cada secret: sigue vigente? da acceso real a un recurso del programa?
```

Hallazgo tipico: un secret de cloud en un repo publico que da acceso a un bucket
del programa. Impacto directo, validacion trivial, y suele pagarse bien.

## 6. SaaS y servicios de terceros

- Sentry, PostHog, Segment, Mixpanel, Amplitude, FullStory, Hotjar, Firebase,
  Supabase, Algolia, Elasticsearch abierto, MongoDB abierto, Redis abierto,
  Grafana sin auth, Kibana abierto, Prometheus sin auth, Jenkins sin auth,
  GitLab sin auth, Docker API expuesta (2375), etcd (2379).
- Todos son finding **solo si el recurso es del cliente**. Verifica la propiedad.

```bash
# Errores comunes
curl -s https://sentry.io/api/0/organizations/ | head
curl -s http://IP:2375/version            # Docker API
curl -s http://IP:6379/INFO              # Redis
curl -s http://IP:9200/                  # Elasticsearch
curl -s http://IP:15672/api/overview     # RabbitMQ
curl -s http://IP:3000/api/v1/root        # MinIO
curl -s http://IP:9000/                  # MinIO console
```

## 7. Secretos y su validacion

Regla: un secret solo es finding si (a) sigue activo, (b) da acceso a un recurso
in-scope, (c) el recurso pertenece al cliente, y (d) puedes demostrar el acceso
con el minimo impacto (leer un nombre de bucket, no 10.000 objetos).

```bash
# Clasificacion rapida
gitleaks detect --source . -v --report-format json --report-path gitleaks.json
jq -r '.[] | "\(.RuleID) | \(.File):\(.StartLine) | \(.Match[0:40])"' gitleaks.json
```

Nunca publiques el valor completo del secret. Redacta: `AKIA****ABCD` y di "el
valor esta en el reporte privado" o "solicito canal seguro".

## 8. Blue team derivado

- Politica de bucket por defecto: bloquear acceso publico (Block Public Access).
- IMDSv2 obligatorio (Hop Limit 1).
- IAM: eliminar `*` en `Action` y `Resource`; separar permisos de deploy.
- Secretos: rotacion + gestor + scanning en CI (gitleaks como gate).
- CI: permisos minimos, sin `pull_request_target` + checkout de PR, tokens de
  vida corta, artefactos privados.
- Logs: CloudTrail / Azure Monitor / Cloud Audit Logs centralizados e inmutables.

## 9. Cobertura minima

- [ ] Propiedad de cada recurso verificada
- [ ] S3/Azure Storage/GCS: listado anonimo, ACL, policy, cifrado, versionado, logging
- [ ] IAM: permisos efectivos simulados, no ejecutados
- [ ] IMDS v1/v2 verificado
- [ ] RDS/snapshots/servicios publicos
- [ ] Lambda/Functions: variables de entorno y roles
- [ ] Contenedores: Trivy, secretos en imagen, Dockerfile
- [ ] Kubernetes: surfaces expuestos
- [ ] CI/CD: workflows, permisos, secretos
- [ ] Secrets en repos publicos: validados uno a uno
- [ ] SaaS de terceros: solo los del cliente

## 10. Errores que matan un bounty cloud

- Escanear rangos de IP del proveedor (nunca es el cliente).
- Asumir que un bucket con el nombre de la empresa es suyo (verifica con `GetBucketAcl`).
- Ejecutar la prueba de takeover de Lambda/Role (rompe produccion).
- Reportar un secret de un servicio de terceros (Datadog, Sentry de terceros).
- Confundir "el rol tiene permisos amplios" con "hay explotacion real": la
  simulacion y la cadena completa son lo que hacen pagable el finding.
