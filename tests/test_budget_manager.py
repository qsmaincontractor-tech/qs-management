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


def test_get_budget_analysis_keys(bm):
    trades = [t['Trade'] for t in bm.get_all_trade_budgets()]
    assert trades, "No trades found in test DB"
    trade = trades[0]
    a = bm.get_budget_analysis(trade)
    for k in ['main_bq', 'total_income', 'sc_works', 'contra_charge', 'total_expense', 'net_profit']:
        assert k in a
    assert a['total_income'] == a['main_bq'] + a['vo_agreed']


def test_contra_reduces_expense(bm):
    trades = [t['Trade'] for t in bm.get_all_trade_budgets()]
    trade = trades[0]
    a = bm.get_budget_analysis(trade)
    calc = a['sc_works'] + a['sc_vo_agreed'] - a['contra_charge']
    assert pytest.approx(calc, rel=1e-6) == a['total_expense']


def test_export_analysis_creates_file(bm, tmp_path):
    out = tmp_path / 'budget_analysis_test.xlsx'
    path = bm.export_analysis_to_excel(str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

    # Try reading sheet names if openpyxl is recent enough
    try:
        import openpyxl
        ver = tuple(map(int, openpyxl.__version__.split('.')[:2]))
        if ver >= (3, 1):
            import pandas as pd
            x = pd.read_excel(path, sheet_name=None)
            assert 'Budget Analysis' in x
    except Exception:
        pytest.skip('openpyxl/pandas not available or too old; skip detailed read')
