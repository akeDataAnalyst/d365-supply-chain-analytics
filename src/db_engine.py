"""
SPORTLUX D365 ERP DuckDB Database Engine
Loads raw CSV extracts from data/raw/ into an in-memory DuckDB database
and provides structured SQL query interfaces for analytics modules.
"""

import os
import duckdb
import pandas as pd

class D365DuckDBEngine:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        # Initialize in-memory DuckDB connection
        self.conn = duckdb.connect(database=":memory:", read_only=False)
        self._initialize_tables()

    def _initialize_tables(self):
        """Loads all raw CSV extracts into virtual SQL tables inside DuckDB."""
        item_path = os.path.join(self.data_dir, "d365_item_master.csv")
        sales_path = os.path.join(self.data_dir, "d365_sales_lines.csv")
        ledger_path = os.path.join(self.data_dir, "d365_item_ledger_entries.csv")
        whse_path = os.path.join(self.data_dir, "d365_warehouse_entries.csv")
        invoice_path = os.path.join(self.data_dir, "carrier_freight_invoices.csv")

        self.conn.execute(f"""
            CREATE OR REPLACE TABLE item_master AS 
            SELECT * FROM read_csv_auto('{item_path}');
            
            CREATE OR REPLACE TABLE sales_lines AS 
            SELECT * FROM read_csv_auto('{sales_path}');
            
            CREATE OR REPLACE TABLE item_ledger_entries AS 
            SELECT * FROM read_csv_auto('{ledger_path}');
            
            CREATE OR REPLACE TABLE warehouse_entries AS 
            SELECT * FROM read_csv_auto('{whse_path}');
            
            CREATE OR REPLACE TABLE carrier_freight_invoices AS 
            SELECT * FROM read_csv_auto('{invoice_path}');
        """)

    def query(self, sql_query: str) -> pd.DataFrame:
        """Executes any SQL query and returns results as a pandas DataFrame."""
        return self.conn.execute(sql_query).df()

    def get_master_fulfillment_view(self) -> pd.DataFrame:
        """Joins sales, items, warehouse, and freight tables into a single master analytics view."""
        query = """
            SELECT 
                s.Document_No_,
                s.Posting_Date,
                s.Sales_Channel,
                s.Destination,
                s.Location_Code,
                s.Carrier_Code,
                s.Quantity_Ordered,
                s.Quantity_Shipped,
                s.OTIF_OnTime,
                s.OTIF_InFull,
                s.OTIF_Compliant,
                s.Delay_Days,
                s.Delay_Root_Cause,
                i.Brand,
                i.Item_Category_Code,
                i.Net_Weight_KG,
                w.Pick_Latency_Hours,
                f.Invoice_No,
                f.Billed_Amount_AED,
                f.Contracted_Rate_AED,
                f.Variance_AED,
                f.Anomaly_Flag,
                f.Anomaly_Type
            FROM sales_lines s
            LEFT JOIN item_master i ON s.Item_No_ = i.No_
            LEFT JOIN warehouse_entries w ON s.Document_No_ = w.Source_Document_No_
            LEFT JOIN carrier_freight_invoices f ON s.Document_No_ = f.Document_No_
        """
        return self.query(query)

if __name__ == "__main__":
    db = D365DuckDBEngine()
    df_view = db.get_master_fulfillment_view()
    print(f"DuckDB Initialized Successfully!")
    print(f"   - Master Unified View Rows: {df_view.shape[0]}")
    print(f"   - Master Unified View Columns: {df_view.shape[1]}")
    print(df_view.head(3))