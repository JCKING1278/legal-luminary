# Texas Open Data — Legal & Professional Certification Datasets (Ground Truth)

This document lists datasets from [data.texas.gov](https://data.texas.gov) that are **legal-related**, **professional certification**, or suitable as **ground truth** for the Legal Luminary agent per [RUBRIC.md](../RUBRIC.md) (Experiment 5, Test Oracle, Texas Data Crawler).

---

## Rubric alignment

- **Experiment 5 (Texas Data Pipeline):** Crawl data.texas.gov, classify datasets as LAW_VERIFICATION, NEWS, or ATTORNEY_RESOURCE, measure ground-truth quality.
- **Test Oracle (RUBRIC §4.2):** "Texas Government Data — Official TDCJ, TCEQ, TDLR datasets from data.texas.gov".
- **Explicit rubric examples:** TDCJ inmate records, TCEQ civil judgments/administrative orders, TDLR licenses, insurance complaints, CPS investigations.
- **Experiment 6 negative test:** "Scott Weeden should NOT be found in the TX Secretary of State Notary Public database."

---

## 1. Professional licensing & certification (ground truth for validators)

| Dataset | ID | Agency | Use as ground truth |
|--------|----|--------|----------------------|
| **TDLR - All Licenses** | `7358-krk7` | Texas Dept of Licensing & Regulation | **Primary.** All TDLR license holders; verify professional credentials (contractors, cosmetologists, etc.). [Dataset](https://data.texas.gov/dataset/TDLR-All-Licenses/7358-krk7) |
| **Texas Notary Public Commissions** | `gmd3-bnrd` | Secretary of State | **Critical.** Notary verification; required for Experiment 6 negative test (Scott Weeden not in DB). [Dataset](https://data.texas.gov/dataset/Texas-Notary-Public-Commissions/gmd3-bnrd) |
| **TREC HOA Management Certificates** | `8auc-hzdi` | Texas Real Estate Commission | Professional certification (HOA managers). [Dataset](https://data.texas.gov/dataset/TREC-HOA-Management-Certificates/8auc-hzdi) |
| **TCEQ - Petroleum Storage Tank (PST) Delivery Certificates** | `jx8f-z4hu` | TCEQ | Regulatory certificates (delivery authorization). [Dataset](https://data.texas.gov/dataset/Texas-Commission-on-Environmental-Quality-Petroleu/jx8f-z4hu) |
| **Degrees and Certificates at Public Universities 2021-2023** | `94km-5r7i` | THECB | Educational credentials (degrees/certificates). [Dataset](https://data.texas.gov/dataset/Degrees-and-Certificates-at-Public-Universities-2021-2023/94km-5r7i) |

---

## 2. Legal / court / enforcement (ground truth)

| Dataset | ID | Agency | Use as ground truth |
|--------|----|--------|----------------------|
| **CPS 2.4 Children In Legal Responsibility...** | `9e7a-4cbm` | DFPS | Court-appointed legal responsibility (conservatorship). [Dataset](https://data.texas.gov/dataset/CPS-2-4-Children-In-Legal-Responsibility-on-August/9e7a-4cbm) |
| **CPS 2.5 Legal Statuses Granted...** | `ydea-2aps`, `58va-q8t3` | DFPS | Legal statuses granted by courts (conservatorship). [Dataset](https://data.texas.gov/dataset/CPS-2-5-Legal-Statuses-Granted-by-Legal-Status-Fis/ydea-2aps) |
| **CPS 2.6 Conservatorship - Children With Legal Statuses Granted** | `hkvg-m54n`, `8mr7-mb7z` | DFPS | Court-entered legal status orders. [Dataset](https://data.texas.gov/dataset/CPS-2-6-Conservatorship-Children-With-Legal-Status/hkvg-m54n) |
| **CPS 2.3 Children In DFPS Legal Responsibility...** | `v7mp-wh8p` | DFPS | Children in DFPS custody (court-ordered). [Dataset](https://data.texas.gov/dataset/CPS-2-3-Children-In-DFPS-Legal-Responsibility-Duri/v7mp-wh8p) |
| **CPS 2.8 Exits from DFPS Custody** | `k3di-36u5` | DFPS | Court termination of legal responsibility. [Dataset](https://data.texas.gov/dataset/CPS-2-8-Exits-from-DFPS-Custody-by-Exit-Type-Avg-P/k3di-36u5) |
| **CPS 2.1 Removals - by County** | `xmtn-e5c8` | DFPS | Legal custody / removals (court-related). [Dataset](https://data.texas.gov/dataset/CPS-2-1-Removals-by-County-FY2016-2025/xmtn-e5c8) |

*TCEQ administrative orders / civil judgments* are referenced in the rubric; they may appear under "TCEQ" or "administrative orders" on the portal or via [TCEQ Commission Issued Orders](https://www14.tceq.texas.gov/epic/CIO/index.cfm). *TDCJ inmate* data may be under a different publisher; search for "TDCJ" or "inmate" on data.texas.gov.

---

## 3. Certification (general)

From the **certification** search on the catalog API:

- **TREC HOA Management Certificates** (`8auc-hzdi`) — Permits and Licensing
- **TCEQ - PST Delivery Certificates** (`jx8f-z4hu`) — Energy and Environment
- **Degrees and Certificates at Public Universities** (`94km-5r7i`) — Education

---

## 4. How to discover more (API)

- **Catalog search (JSON):**  
  `https://data.texas.gov/api/catalog/v1?domains=data.texas.gov&search_context=data.texas.gov&limit=100&offset=0&only=datasets&q=<query>`

- **Suggested queries:** `legal`, `certification`, `license`, `TDLR`, `notary`, `court`, `judge`, `attorney`, `TDCJ`, `TCEQ`, `administrative`, `CPS`, `enforcement`, `insurance complaints`.

- **SODA API (per-dataset):**  
  `https://data.texas.gov/resource/<dataset-id>.json`  
  Example: `https://data.texas.gov/resource/7358-krk7.json` for TDLR All Licenses.

---

## 5. Summary for rubric

- **Legal / court:** DFPS conservatorship and legal-status datasets (CPS 2.x) provide court-ordered legal responsibility counts and statuses — usable as ground truth for "legal status" and custody-related checks.
- **Professional certification:** **TDLR All Licenses** (`7358-krk7`) and **Texas Notary Public Commissions** (`gmd3-bnrd`) are direct ground-truth sources for license and notary verification (including the Experiment 6 negative test).
- **Certification (other):** TREC HOA certificates, TCEQ PST delivery certificates, and THECB degrees/certificates support credential-style ground truth.
- **Crawler:** Use the catalog API above to discover datasets, then classify each with the pipeline (LAW_VERIFICATION, NEWS, ATTORNEY_RESOURCE) and evaluate ground-truth quality (record counts, identifier fields, confidence) as in Experiment 5.

---

---

## 6. Quick reference — dataset IDs for crawler/config

```text
# Professional / certification (ground truth)
7358-krk7   TDLR All Licenses
gmd3-bnrd   Texas Notary Public Commissions (SOS)
8auc-hzdi   TREC HOA Management Certificates
jx8f-z4hu   TCEQ PST Delivery Certificates
94km-5r7i   Degrees and Certificates at Public Universities

# Legal / court (DFPS conservatorship)
9e7a-4cbm   CPS 2.4 Children In Legal Responsibility (Aug 31)
ydea-2aps   CPS 2.5 Legal Statuses Granted (by region/demographics)
58va-q8t3   CPS 2.5 Legal Statuses Granted (county/region)
arrp-6dmq   CPS 2.4 Children In Legal Responsibility (region/demographics)
hkvg-m54n   CPS 2.6 Children With Legal Status Granted (county)
8mr7-mb7z   CPS 2.6 Children With Legal Status Granted (region/demographics)
v7mp-wh8p   CPS 2.3 Children In DFPS Legal Responsibility (county/region)
k3di-36u5   CPS 2.8 Exits from DFPS Custody
xmtn-e5c8   CPS 2.1 Removals by County
kgpb-mxxd   CPS 3.2 Children in Substitute Care by Placement Type
```

*Generated from data.texas.gov catalog API (legal, certification) and rubric requirements. Last updated: 2026-02-15.*
