"""Safe monetary parsing and official data mapping, without API access."""
import unittest

from scripts.publish_expenses import normalize, parse_amount, value


class ParseAmountTests(unittest.TestCase):
    def test_brazilian_format(self):
        self.assertEqual(parse_amount("R$ 1.234.567,89"), 1234567.89)
        self.assertEqual(parse_amount("12.345,67"), 12345.67)

    def test_standard_numbers(self):
        self.assertEqual(parse_amount("1234.56"), 1234.56)
        self.assertEqual(parse_amount(1250.5), 1250.5)
        self.assertEqual(parse_amount("1,234.56"), 1234.56)

    def test_invalid_values(self):
        for raw in (None, "", "não informado", "NaN", True):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_amount(raw)

    def test_real_field_names_without_live_api(self):
        response = [{"orgao": "Órgão de teste", "codigoOrgao": "26000",
                     "empenhado": "1.234,56", "liquidado": "1000,00",
                     "pago": "900,55"}]
        records = normalize(response, 2025, "26000")
        self.assertEqual(records[0]["empenhado"], 1234.56)
        self.assertEqual(records[0]["liquidado"], 1000.0)
        self.assertEqual(records[0]["pago"], 900.55)

    def test_missing_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            value({"pago": None}, "pago")


if __name__ == "__main__":
    unittest.main()
