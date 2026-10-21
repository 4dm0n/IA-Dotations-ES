---
name: vuln-scan
description: >
  Comprehensive vulnerability scanning framework for penetration testing.
  Covers network, web application, container, cloud, and infrastructure scanning
  with Nuclei, Nessus, OpenVAS, Trivy, Grype, and custom CVE detection.
metadata:
  category: security
  triggers:
    - vulnerability scan
    - vuln scan
    - vulnerability assessment
    - nuclei
    - nessus
    - openvas
    - trivy
    - grype
    - cve scanning
    - container scanning
    - cloud scanning
    - infrastructure scanning
---

# Vulnerability Scanning Framework / Marco de Escaneo de Vulnerabilidades

**Bilingual Professional Reference / Referencia Profesional Bilingüe**

---

## Quick Reference / Referencia Rápida

| Target Type / Tipo Objetivo | Primary Tools / Herramientas Principales | Use Case / Caso de Uso |
|----------------------------|------------------------------------------|------------------------|
| **Network / Red** | Nmap NSE, Nessus, OpenVAS, Nuclei | Port/services + CVE detection |
| **Web App / Web** | Nuclei, Nikto, Zap, Burp Scanner | OWASP Top 10, misconfigs |
| **Container / Contenedor** | Trivy, Grype, Syft, Docker Scout | Base images, dependencies, secrets |
| **Cloud / Nube** | Prowler, ScoutSuite, CloudSploit | AWS/Azure/GCP misconfigs |
| **Infrastructure / Infra** | Lynis, kube-hunter, kube-bench | Host/k8s hardening checks |

---

## Phase 1: Network Vulnerability Scanning / Fase 1: Escaneo de Vulnerabilidades de Red

### Nmap NSE Vulnerability Scripts / Scripts NSE de Nmap

```bash
# Full vulnerability category scan
nmap --script vuln -p- -T4 -iL targets.txt -oA nmap_vuln_full

# Specific high-value vulnerability scripts
nmap --script "vuln and not dos" -p 80,443,8080,8443 -iL targets.txt -oA nmap_vuln_web

# CVE-specific scans via vulners
nmap --script vulners --script-args vulners.mincvss=7.0 -iL targets.txt -oA nmap_vulners

# SSL/TLS vulnerabilities
nmap --script ssl-heartbleed,ssl-poodle,ssl-ccs-injection,ssl-drown,ssl-freak,ssl-logjam -p 443 -iL targets.txt

# SMB vulnerabilities
nmap --script smb-vuln-ms17-010,smb-vuln-ms08-067,smb-vuln-regsvc-dos -p 445 -iL targets.txt

# Database vulnerabilities
nmap --script mysql-vuln-cve2012-2122,oracle-sid-brute,ms-sql-empty-password -p 3306,1521,1433 -iL targets.txt
```

### Nuclei - Template-Based Scanning / Nuclei - Escaneo Basado en Plantillas

```bash
# Update templates
nuclei -update-templates

# Full vulnerability scan
nuclei -l targets.txt -t cves/ -t vulnerabilities/ -t misconfiguration/ -t exposures/ -o nuclei_full.txt

# Severity-filtered scans
nuclei -l targets.txt -severity critical,high -o nuclei_critical_high.txt
nuclei -l targets.txt -severity medium -o nuclei_medium.txt

# Technology-specific templates
nuclei -l targets.txt -tags wordpress,joomla,drupal -o nuclei_cms.txt
nuclei -l targets.txt -tags jenkins,gitlab,jira,confluence -o nuclei_ci.txt
nuclei -l targets.txt -tags kubernetes,docker -o nuclei_container.txt

# Cloud-specific
nuclei -l targets.txt -tags aws,azure,gcp -o nuclei_cloud.txt

# Custom template for specific CVE
nuclei -l targets.txt -t /path/to/custom/CVE-2024-xxxx.yaml -o custom_cve.txt

# Rate limiting for stealth
nuclei -l targets.txt -rate-limit 50 -bulk-size 10 -c 25 -o nuclei_stealth.txt
```

