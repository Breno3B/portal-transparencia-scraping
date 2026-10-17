"""Read-only Flask API for the scraped records."""
import os
from decimal import Decimal
from flask import Flask, jsonify
from dotenv import load_dotenv
from storage.connection import db_connection, identifier

load_dotenv()

def create_app(connection_factory=db_connection):
    app = Flask(__name__)

    @app.get("/api/dados")
    def expenses():
        database = identifier(os.getenv("DB_NAME", "agilize"))
        table = identifier(os.getenv("TABLE_NAME", "expense"))
        connection = connection_factory()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(f"SELECT mes_ano, programa_orcamentario, acao_orcamentaria, "
                               f"valor_empenhado, valor_liquidado, valor_pago, "
                               f"valor_restos_a_pagar_pagos FROM `{database}`.`{table}`")
                records = cursor.fetchall()
                for record in records:
                    for key, value in record.items():
                        if isinstance(value, Decimal):
                            record[key] = str(value)
                return jsonify(records)
            finally:
                cursor.close()
        finally:
            connection.close()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
