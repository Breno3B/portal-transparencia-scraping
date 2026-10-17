"""Normalize scraped records and persist them safely."""
import os
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from storage.connection import identifier

load_dotenv()

FIELDS = (
    "mes_ano", "programa_orcamentario", "acao_orcamentaria",
    "valor_empenhado", "valor_liquidado", "valor_pago",
    "valor_restos_a_pagar_pagos",
)
# Column offsets from the historical challenge page. Verify against live HTML.
SOURCE_COLUMNS = (1, 7, 8, 15, 16, 17, 18)

def parse_value(value):
    """Parse a Brazilian or standard decimal value into Decimal."""
    if value is None:
        return None
    text = str(value).strip().replace("R$", "").replace("\u00a0", "").replace(" ", "")
    if not text or text in {"-", "nan", "None"}:
        return None
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid monetary value: {value!r}") from exc

def normalize_row(row):
    if len(row) <= max(SOURCE_COLUMNS):
        raise ValueError("Unexpected source table layout; verify column mapping")
    values = [row.iloc[i] for i in SOURCE_COLUMNS]
    return tuple(str(v).strip() for v in values[:3]) + tuple(
        parse_value(v) for v in values[3:]
    )

def save_data_frame(data_frame, connection, table_name=None):
    table = identifier(table_name or os.getenv("TABLE_NAME", "expense"))
    placeholders = ", ".join(["%s"] * len(FIELDS))
    query = f"INSERT INTO `{table}` ({', '.join(FIELDS)}) VALUES ({placeholders})"
    records = [normalize_row(row) for _, row in data_frame.iterrows()]
    cursor = connection.cursor()
    try:
        if records:
            cursor.executemany(query, records)
        connection.commit()
        return len(records)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