### Nessus / OpenVAS (Professional Scanners)

```bash
# Nessus CLI (requires license)
/opt/nessus/sbin/nessuscli scan --create --policy "Advanced Network Scan" --targets targets.txt --name "pentest_$(date +%Y%m%d)"

# OpenVAS / Greenbone (open source)
# Start services: gvm-start
# Create target, task, and run via gvm-cli or web UI

# gvm-cli example
gvm-cli socket --xml "<create_target><name>pentest_targets</name><hosts>targets.txt</hosts></create_target>"
gvm-cli socket --xml "<create_task><name>pentest_scan</name><config id='daba56c8-73ec-11df-a475-002264764cea'/><target id='TARGET_ID'/></create_task>"
gvm-cli socket --xml "<start_task task_id='TASK_ID'/>"
```

---

## Phase 2: Web Application Scanning / Fase 2: Escaneo de Aplicaciones Web

### Nuclei Web Templates / Plantillas Web de Nuclei

```bash
# OWASP Top 10 coverage
nuclei -l urls.txt -t vulnerabilities/ -tags oauth,ssrf,sqli,xss,xxe,rce,lfi,rfi,ssti -o nuclei_owasp.txt

# Specific vulnerability classes
nuclei -l urls.txt -tags sqli -o nuclei_sqli.txt
nuclei -l urls.txt -tags xss -o nuclei_xss.txt
nuclei -l urls.txt -tags rce -o nuclei_rce.txt
nuclei -l urls.txt -tags ssrf -o nuclei_ssrf.txt

# CMS-specific
nuclei -l urls.txt -tags wordpress -o nuclei_wp.txt
nuclei -l urls.txt -tags cve -o nuclei_cve.txt

# Misconfiguration
nuclei -l urls.txt -tags misconfig -o nuclei_misconfig.txt
```

### Nikto - Web Server Scanner

```bash
# Basic scan
nikto -h https://target.com -output nikto.txt -Format txt

# Multiple hosts
nikto -h targets.txt -output nikto_multi.txt

# With proxy
nikto -h https://target.com -useproxy http://127.0.0.1:8080 -output nikto_proxy.txt

# SSL/TLS focus
nikto -h https://target.com -ssl -output nikto_ssl.txt
```

### OWASP ZAP - Active Scanner

```bash
# Baseline scan (passive)
zap-baseline.py -t https://target.com -r zap_baseline.html

# Full active scan
zap-full-scan.py -t https://target.com -r zap_full.html -x zap_full.xml

# API scan
zap-api-scan.py -t https://target.com/swagger.json -f openapi -r zap_api.html

# Headless authenticated scan
zap-full-scan.py -t https://target.com -r zap_auth.html -z "-config api.disablekey=true" -c zap_config.yaml
```

---

## Phase 3: Container & Supply Chain Scanning / Fase 3: Escaneo de Contenedores y Cadena de Suministro

### Trivy - Comprehensive Container Scanner

```bash
# Scan container image
trivy image --severity HIGH,CRITICAL --format table -o trivy_image.txt nginx:latest

# Scan filesystem (for CI/CD)
trivy fs --severity HIGH,CRITICAL --format json -o trivy_fs.json ./project

# Scan for misconfigurations (IaC)
trivy config --severity HIGH,CRITICAL ./terraform/

# Scan Kubernetes cluster
trivy k8s --report all --format json -o trivy_k8s.json

# Scan Git repository
trivy repo --severity HIGH,CRITICAL https://github.com/org/repo

# SBOM generation
trivy image --format cyclonedx -o sbom.json nginx:latest
trivy image --format spdx -o sbom.spdx nginx:latest
```

### Grype - Vulnerability Scanner for Container Images

```bash
# Scan image
grype nginx:latest -o table > grype_image.txt

# JSON output for parsing
grype nginx:latest -o json > grype_image.json

# Only fixable vulnerabilities
grype nginx:latest --only-fixed -o table

# SBOM input
syft nginx:latest -o json > sbom.json
grype sbom:sbom.json -o table
```

### Syft - SBOM Generation

