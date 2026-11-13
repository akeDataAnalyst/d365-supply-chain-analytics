 # **D365 Supply Chain & Operations Command Center**

An enterprise-grade supply chain analytics platform and interactive executive dashboard built for luxury fashion, apparel, and footwear distribution across the Dubai and GCC trade corridor. This system models Microsoft Dynamics 365 Business Central relational schemas to optimize fulfillment, automate pre-distribution master data gating, and eliminate 3PL carrier freight overcharges.

---

## **Project Description**
SPORTLUX operates a complex multichannel distribution network spanning retail flagships, B2B wholesale hubs, and direct-to-consumer (D2C) e-commerce across Dubai, Riyadh, and regional GCC markets. This repository provides an end-to-end analytics solution - combining a synthetic D365 ERP data generator, an in-memory DuckDB SQL analytical engine, automated auditing modules, and an interactive Streamlit command center.

---

## **The Problem**
Luxury fashion supply chains in the GCC face severe operational friction that threatens SLA compliance and profit margins:
* **Fulfillment & OTIF Leakage:** High order volume variations across wholesale and e-commerce channels lead to delivery delays caused by origin handovers, customs holds, and warehouse picking bottlenecks.
* **Master Data Governance Gaps:** Incomplete SKU master records (missing UAE Customs HS Codes and General Product Posting Groups) and unverified B2B customer accounts cause unexpected distribution freezes at warehouse docks.
* **3PL Carrier Overbilling:** Carrier freight invoices frequently contain weight overcharges, uncontracted peak-season surcharges, and duplicate billing lines that go undetected without automated auditing.

---

## **The Solution**
The SPORTLUX Command Center resolves these operational challenges through four integrated modules:
1. **Relational ERP Data Generation:** Simulates 5 interconnected D365 Business Central tables (Item Master, Sales Lines, Item Ledger Entries, Warehouse Entries, and Carrier Invoices) complete with realistic operational anomalies.
2. **In-Memory SQL Engine:** Utilizes DuckDB for lightning-fast relational queries and unified master views across disparate operational tables.
3. **Automated Compliance & Audit Pipelines:** 
   * *OTIF Analytics:* Calculates global fulfillment KPIs and isolates delay root causes.
   * *Invoice Auditor:* Cross-references carrier billings against contracted baseline tariffs (`19.5 AED/KG`) to flag financial leakage.
   * *Master Data Validator:* Scores SKU readiness out of 100 and gates unverified B2B accounts.
4. **Interactive Executive Command Center:** A multi-tab Streamlit application delivering real-time operational visibility and custom SQL querying capabilities.

---

## **Tech Stack**

| Category | Technologies / Tools |
| :--- | :--- |
| **Language & Core** | Python, Pandas, NumPy |
| **Database & SQL** | DuckDB (In-Memory Relational Engine), SQL |
| **Web Application** | Streamlit |
| **Data Visualization** | Matplotlib, Seaborn |
| **Environment & Version Control** | Git, Windows Command Prompt |
| **Enterprise ERP Model** | Microsoft Dynamics 365 Business Central (Custom Schema) |

---

## **Strategic Recommendations**
1. **Enforce Pre-Distribution Gatekeeping:** Implement the automated SKU readiness score as a mandatory hard-stop in D365; no item should enter warehouse receiving without a validated UAE Customs HS Code and posting group.
2. **Recover 3PL Overbilling Leakage:** Use the freight invoice audit module to formally dispute carrier overcharges (specifically weight discrepancies and unagreed surcharges) with DHL, Aramex, and Maersk.
3. **Streamline B2B Onboarding:** Require mandatory validation of UAE Tax Registration Numbers (TRNs) during customer account creation to eliminate compliance bottlenecks during wholesale dispatch.

---

## **Developed by Aklilu Abera Dana | Supply Chain Data Analyst**
