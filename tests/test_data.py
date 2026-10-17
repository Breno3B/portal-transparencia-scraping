from decimal import Decimal
import unittest
from unittest.mock import MagicMock
import pandas as pd
from backend.save_data import parse_value, normalize_row, save_data_frame
from storage.connection import identifier
from api.app import create_app

class DataTests(unittest.TestCase):
    def test_parse_brazilian_currency(self):
        self.assertEqual(parse_value("1.234,56"), Decimal("1234.56"))
        self.assertEqual(parse_value("1234.56"), Decimal("1234.56"))
        self.assertIsNone(parse_value("-"))

    def test_reject_unexpected_table(self):
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            normalize_row(pd.Series(["one", "two"]))

    def test_identifiers(self):
        self.assertEqual(identifier("expense_2"), "expense_2")
        for value in ["foo;DROP", "bad-name", ""]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    identifier(value)

    def test_bulk_insert_with_placeholders(self):
        row = list(range(19))
        row[15:19] = ["1,20", "2,30", "3,40", "4,50"]
        conn = MagicMock()
        count = save_data_frame(pd.DataFrame([row]), conn, table_name="expense")
        self.assertEqual(count, 1)
        sql, records = conn.cursor.return_value.executemany.call_args.args
        self.assertIn("%s", sql)
        self.assertNotIn("DROP", sql)
        self.assertEqual(records[0][3], Decimal("1.20"))
        conn.commit.assert_called_once()

    def test_api_response(self):
        conn = MagicMock()
        cur = conn.cursor.return_value
        cur.fetchall.return_value = [{"valor_pago": Decimal("2.50"), "mes_ano": "2022-01"}]
        client = create_app(lambda: conn).test_client()
        response = client.get("/api/dados")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["valor_pago"], "2.50")
        conn.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