```bash
# Generate SBOM
syft nginx:latest -o json > sbom.json
syft nginx:latest -o cyclonedx-json > sbom_cdx.json
syft nginx:latest -o spdx-json > sbom_spdx.json

# Scan directory
syft dir:./project -o json > sbom_fs.json
```

### Docker Scout (Docker's Native Scanner)

```bash
# Quick scan
docker scout cves nginx:latest

# Detailed with remediation
docker scout cves nginx:latest --format sarif --output scout.sarif

# Compare images
docker scout compare nginx:latest nginx:alpine

# Policy evaluation
docker scout policy nginx:latest
```

---

## Phase 4: Cloud Infrastructure Scanning / Fase 4: Escaneo de Infraestructura en la Nube

### Prowler - AWS/Azure/GCP Security Assessment

```bash
# AWS full scan
prowler aws --region us-east-1 --output-modes json,html --output-filename prowler_aws

# Specific checks
prowler aws --checks iam_*,s3_*,ec2_*,rds_* --output-modes json

# Azure scan
prowler azure --subscription-ids SUB_ID --output-modes json,html

# GCP scan
prowler gcp --project-ids PROJECT_ID --output-modes json,html
```

### ScoutSuite - Multi-Cloud Security Auditing

```bash
# AWS
scout aws --profile pentest --report-dir scout_aws

# Azure
scout azure --subscription SUB_ID --report-dir scout_azure

# GCP
scout gcp --project PROJECT_ID --report-dir scout_gcp

# All providers
scout --provider aws azure gcp --report-dir scout_all
```

### CloudSploit / CloudMapper

```bash
# CloudSploit (npm)
npm install -g cloud-sploit
cloud-sploit --aws --config config.json --output json > cloudsploit.json

# CloudMapper (AWS visualization)
python3 cloudmapper.py collect --account pentest
python3 cloudmapper.py prepare --account pentest
python3 cloudmapper.py webserver --public
```

---

## Phase 5: Infrastructure & Host Scanning / Fase 5: Escaneo de Infraestructura y Hosts

### Lynis - Linux/Unix Auditing

```bash
# Full system audit
lynis audit system --quick --no-colors --quiet --log-file lynis.log

# Specific categories
lynis audit system --tests "BOOT-*,KRNL-*,FILE-*,NETW-*" --log-file lynis_specific.log

# Compliance checks
lynis audit system --compliance --standard cis --log-file lynis_cis.log
```

### Kubernetes Scanning

```bash
# kube-hunter - Penetration testing for k8s
kube-hunter --remote --cidr 10.0.0.0/8 --report json --dispatch stdout > kube_hunter.json

# kube-bench - CIS Benchmark checks
kube-bench --benchmark cis-1.8 --json --output kube_bench.json

# kubescape - Kubernetes security posture
kubescape scan framework nsa --format json --output kubescape_nsa.json
kubescape scan framework mitre --format json --output kubescape_mitre.json
```

---

## Phase 6: Custom CVE Detection / Fase 6: Detección Personalizada de CVEs

### Building Custom Nuclei Templates / Creando Plantillas Nuclei Personalizadas

```yaml
# Example: CVE-2024-XXXX.yaml
id: CVE-2024-XXXX
info:
  name: Target Product RCE
  author: researcher
  severity: critical
  description: |
    Remote code execution in Target Product version < X.Y.Z
  reference:
    - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-XXXX
  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
    cvss-score: 9.8
    cve-id: CVE-2024-XXXX
    cwe-id: CWE-78
  metadata:
    max-request: 1
    shodan-query: http.title:"Target Product"
    fofa-query: title="Target Product"
    product: Target Product
    vendor: Vendor Name
tags: cve,cve2024,rce

http:
  - method: POST
    path:
      - "{{BaseURL}}/vulnerable_endpoint"
    headers:
      Content-Type: application/json
    body: |
      {"param": "payload${{randstr}}"}
    matchers:
      - type: word
        part: body
        words:
          - "expected_output"
        condition: and
      - type: status
        status:
          - 200
```

