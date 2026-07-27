import sqlite3
from pathlib import Path

import pandas as pd


REQUIRED = {
    "Order ID", "Order Date", "Customer ID", "Customer Name", "Segment",
    "City", "State", "Region", "Product ID", "Category", "Sub-Category",
    "Product Name", "Sales", "Quantity", "Discount", "Profit",
}


def load_source(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="windows-1252")
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    frame["Order Date"] = pd.to_datetime(frame["Order Date"], errors="raise")
    for column in ["Sales", "Quantity", "Discount", "Profit"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame.drop_duplicates(subset=["Row ID"]).copy()


def build_warehouse(frame: pd.DataFrame, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    customer = (
        frame[["Customer ID", "Customer Name", "Segment"]]
        .drop_duplicates("Customer ID")
        .rename(columns={"Customer ID": "customer_id", "Customer Name": "customer_name", "Segment": "segment"})
    )
    product = (
        frame[["Product ID", "Product Name", "Category", "Sub-Category"]]
        .drop_duplicates("Product ID")
        .rename(columns={
            "Product ID": "product_id", "Product Name": "product_name",
            "Category": "category", "Sub-Category": "sub_category",
        })
    )
    geography = (
        frame[["City", "State", "Region"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .reset_index(names="geography_id")
        .rename(columns={"City": "city", "State": "state", "Region": "region"})
    )
    dates = pd.DataFrame({"order_date": frame["Order Date"].drop_duplicates().sort_values()})
    dates["date_id"] = dates["order_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["order_date"].dt.year
    dates["month"] = dates["order_date"].dt.month

    fact = frame.merge(
        geography,
        left_on=["City", "State", "Region"],
        right_on=["city", "state", "region"],
        how="left",
    )
    fact = fact.merge(dates[["order_date", "date_id"]], left_on="Order Date", right_on="order_date")
    fact = fact[[
        "Row ID", "Order ID", "date_id", "Customer ID", "Product ID",
        "geography_id", "Sales", "Quantity", "Discount", "Profit",
    ]].rename(columns={
        "Row ID": "sales_id", "Order ID": "order_id", "Customer ID": "customer_id",
        "Product ID": "product_id", "Sales": "sales", "Quantity": "quantity",
        "Discount": "discount", "Profit": "profit",
    })

    connection = sqlite3.connect(database)
    try:
        for table in ["fact_sales", "dim_customer", "dim_product", "dim_geography", "dim_date"]:
            connection.execute(f"DROP TABLE IF EXISTS {table}")
        customer.to_sql("dim_customer", connection, index=False)
        product.to_sql("dim_product", connection, index=False)
        geography.to_sql("dim_geography", connection, index=False)
        dates.to_sql("dim_date", connection, index=False)
        fact.to_sql("fact_sales", connection, index=False)
        connection.commit()
    finally:
        connection.close()


def export_reports(database: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        queries = {
            "regional_performance.csv": """SELECT g.region, ROUND(SUM(f.sales),2) total_sales,
                ROUND(SUM(f.profit),2) total_profit FROM fact_sales f
                JOIN dim_geography g USING(geography_id) GROUP BY g.region ORDER BY total_sales DESC""",
            "category_performance.csv": """SELECT p.category, ROUND(SUM(f.sales),2) total_sales,
                ROUND(SUM(f.profit),2) total_profit FROM fact_sales f
                JOIN dim_product p USING(product_id) GROUP BY p.category ORDER BY total_sales DESC""",
        }
        for filename, query in queries.items():
            pd.read_sql_query(query, connection).to_csv(output / filename, index=False)
    finally:
        connection.close()


def main() -> None:
    frame = load_source(Path("data/raw/superstore.csv"))
    database = Path("warehouse/sales.db")
    build_warehouse(frame, database)
    export_reports(database, Path("output"))
    print(f"Loaded {len(frame)} sales rows into the dimensional warehouse")


if __name__ == "__main__":
    main()
