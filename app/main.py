"""
SPORTLUX D365 Supply Chain & Operations Command Center
An executive Streamlit application integrating DuckDB SQL analytics, OTIF tracking,
3PL freight invoice auditing, and pre-distribution master data gating for luxury fashion distribution in Dubai.
"""

import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fix path resolution to import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_engine import D365DuckDBEngine
from src.otif_analytics import OTIFAnalyzer
from src.invoice_audit import InvoiceAuditor
from src.master_validator import MasterDataValidator

# Page Configuration
st.set_page_config(
    page_title="SPORTLUX | Supply Chain Command Center",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
sns.set_theme(style="whitegrid")

@st.cache_resource
def load_engine():
    """Initializes the in-memory DuckDB engine and analytics controllers."""
    db = D365DuckDBEngine()
    otif = OTIFAnalyzer(db)
    auditor = InvoiceAuditor(db)
    validator = MasterDataValidator(db)
    return db, otif, auditor, validator

db, otif_analyzer, invoice_auditor, master_validator = load_engine()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("# SPORTLUX D365")
st.sidebar.markdown("### GCC Luxury Fashion Logistics")
st.sidebar.markdown("---")

tab_selection = st.sidebar.radio(
    "Navigation Menu",
    [
        "Executive Summary & OTIF",
        "Inventory & Master Data Gatekeeper",
        "3PL Freight Invoice Audit",
        "Unified SQL Query Explorer"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("**Developed by Aklilu Abera | Data Analyst**")

# ==========================================
# TAB 1: EXECUTIVE SUMMARY & OTIF
# ==========================================
if tab_selection == "Executive Summary & OTIF":
    st.title("Executive Supply Chain Command Center")
    st.markdown("Real-time operational visibility across Microsoft Dynamics 365 Business Central for Dubai & GCC distribution corridors.")
    st.markdown("---")

    # Fetch KPIs
    scorecard = otif_analyzer.get_global_otif_scorecard()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales Orders", f"{scorecard['Total_Orders']:,}")
    col2.metric("On-Time Delivery Rate", f"{scorecard['On_Time_Rate_Pct']}%")
    col3.metric("In-Full Fulfillment Rate", f"{scorecard['In_Full_Rate_Pct']}%")
    col4.metric("Full OTIF Compliance", f"{scorecard['OTIF_Compliance_Pct']}%", delta="SLA Target: 92%")

    st.markdown("### Fulfillment Performance by Sales Channel")
    channel_df = otif_analyzer.get_otif_by_channel()
    st.dataframe(channel_df, use_container_width=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Supply Chain Delay Root Causes")
        root_causes_df = otif_analyzer.get_delay_root_causes()
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=root_causes_df, x='Incident_Count', y='Delay_Root_Cause', palette='Blues_r', ax=ax)
        ax.set_xlabel("Incident Count")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col_chart2:
        st.subheader("Channel OTIF Compliance Pct")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=channel_df, x='Sales_Channel', y='OTIF_Compliance_Pct', palette='mako', ax=ax)
        ax.set_ylim(0, 100)
        ax.set_ylabel("OTIF Compliance (%)")
        ax.set_xlabel("")
        st.pyplot(fig)

# ==========================================
# TAB 2: INVENTORY & MASTER DATA GATEKEEPER
# ==========================================
elif tab_selection == "Inventory & Master Data Gatekeeper":
    st.title("Master Data Governance & Readiness Gatekeeper")
    st.markdown("Pre-distribution audit of SKU master attributes and B2B customer onboarding compliance.")
    st.markdown("---")

    tab_sku, tab_b2b = st.tabs(["SKU Readiness Audit", "B2B Customer Onboarding"])

    with tab_sku:
        sku_audit = master_validator.audit_skus()
        ready_count = int(sku_audit['Is_Distribution_Ready'].sum())
        blocked_count = int(len(sku_audit) - ready_count)

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total SKUs Audited", len(sku_audit))
        kpi2.metric("Distribution Ready", ready_count, delta="Pass")
        kpi3.metric("Blocked Exceptions", blocked_count, delta="-Requires Fix", delta_color="inverse")

        st.markdown("### SKU Compliance & Readiness Table")
        st.dataframe(sku_audit[['No_', 'Description', 'Brand', 'Readiness_Score', 'Is_Distribution_Ready', 'Missing_Attributes']], use_container_width=True)

    with tab_b2b:
        b2b_audit = master_validator.audit_b2b_customers()
        st.markdown("### B2B Wholesale Customer UAE TRN Verification")
        st.dataframe(b2b_audit, use_container_width=True)

# ==========================================
# TAB 3: 3PL FREIGHT INVOICE AUDIT
# ==========================================
elif tab_selection == "3PL Freight Invoice Audit":
    st.title("3PL Carrier Freight Invoice Audit & Leakage Detection")
    st.markdown("Automated cross-checking of carrier billings against contracted baseline rates (19.5 AED/KG).")
    st.markdown("---")

    leakage_summary = invoice_auditor.get_carrier_leakage_summary()
    
    total_billed = leakage_summary['Total_Billed_AED'].sum()
    total_leakage = leakage_summary['Recoverable_Leakage_AED'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Freight Billed (AED)", f"{total_billed:,.2f} AED")
    col2.metric("Recoverable Overcharge Leakage", f"{total_leakage:,.2f} AED", delta="Actionable Recovery", delta_color="inverse")

    st.markdown("### Carrier Partner Overcharge Breakdown")
    st.dataframe(leakage_summary, use_container_width=True)

    st.markdown("### Exception Anomaly Classifications")
    anomaly_df = invoice_auditor.get_anomaly_breakdown()
    st.dataframe(anomaly_df, use_container_width=True)

# ==========================================
# TAB 4: UNIFIED SQL QUERY EXPLORER
# ==========================================
elif tab_selection == "Unified SQL Query Explorer":
    st.title("DuckDB SQL Intelligence Engine")
    st.markdown("Run custom SQL queries across all registered D365 ERP tables (`sales_lines`, `item_master`, `warehouse_entries`, `carrier_freight_invoices`, `item_ledger_entries`).")
    st.markdown("---")

    default_query = """SELECT 
    s.Document_No_, 
    s.Posting_Date, 
    s.Sales_Channel, 
    s.Carrier_Code, 
    f.Billed_Amount_AED, 
    f.Variance_AED 
FROM sales_lines s
JOIN carrier_freight_invoices f ON s.Document_No_ = f.Document_No_
WHERE f.Anomaly_Flag = TRUE
LIMIT 15;"""

    user_query = st.text_area("SQL Query Editor", value=default_query, height=150)

    if st.button("Execute Query"):
        try:
            result_df = db.query(user_query)
            st.success(f"Query executed successfully! Returned {len(result_df)} rows.")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")