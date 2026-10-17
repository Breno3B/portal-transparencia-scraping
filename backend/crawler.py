"""Collect expenditure table rows from the public Transparency Portal.

The portal is JavaScript-driven and its markup can change. Keep the selector
configurable and fail clearly rather than silently storing incorrect data.
"""
import os
from io import StringIO

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from backend.save_data import save_data_frame
from storage.connection import db_connection
from storage.migrate import access_database

load_dotenv()
URL_BASE = "https://www.transparencia.gov.br/despesas/orgao?ordenarPor=orgaoSuperior&direcao=asc"
TABLE_SELECTOR = os.getenv("TABLE_SELECTOR", "table")
TIMEOUT = 25

def scraper(url=URL_BASE, *, driver_factory=None, table_selector=TABLE_SELECTOR):
    """Return the first matching HTML table as a DataFrame.

    This does not automatically paginate through every result page.
    """
    if driver_factory is None:
        opts = Options()
        opts.add_argument("--headless=new")
        driver_factory = lambda: webdriver.Chrome(options=opts)
    driver = driver_factory()
    try:
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
        )
        tables = pd.read_html(StringIO(driver.page_source))
        if not tables:
            raise ValueError("No HTML tables were found in the rendered page")
        return tables[0]
    finally:
        driver.quit()

def main():
    frame = scraper()
    connection = db_connection()
    try:
        access_database(connection)
        count = save_data_frame(frame, connection)
        print(f"Saved {count} records")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
