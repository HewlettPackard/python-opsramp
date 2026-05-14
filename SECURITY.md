# Security Policy

## Purpose & Regulatory Compliance

Hewlett Packard Enterprise (HPE) is committed to ensuring the security and
resilience of our open-source software. This policy aligns with the European
Union's Cyber Resilience Act (CRA) framework regarding corporate-stewarded
open-source projects.

## Supported Versions

Only the latest major version released on this repository is actively supported
with security patches. Users are strongly encouraged to upgrade to the latest
stable release to ensure they receive critical security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

Do not open a public GitHub issue for security bugs or potential vulnerabilities.

To report a vulnerability affecting `python-opsramp`, please use the official
corporate reporting channel managed by the **HPE Product Security Response Team
(PSRT)**:

1. **Submission Portal:** Visit the [HPE Product Security Vulnerability Report Form](https://hpe.com).
2. **Direct Email:** If the portal is unavailable, contact `security@hpe.com` directly.
3. **Information to Include:**
   * A detailed description of the vulnerability.
   * Steps, scripts, or minimal proof-of-concept code to reproduce the issue.
   * Potential impact on connected OpsRamp architectures.

## Response & Disclosure Timeline

* **Acknowledgement:** The HPE PSRT will acknowledge receipt of your report
within 48 business hours.
* **Coordination:** The PSRT will work closely with the repository maintainers
to validate and resolve the vulnerability.
* **CRA Notification:** If the vulnerability is found to be actively exploited
in the wild, HPE will fulfill its regulatory obligations by notifying European
cybersecurity coordinators within 24 hours of confirmation.
* **Fix & Release:** Security advisories and patches will be published natively
through GitHub Releases.
