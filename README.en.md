# Web Scraping — Brazilian Transparency Portal

[🇧🇷 Português](README.md) | 🇺🇸 **English**

Python project for collecting public federal expenditure data and exposing it through a simple API. Originally developed for an **Agilize backend technical challenge**, and later revisited as a backend maintenance and code-quality exercise.

## Overview

- **Selenium** accesses the public expenditure portal.
- **Pandas** parses an HTML table from the rendered page.
- **MySQL** stores expense records.
- **Flask** exposes `GET /api/dados` returning JSON.

**Stack:** Python, Selenium, Pandas, MySQL, Flask. Unit tests use Python's `unittest`.

## Getting started

Requires Python compatible with the dependencies, MySQL, and Chrome/ChromeDriver.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure `.env`, then run in separate terminals:

```bash
python -m backend.crawler
python -m api.app
```

Query `http://127.0.0.1:5000/api/dados`.

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

## Limitations

This is a **learning project, not a production service**. The portal's HTML can change, requiring updates to `TABLE_SELECTOR` or source-column mapping. The scraper reads the first matching HTML table; **full pagination is not implemented**. Running the project requires browser/driver, database and network access. No live-portal integration tests are included.

The API represents monetary values as decimal strings to avoid precision loss.

## Development history

The initial challenge implementation is preserved at [`archive/original-challenge-2022`](https://github.com/Breno3B/Web-Scraping/tree/archive/original-challenge-2022). Subsequent updates improve SQL parameterization, identifier validation, transaction handling, resource cleanup, API routing, and unit testing.

See the [original project notes](PROJETO.md) and [challenge statement](https://github.com/Debora1Allen/backend-challenge). This repository remains marked as a fork.

## Author

[Breno Rodrigues Magalhães](https://github.com/Breno3B)
