"""
SPORTLUX D365 OTIF & Fulfillment Analytics Module
Calculates On-Time In-Full (OTIF) compliance KPIs, channel breakdowns,
and delay root-cause attributions using DuckDB SQL queries.
"""

import os
import sys
import pandas as pd

# Fix path resolution for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_engine import D365DuckDBEngine

class OTIFAnalyzer:
    def __init__(self, db_engine: D365DuckDBEngine = None):
        """Initializes the OTIF analyzer with a DuckDB engine instance."""
        self.db = db_engine if db_engine else D365DuckDBEngine()

    def get_global_otif_scorecard(self) -> dict:
        """Calculates aggregate enterprise fulfillment performance KPIs."""
        query = """
            SELECT 
                COUNT(*) AS Total_Orders,
                SUM(CASE WHEN OTIF_OnTime THEN 1 ELSE 0 END) AS On_Time_Orders,
                SUM(CASE WHEN OTIF_InFull THEN 1 ELSE 0 END) AS In_Full_Orders,
                SUM(CASE WHEN OTIF_Compliant THEN 1 ELSE 0 END) AS Compliant_Orders,
                ROUND(100.0 * SUM(CASE WHEN OTIF_OnTime THEN 1 ELSE 0 END) / COUNT(*), 2) AS On_Time_Rate_Pct,
                ROUND(100.0 * SUM(CASE WHEN OTIF_InFull THEN 1 ELSE 0 END) / COUNT(*), 2) AS In_Full_Rate_Pct,
                ROUND(100.0 * SUM(CASE WHEN OTIF_Compliant THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTIF_Compliance_Pct
            FROM sales_lines;
        """
        result_df = self.db.query(query)
        return result_df.iloc[0].to_dict()

    def get_otif_by_channel(self) -> pd.DataFrame:
        """Breaks down OTIF performance across sales channels (B2B, D2C, Retail)."""
        query = """
            SELECT 
                Sales_Channel,
                COUNT(*) AS Total_Orders,
                ROUND(100.0 * SUM(CASE WHEN OTIF_OnTime THEN 1 ELSE 0 END) / COUNT(*), 2) AS On_Time_Rate_Pct,
                ROUND(100.0 * SUM(CASE WHEN OTIF_InFull THEN 1 ELSE 0 END) / COUNT(*), 2) AS In_Full_Rate_Pct,
                ROUND(100.0 * SUM(CASE WHEN OTIF_Compliant THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTIF_Compliance_Pct,
                ROUND(AVG(Delay_Days), 1) AS Avg_Delay_Days
            FROM sales_lines
            GROUP BY Sales_Channel
            ORDER BY OTIF_Compliance_Pct DESC;
        """
        return self.db.query(query)

    def get_delay_root_causes(self) -> pd.DataFrame:
        """Aggregates delay root causes for fulfillment exceptions across GCC corridors."""
        query = """
            SELECT 
                Delay_Root_Cause,
                COUNT(*) AS Incident_Count,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sales_lines WHERE Delay_Root_Cause != 'On-Time & In-Full'), 2) AS Share_Of_Exceptions_Pct
            FROM sales_lines
            WHERE Delay_Root_Cause != 'On-Time & In-Full'
            GROUP BY Delay_Root_Cause
            ORDER BY Incident_Count DESC;
        """
        return self.db.query(query)

if __name__ == "__main__":
    analyzer = OTIFAnalyzer()
    
    print("==========================================")
    print("   SPORTLUX GLOBAL OTIF SCORECARD KPI     ")
    print("==========================================")
    scorecard = analyzer.get_global_otif_scorecard()
    for metric, val in scorecard.items():
        print(f" - {metric}: {val}")
    
    print("\n--- OTIF Performance by Sales Channel ---")
    print(analyzer.get_otif_by_channel())
    
    print("\n--- Delay Root-Cause Breakdown ---")
    print(analyzer.get_delay_root_causes())