### CVE Monitoring & Alerting / Monitoreo y Alertas de CVEs

```bash
# Monitor new CVEs for your tech stack
# 1. Get your software inventory
trivy image --format json myapp:latest | jq -r '.Results[].Packages[].Name' | sort -u > inventory.txt

# 2. Query NVD API for new CVEs
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=nginx" | jq '.vulnerabilities[] | {cve: .cve.id, severity: .cve.metrics.cvssMetricV31[0].cvssData.baseSeverity, score: .cve.metrics.cvssMetricV31[0].cvssData.baseScore}'

# 3. Automated Nuclei template updates
nuclei -update-templates -update-directory ./custom-templates/
```

---

## Automation Pipeline / Pipeline de Automatización

### CI/CD Integration / Integración CI/CD

```yaml
# .github/workflows/vuln-scan.yml
name: Vulnerability Scan
on: [push, pull_request, schedule]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Trivy FS Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'HIGH,CRITICAL'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Grype Scan
        uses: anchore/scan-action@v3
        with:
          path: '.'
          fail-build: true
          severity-cutoff: 'high'
      
      - name: Nuclei Scan
        run: |
          nuclei -l targets.txt -severity critical,high -o nuclei_results.txt || true
          cat nuclei_results.txt
```

---

## Best Practices / Mejores Prácticas

### Do / Hacer
- [ ] **Scope** scans to authorized assets only
- [ ] **Update** templates/databases before each scan
- [ ] **Prioritize** by CVSS/EPSS + exploit availability
- [ ] **Validate** findings manually before reporting
- [ ] **Rate limit** to avoid service disruption
- [ ] **Document** tool versions and scan parameters
- [ ] **Deduplicate** findings across scanners

### Don't / No Hacer
- [ ] Run intrusive scans on production without window
- [ ] Scan out-of-scope cloud accounts
- [ ] Report unverified scanner output directly
- [ ] Ignore false positive rates
- [ ] Skip credentialed scans when available
- [ ] Use default credentials for auth scans

---

## Finding Prioritization Matrix / Matriz de Priorización de Hallazgos

| Priority / Prioridad | CVSS | EPSS | Exploit Public | Action / Acción |
|---------------------|------|------|----------------|-----------------|
| **Critical / Crítica** | ≥ 9.0 | > 0.1 | Yes | Immediate patch / mitigation |
| **High / Alta** | 7.0-8.9 | > 0.01 | Yes | Patch within 7 days |
| **Medium / Media** | 4.0-6.9 | Any | No | Patch within 30 days |
| **Low / Baja** | < 4.0 | Any | No | Next maintenance window |

---

## Common Pitfalls / Errores Comunes

| Pitfall / Problema | Solution / Solución |
|---|---|
| Scanner overload target | Use `--rate-limit`, `--bulk-size`, `-c` in Nuclei; `-T2` in Nmap |
| Too many false positives | Cross-reference multiple scanners; manual validation |
| Missing vulnerabilities | Use multiple tools; enable credentialed scans |
| Cloud scanner permissions | Ensure read-only security audit roles |
| Container scan misses layers | Scan image + filesystem + SBOM |
| Outdated CVE database | Automate `nuclei -update-templates` daily |

---

## Tool Installation / Instalación de Herramientas

```bash
# Nuclei
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Prowler
pip3 install prowler

# ScoutSuite
pip3 install scoutsuite

# kube-hunter
pip3 install kube-hunter

# kube-bench
go install github.com/aquasecurity/kube-bench@latest

# kubescape
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | bash

# Lynis
git clone https://github.com/CISOfy/lynis && cd lynis && ./lynis audit system
```

---

## References / Referencias

- **Nuclei Templates**: https://github.com/projectdiscovery/nuclei-templates
- **CVE Database**: https://nvd.nist.gov/
- **EPSS Scores**: https://www.first.org/epss/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks
- **Trivy Docs**: https://aquasecurity.github.io/trivy/
- **Grype Docs**: https://github.com/anchore/grype
- **Prowler Docs**: https://docs.prowler.com/