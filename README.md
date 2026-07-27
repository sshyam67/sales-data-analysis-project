# Sales Data Analysis Project

An end-to-end analytics-engineering workflow that transforms a raw Superstore
extract into a dimensional SQLite warehouse and reproducible KPI exports.

## Architecture

```text
data/raw/superstore.csv
        |
        v
schema + type validation
        |
        v
dimensions (customer, product, geography, date)
        |
        v
fact_sales -> SQL analytics -> output CSV reports
```

## Run

```bash
pip install -r requirements.txt
python pipeline.py
```

The pipeline creates `warehouse/sales.db` and exports regional and category
performance reports under `output/`.

```bash
python -m unittest discover -s tests -v
```

## Skills demonstrated

- Raw-to-curated transformation with explicit schema checks
- Star-schema construction and surrogate keys
- Idempotent warehouse builds
- SQL-based business metrics
- Automated testing and GitHub Actions

The dataset is a public sample used for portfolio demonstration. This project
does not include a fabricated Power BI file; every committed artifact is
runnable or inspectable.

## Production roadmap

Add incremental loads, slowly changing dimensions, dbt models, orchestration,
warehouse-native tests, and a governed BI semantic layer.
