"""Initialize database and table if they do not exist."""
import os
from dotenv import load_dotenv
from storage.connection import identifier

load_dotenv()

def access_database(connection):
    database = identifier(os.getenv("DB_NAME", "agilize"))
    table = identifier(os.getenv("TABLE_NAME", "expense"))
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4")
        cursor.execute(f"USE `{database}`")
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{table}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mes_ano VARCHAR(100),
            programa_orcamentario VARCHAR(255),
            acao_orcamentaria VARCHAR(255),
            valor_empenhado DECIMAL(18,2),
            valor_liquidado DECIMAL(18,2),
            valor_pago DECIMAL(18,2),
            valor_restos_a_pagar_pagos DECIMAL(18,2)
        )""")
        connection.commit()
    finally:
        cursor.close()
