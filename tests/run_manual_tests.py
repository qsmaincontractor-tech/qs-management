"""
Manual test runner fallback when pytest is unavailable.
Runs core checks and reports pass/fail.
"""
import sys, os
module_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, module_root)
from function.DB_manager import DB_Manager
from function.Budget_manager import Budget_Manager

DB_PATH = os.path.join(module_root, 'database', 'QS_Project.db')

def run():
    db = DB_Manager(DB_PATH)
    bm = Budget_Manager(db)
    ok = True
    try:
        trades = [t['Trade'] for t in bm.get_all_trade_budgets()]
        print('Trades sample:', trades[:5])
        trade = trades[0]
        a = bm.get_budget_analysis(trade)
        print('Budget analysis keys:', list(a.keys()))
    except Exception as e:
        print('Budget analysis test failed:', e)
        ok = False

    try:
        rows, total = bm.get_cashflow_client()
        calc = sum(r.get('Paid Amount') or 0 for r in rows)
        print('Client total:', total, 'sum check:', calc)
        assert abs(calc - total) < 1e-6
    except Exception as e:
        print('Client cashflow test failed:', e)
        ok = False

    try:
        months, sc_list, rows, total_paid_sc = bm.get_cashflow_subcontracts()
        print('SC months:', months)
        # monotonic check
        for sc_no, _ in sc_list:
            prev = 0.0
            for r in rows:
                val = r.get(sc_no, 0.0) or 0.0
                if val + 1e-6 < prev:
                    raise AssertionError(f'Non-monotonic cumulative values for {sc_no}')
                prev = val
        print('Subcontract cashflow monotonic check passed')
    except Exception as e:
        print('Subcontract cashflow test failed:', e)
        ok = False

    try:
        import tempfile
        fa = os.path.join(tempfile.gettempdir(), 'tmp_budget_analysis_test.xlsx')
        fb = os.path.join(tempfile.gettempdir(), 'tmp_cashflow_test.xlsx')
        bm.export_analysis_to_excel(fa)
        bm.export_cashflow_to_excel(fb)
        print('Exports created:', os.path.exists(fa), os.path.exists(fb))
    except Exception as e:
        print('Export tests failed:', e)
        ok = False

    print('ALL OK' if ok else 'SOME TESTS FAILED')

if __name__ == '__main__':
    run()
