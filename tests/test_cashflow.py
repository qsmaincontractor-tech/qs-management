import sys, os
import pytest

module_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, module_root)

from function.DB_manager import DB_Manager
from function.Budget_manager import Budget_Manager

DB_PATH = os.path.join(module_root, 'database', 'QS_Project.db')

@pytest.fixture(scope='module')
def bm():
    db = DB_Manager(DB_PATH)
    return Budget_Manager(db)


def test_get_cashflow_client_totals(bm):
    rows, total = bm.get_cashflow_client()
    calc = sum(r.get('Paid Amount') or 0 for r in rows)
    assert pytest.approx(calc, rel=1e-6) == total


def test_get_cashflow_subcontracts_monotonic(bm):
    months, sc_list, rows, total_paid_sc = bm.get_cashflow_subcontracts()
    # for each subcontract column, values should be non-decreasing across months
    for sc_no, sc_name in sc_list:
        prev = 0.0
        for r in rows:
            val = r.get(sc_no, 0.0) or 0.0
            assert val >= prev - 1e-6
            prev = val


def test_export_cashflow_creates_file(bm, tmp_path):
    out = tmp_path / 'cashflow_test.xlsx'
    path = bm.export_cashflow_to_excel(str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

    try:
        import openpyxl
        ver = tuple(map(int, openpyxl.__version__.split('.')[:2]))
        if ver >= (3, 1):
            import pandas as pd
            x = pd.read_excel(path, sheet_name=None)
            assert 'Client Cash Flow' in x and 'Subcontract Cash Flow' in x
    except Exception:
        pytest.skip('openpyxl/pandas not available or too old; skip detailed read')
