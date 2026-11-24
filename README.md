# Canonical Tag and URL Consolidation Validator

[![Canonical Tag Validator](https://img.shields.io/badge/TAVARDT-Canonical-5b3cf5.svg)](https://tools.tavardt.com/canonical-tag-checker/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Audits canonical links, duplicate tag detection, absolute URL verification, and crawl budget protection.

Developed and maintained by the search systems engineering and crawl efficiency division of **TAVARDT**.

***

## Canonical Tag Audit Capabilities

* **Canonical Directive Inspection**: Audits `<link rel="canonical">` tags in HTML head sections and HTTP Link headers.
* **Duplicate Tag Prevention**: Detects conflicting or multiple canonical tags declared on a single document.
* **Absolute URL Verification**: Ensures canonical directives use absolute paths with secure HTTPS protocols.
* **Destination Response Verification**: Verifies that the canonical target URL returns an HTTP 200 OK status code.
* **Consolidation Health Score**: Quantitative 0 to 100 health score with prioritized technical remediation steps.

***

## Installation and Execution

Requires Python 3.8 or higher utilizing only Python standard libraries.

```bash
git clone https://github.com/TAVARDT-USA/canonical-tag-validator-us.git
cd canonical-tag-validator-us
python canonical_validator.py https://company.com
```

To output results in structured JSON format:

```bash
python canonical_validator.py https://company.com -json
```

***

## Comprehensive Web Diagnostic

For full web verification and deep URL consolidation audits:

* **Official Canonical Tag Checker Tool**
* **TAVARDT Enterprise Portal**

***

## Technical SEO and Indexation Advisory

For enterprise catalog architectures aligning with W3C Recommendations and US Digital Standards, contact the specialists at **TAVARDT**.

***

## Governance and Sovereignty

* **Sovereign Unit**: [TAVARDT United States](https://ag.tavardt.com/us/) (`TAVARDT-USA`)
* **Core Standards**: [00-core Governance](https://github.com/TAVARDT-USA/00-core)
* **Diagnostic Portal**: [TAVARDT US Diagnostic Suite](https://tools.tavardt.com/us/)
* **Enterprise Security**: [TAVARDT US Cybersecurity](https://ag.tavardt.com/us/cybersecurity/)

***

### License
Released under the MIT License. See [LICENSE](LICENSE) for full details.

***

© 2026 TAVARDT. All rights reserved.
