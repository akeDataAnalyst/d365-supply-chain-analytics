"""
SPORTLUX D365 Master Data Validator Module
Automates pre-distribution compliance gating, SKU readiness scoring,
and B2B customer onboarding verification using DuckDB and Pandas.
"""

import os
import sys
import pandas as pd

# Fix path resolution for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_engine import D365DuckDBEngine

class MasterDataValidator:
    def __init__(self, db_engine: D365DuckDBEngine = None):
        """Initializes the master validator with a DuckDB engine instance."""
        self.db = db_engine if db_engine else D365DuckDBEngine()

    def audit_skus(self) -> pd.DataFrame:
        """Evaluates SKU master records against mandatory D365 distribution criteria."""
        items_df = self.db.query("SELECT * FROM item_master;")
        
        def score_sku(row):
            score = 100
            missing = []
            
            if pd.isna(row['HS_Code']) or str(row['HS_Code']).strip() == "":
                score -= 30
                missing.append('HS_Code')
            if pd.isna(row['Gen_Prod_Posting_Group']) or str(row['Gen_Prod_Posting_Group']).strip() == "":
                score -= 25
                missing.append('Gen_Prod_Posting_Group')
            if row['Net_Weight_KG'] <= 0:
                score -= 20
                missing.append('Net_Weight_KG')
            if row['Unit_Volume_M3'] <= 0:
                score -= 15
                missing.append('Unit_Volume_M3')
            if row['Unit_Price_AED'] <= 0:
                score -= 10
                missing.append('Unit_Price_AED')
                
            return pd.Series({
                'Readiness_Score': max(score, 0),
                'Is_Distribution_Ready': score >= 85,
                'Missing_Attributes': ", ".join(missing) if missing else "None"
            })

        audit_results = items_df.copy()
        audit_results[['Readiness_Score', 'Is_Distribution_Ready', 'Missing_Attributes']] = audit_results.apply(score_sku, axis=1)
        return audit_results

    def audit_b2b_customers(self) -> pd.DataFrame:
        """Simulates and audits B2B wholesale accounts for UAE TRN compliance."""
        query = """
            SELECT DISTINCT Destination AS Customer_Name 
            FROM sales_lines 
            WHERE Sales_Channel = 'B2B Wholesale';
        """
        b2b_destinations = self.db.query(query)
        
        customers = []
        for idx, row in b2b_destinations.iterrows():
            has_trn = (idx % 3 != 0)  # Inject compliance gaps
            customers.append({
                "Customer_No": f"CUST-B2B-{301 + idx}",
                "Customer_Name": row['Customer_Name'],
                "Tax_Registration_No": f"TRN-UAE-{700000 + idx}" if has_trn else None,
                "Credit_Limit_AED": 500000.0,
                "Onboarding_Status": "Approved" if has_trn else "Blocked (Missing UAE TRN)"
            })
            
        return pd.DataFrame(customers)

if __name__ == "__main__":
    validator = MasterDataValidator()
    
    print("==========================================")
    print("  SPORTLUX MASTER DATA GATEKEEPER AUDIT   ")
    print("==========================================")
    
    sku_audit = validator.audit_skus()
    ready_count = sku_audit['Is_Distribution_Ready'].sum()
    blocked_count = len(sku_audit) - ready_count
    print(f"SKU Audit Summary:")
    print(f" - Total SKUs Audited     : {len(sku_audit)}")
    print(f" - Distribution Ready     : {ready_count}")
    print(f" - Blocked Exceptions     : {blocked_count}")
    
    b2b_audit = validator.audit_b2b_customers()
    print(f"\nB2B Customer Onboarding Audit:")
    print(b2b_audit.head(3))