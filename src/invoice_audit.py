"""
SPORTLUX D365 Freight Invoice Audit Module
Automates 3PL tariff cross-checking, chargeable weight verification,
and financial overcharge detection using DuckDB SQL.
"""

import os
import sys
import pandas as pd

# Fix path resolution for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_engine import D365DuckDBEngine

class InvoiceAuditor:
    def __init__(self, db_engine: D365DuckDBEngine = None):
        """Initializes the invoice auditor with a DuckDB engine instance."""
        self.db = db_engine if db_engine else D365DuckDBEngine()

    def get_carrier_leakage_summary(self) -> pd.DataFrame:
        """Aggregates freight overcharge leakage and discrepancy totals by carrier partner."""
        query = """
            SELECT 
                i.Carrier_Code,
                COUNT(i.Invoice_No) AS Total_Invoices,
                SUM(CASE WHEN i.Anomaly_Flag THEN 1 ELSE 0 END) AS Anomaly_Count,
                ROUND(SUM(i.Billed_Amount_AED), 2) AS Total_Billed_AED,
                ROUND(SUM(CASE WHEN i.Variance_AED > 0 THEN i.Variance_AED ELSE 0 END), 2) AS Recoverable_Leakage_AED
            FROM carrier_freight_invoices i
            GROUP BY i.Carrier_Code
            ORDER BY Recoverable_Leakage_AED DESC;
        """
        return self.db.query(query)

    def get_anomaly_breakdown(self) -> pd.DataFrame:
        """Breaks down billing discrepancies by specific exception classification."""
        query = """
            SELECT 
                Anomaly_Type,
                COUNT(*) AS Incident_Count,
                ROUND(SUM(Variance_AED), 2) AS Total_Variance_AED,
                ROUND(AVG(Variance_AED), 2) AS Avg_Variance_AED
            FROM carrier_freight_invoices
            WHERE Anomaly_Flag = TRUE
            GROUP BY Anomaly_Type
            ORDER BY Total_Variance_AED DESC;
        """
        return self.db.query(query)

if __name__ == "__main__":
    auditor = InvoiceAuditor()
    
    print("==========================================")
    print("    SPORTLUX 3PL CARRIER LEAKAGE AUDIT    ")
    print("==========================================")
    leakage_df = auditor.get_carrier_leakage_summary()
    print(leakage_df)
    
    print("\n--- Anomaly Type Financial Breakdown ---")
    anomaly_df = auditor.get_anomaly_breakdown()
    print(anomaly_df)