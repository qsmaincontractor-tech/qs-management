# QS Management (Beta)

A desktop tool for Quantity Surveying: Budget analysis, Payments, Cash Flow, and Export features.

## Quick start

1. Create a Python 3.10 environment and install runtime requirements (example):

   python -m pip install -r "04 QS Management/requirements-dev.txt"

2. Run the app (example module entry):

   python "04 QS Management/main.py"

3. Open the **Budget Manager** to view trades, generate Analysis, and export to Excel.

## Tests

- Unit tests are in `04 QS Management/tests/` and can be run with:

  python -m pytest -q "04 QS Management/tests"

## Database migration

- Backup your DB file first: `cp "04 QS Management/database/QS_Project.db" "04 QS Management/database/QS_Project.db.bak"`
- Run the migration (on a copy):

  sqlite3 "04 QS Management/database/QS_Project_test.db" < "04 QS Management/migrations/20260104_update_ip_item.sql"

## Exports

- Analysis and Cash Flow exports are available in the Budget Manager (buttons below the tab).
- Exports use number formats with parentheses for negatives and red font for negative totals.

## Screenshots 📸

Below are screenshots of the main outputs (generated from the app):

- **Analysis (formatted HTML)**

  ![Analysis](docs/screenshots/analysis.png)

- **Client Cash Flow**

  ![Client Cash Flow](docs/screenshots/cashflow_client.png)

- **Subcontract Cash Flow**

  ![Subcontract Cash Flow](docs/screenshots/cashflow_subcontract.png)

- **Subcontract Cash Flow (Excel preview)**

  ![Cashflow Excel Preview](docs/screenshots/cashflow_excel_preview.png)

## Packaging & Release

- Build distribution artifacts locally:

  python -m build "04 QS Management"

- Built distributions are in `04 QS Management/dist/` (wheel and sdist).

## Notes

- Backup your DB before applying migrations.
- If you encounter issues reading Excel exports, upgrade `openpyxl` to at least 3.1.0.
