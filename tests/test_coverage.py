"""Unit tests for bounded snapshots (no API key or network required)."""
import unittest
from unittest.mock import patch, MagicMock
import io
import json
import os
import tempfile
from pathlib import Path

from scripts import publish_expenses as pub


class SnapshotTests(unittest.TestCase):
    def test_parse_brazilian_currency(self):
        self.assertEqual(pub.parse_amount("R$ 1.234,56"), 1234.56)
        self.assertEqual(pub.parse_amount("1,234.56"), 1234.56)

    def test_invalid_amount_is_rejected(self):
        for item in [None, True, "no data", "NaN"]:
            with self.subTest(item=item), self.assertRaises(ValueError):
                pub.parse_amount(item)

    def test_normalizes_official_field_names(self):
        records=pub.normalize([{"orgao":"Órgão exemplo","codigoOrgao":"26001",
            "empenhado":"1.234,00","liquidado":"1.000,00","pago":"900,00"}],2025,"26000")
        self.assertEqual(records[0]["pago"],900.0)

    def test_partial_multi_agency_snapshot_with_metadata(self):
        def fake_urlopen(req,timeout):
            params=__import__("urllib.parse",fromlist=["parse_qs","urlparse"])
            query=params.parse_qs(params.urlparse(req.full_url).query)
            code=query["orgaoSuperior"][0]
            page=int(query["pagina"][0])
            answer=([{"orgao":f"Órgão {code}","codigoOrgao":code,
                     "empenhado":"1.234,50","liquidado":"900,20","pago":"800,10"}]
                    if page==1 else [])
            context=MagicMock()
            context.__enter__.return_value=io.BytesIO(json.dumps(answer).encode("utf-8"))
            return context
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/"expenses.json"
            variables={"CGU_API_KEY":"test-key-not-real","CGU_YEAR":"2025",
                       "CGU_ORGAOS":"26000,25000","CGU_MAX_PAGES":"2",
                       "CGU_REQUEST_DELAY_SECONDS":"1"}
            with patch.dict(os.environ,variables),patch.object(pub,"OUT",dest),\
                 patch.object(pub.urllib.request,"urlopen",side_effect=fake_urlopen),\
                 patch.object(pub.time,"sleep"):
                pub.main()
            snapshot=json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["status"],"official")
        self.assertEqual(len(snapshot["records"]),2)
        self.assertEqual(snapshot["coverage"]["requested_pages"],4)
        self.assertFalse(snapshot["coverage"]["complete"])

    def test_duplicate_records_do_not_replace_existing_snapshot(self):
        def fake_urlopen(req,timeout):
            answer=[{"orgao":"Órgão exemplo","codigoOrgao":"26001",
                "empenhado":"100","liquidado":"90","pago":"80"}]
            context=MagicMock()
            context.__enter__.return_value=io.BytesIO(json.dumps(answer).encode())
            return context
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/"expenses.json"
            dest.write_text('{"status":"sample"}',encoding="utf-8")
            variables={"CGU_API_KEY":"test-key-not-real","CGU_YEAR":"2025",
                       "CGU_ORGAOS":"26000","CGU_MAX_PAGES":"2","CGU_REQUEST_DELAY_SECONDS":"1"}
            with patch.dict(os.environ,variables),patch.object(pub,"OUT",dest),\
                 patch.object(pub.urllib.request,"urlopen",side_effect=fake_urlopen),\
                 patch.object(pub.time,"sleep"):
                with self.assertRaisesRegex(ValueError,"Duplicate agency"):
                    pub.main()
            self.assertEqual(json.loads(dest.read_text())["status"],"sample")


if __name__=="__main__":
    unittest.main()
