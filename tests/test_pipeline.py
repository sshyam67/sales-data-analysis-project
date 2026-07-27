import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline import build_warehouse, export_reports, load_source


class SalesPipelineTests(unittest.TestCase):
    def test_builds_fact_table_and_reports(self) -> None:
        frame = load_source(Path("data/raw/superstore.csv")).head(100)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "sales.db"
            build_warehouse(frame, database)
            export_reports(database, root / "output")
            connection = sqlite3.connect(database)
            try:
                count = connection.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(count, 100)
            self.assertTrue((root / "output" / "regional_performance.csv").exists())


if __name__ == "__main__":
    unittest.main()
