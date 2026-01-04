# Changelog

## 0.9.0b1 - Beta (2026-01-04)

### Added
- Autosave for Budget description and Payment header fields
- Formatted Analysis HTML output in Budget Manager
- Cash Flow sub-tab with Client and Subcontract pivot tables
- Excel export for Analysis and Cash Flow with formatting (parentheses for negatives, red for negative totals)
- DB migration to add FKs to `Main Contract IP Item` and remove obsolete `Main Contract IP_Old`
- Unit tests for Budget analysis and Cash Flow (pytest)
- CI workflow for lint, tests, and build

### Fixed
- Contra Charge applied as deduction in expense calculation
- Subcontract subtotal display adjusted (negated and percentage of projected subcontract expense)

### Notes
- Backup database before running migrations. Run `migrations/20260104_update_ip_item.sql` on a DB copy.
- Dev dependencies were added (`requirements-dev.txt`) including `pytest`, `flake8`, `openpyxl>=3.1.0`.

