from .DB_manager import DB_Manager
import pandas as pd
import os

class Budget_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    def add_trade_budget(self, trade, description):
        data = {
            "Trade": trade,
            "Description": description,
            # Keep these columns with sensible defaults in case DB schema expects them
            "Qty": 0,
            "Unit": "",
            "Rate": 0,
            "Discount Factor": 0
        }
        return self.db.insert("Trade Budget", data)

    def get_trade_budget(self, trade):
        return self.db.fetch_one("SELECT * FROM \"Trade Budget\" WHERE Trade = ?", (trade,))

    def get_all_trade_budgets(self):
        return self.db.fetch_all("SELECT * FROM \"Trade Budget\"")

    def update_trade_budget(self, trade, data):
        self.db.update("Trade Budget", data, "Trade = ?", (trade,))

    def delete_trade_budget(self, trade):
        self.db.delete("Trade Budget", "Trade = ?", (trade,))

    def calculate_income(self, trade):
        # Sum income from Main Contract BQ and VO Item for a specific trade
        bq_income = self.db.fetch_one("SELECT SUM(Amount) as Total FROM \"Main Contract BQ\" WHERE Trade = ?", (trade,))
        vo_income = self.db.fetch_one("SELECT SUM(Amount) as Total FROM \"VO Item\" WHERE Trade = ?", (trade,))
        
        total_bq = bq_income['Total'] if bq_income and bq_income['Total'] else 0
        total_vo = vo_income['Total'] if vo_income and vo_income['Total'] else 0
        
        return total_bq + total_vo

    def calculate_expense(self, trade):
        # Sum expense from SC Works and SC VO Item for a specific trade
        sc_works_expense = self.db.fetch_one("SELECT SUM(Amount) as Total FROM \"Sub Con Works\" WHERE Trade = ?", (trade,))
        sc_vo_expense = self.db.fetch_one("SELECT SUM(Amount) as Total FROM \"SC VO Item\" WHERE Trade = ?", (trade,))
        
        total_sc_works = sc_works_expense['Total'] if sc_works_expense and sc_works_expense['Total'] else 0
        total_sc_vo = sc_vo_expense['Total'] if sc_vo_expense and sc_vo_expense['Total'] else 0
        
        return total_sc_works + total_sc_vo

    def get_budget_status(self, trade):
        budget_data = self.get_trade_budget(trade)
        if not budget_data:
            return None
        
        budget_amount = budget_data.get('Budget Amount')
        if budget_amount is None:
            # If Budget Amount not available, default to 0
            budget_amount = 0

        income = self.calculate_income(trade)
        expense = self.calculate_expense(trade)
        
        return {
            "Trade": trade,
            "Budget Amount": budget_amount,
            "Total Income (MC)": income,
            "Total Expense (SC)": expense,
            "Net Profit/Loss (Income - Expense)": income - expense,
            "Budget Variance (Budget - Expense)": budget_amount - expense
        }

    def get_budget_analysis(self, trade):
        """Return detailed figures for analysis display.
        Fields returned:
          - main_bq, vo_agreed, vo_potential
          - sc_works, sc_vo_agreed, sc_vo_potential, contra_charge
          - total_income, total_expense, net_profit
        """
        # Income
        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "Main Contract BQ" WHERE Trade = ?', (trade,))
        main_bq = row['Total'] if row and row['Total'] else 0

        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "VO Item" WHERE Trade = ? AND Agree = 1', (trade,))
        vo_agreed = row['Total'] if row and row['Total'] else 0

        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "VO Item" WHERE Trade = ? AND (Agree IS NULL OR Agree = 0)', (trade,))
        vo_potential = row['Total'] if row and row['Total'] else 0

        total_income = main_bq + vo_agreed

        # Expense
        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "Sub Con Works" WHERE Trade = ?', (trade,))
        sc_works = row['Total'] if row and row['Total'] else 0

        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "SC VO Item" WHERE Trade = ? AND Agree = 1', (trade,))
        sc_vo_agreed = row['Total'] if row and row['Total'] else 0

        row = self.db.fetch_one('SELECT SUM(Amount) as Total FROM "SC VO Item" WHERE Trade = ? AND (Agree IS NULL OR Agree = 0)', (trade,))
        sc_vo_potential = row['Total'] if row and row['Total'] else 0

        # Contra Charge: join on Give to (works) matching sub con works where trade = ?
        row = self.db.fetch_one('''SELECT SUM(c.Qty * (c.Rate + COALESCE(c."Admin Rate",0))) as Total
                                    FROM "Contra Charge Item" c
                                    JOIN "Sub Con Works" s ON c."Give to" = s.Works
                                    WHERE s.Trade = ?''', (trade,))
        contra_charge = row['Total'] if row and row['Total'] else 0

        # Contra Charge reduces the total expense (it's a deduction/credit)
        total_expense = sc_works + sc_vo_agreed - contra_charge
        net_profit = total_income - total_expense

        return {
            "main_bq": main_bq,
            "vo_agreed": vo_agreed,
            "vo_potential": vo_potential,
            "total_income": total_income,
            "sc_works": sc_works,
            "sc_vo_agreed": sc_vo_agreed,
            "sc_vo_potential": sc_vo_potential,
            "contra_charge": contra_charge,
            "total_expense": total_expense,
            "net_profit": net_profit
        }

    def get_all_budget_analysis(self):
        """Return list of analysis dicts for every trade."""
        trades = self.get_all_trade_budgets()
        rows = []
        for t in trades:
            trade = t['Trade']
            a = self.get_budget_analysis(trade)
            expected = a['total_income'] + a['vo_potential'] - (a['total_expense'] + a['sc_vo_potential'])
            rows.append({
                'Trade': trade,
                'Main Contract Works': a['main_bq'],
                'VO Agreed': a['vo_agreed'],
                'Subtotal Income': a['total_income'],
                'SC Works': a['sc_works'],
                'SC VO Agreed': a['sc_vo_agreed'],
                'Contra Charge': a['contra_charge'],
                'Subtotal Expense': a['total_expense'],
                'Net Profit/Loss': a['net_profit'],
                'VO Potential': a['vo_potential'],
                'SC VO Potential': a['sc_vo_potential'],
                'Expected Total Profit/Loss': expected
            })
        return rows

    def export_analysis_to_excel(self, file_path):
        """Export analysis for every trade to an Excel file (tabular format)."""
        rows = self.get_all_budget_analysis()
        df = pd.DataFrame(rows)
        # Make Contra Charge a negative value to reflect deduction
        if 'Contra Charge' in df.columns:
            df['Contra Charge'] = -df['Contra Charge']

        # Ensure output directory exists
        out_dir = os.path.dirname(file_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Write to Excel with formatting (parentheses for negatives)
        try:
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Budget Analysis')
                workbook = writer.book
                worksheet = writer.sheets['Budget Analysis']

                # Number format with parentheses for negatives
                money_fmt = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
                # Apply to all monetary columns (heuristic by column name)
                money_cols = [i for i, c in enumerate(df.columns) if c.lower() != 'trade' and c not in ['Expected Total Profit/Loss']]
                # Set column widths and formats
                for idx, col in enumerate(df.columns):
                    width = max(12, min(30, max(df[col].astype(str).map(len).max() + 2, len(col) + 2)))
                    worksheet.set_column(idx, idx, width)
                    if idx in money_cols:
                        worksheet.set_column(idx, idx, width, money_fmt)
        except Exception:
            # Fall back to simple write if xlsxwriter not available
            df.to_excel(file_path, index=False, sheet_name='Budget Analysis')
        return file_path

    def get_cashflow_client(self):
        """Return a list of payment applications as cash-flow rows and a total paid amount."""
        rows = []
        apps = self.db.fetch_all('SELECT IP, "Payment Date" as PaymentDate, "This Applied Amount" as ThisApplied, "Certified Amount" as Certified, "Paid Amount" as Paid FROM "Main Contract IP Application" ORDER BY COALESCE("Payment Date","Issue Date","Approved Date") ASC')
        total_paid = 0
        for a in apps:
            date = a.get('PaymentDate')
            ip = a.get('IP')
            applied = a.get('ThisApplied') or 0
            certified = a.get('Certified') or 0
            paid = a.get('Paid') or 0
            total_paid += paid
            rows.append({
                'Date': date,
                'IP': ip,
                'Applied Amount': applied,
                'Certified Amount': certified,
                'Paid Amount': paid
            })
        return rows, total_paid

    def get_cashflow_subcontracts(self):
        """Return a pivoted monthly accumulated paid amount table for all subcontracts.
        Returns: (months_sorted, subcontract_list, rows)
        where rows is a list of dicts with 'Month' and subcontract keys and 'Total'.
        """
        # Get all subcontracts
        scs = self.db.fetch_all('SELECT "Sub Contract No" as sc_no FROM "Sub Contract" ORDER BY "Sub Contract No"')
        subcontract_list = [s['sc_no'] for s in scs]

        # Collect payments by month and subcontract
        payments = self.db.fetch_all('SELECT "Sub Contract No" as sc_no, "Payment Date" as PaymentDate, "Paid Amount" as Paid FROM "Sub Contract IP Application" WHERE "Payment Date" IS NOT NULL')
        from collections import defaultdict
        monthly = defaultdict(lambda: defaultdict(float))
        for p in payments:
            date = p.get('PaymentDate')
            sc = p.get('sc_no')
            paid = p.get('Paid') or 0
            if not date or not sc:
                continue
            # Parse month key as mm/yy
            try:
                import datetime as _dt
                dt = _dt.datetime.fromisoformat(date)
                key = dt.strftime('%m/%y')
            except Exception:
                # fallback: try YYYY-MM-DD split
                try:
                    parts = str(date).split('-')
                    key = f"{parts[1]}/{parts[0][2:]}"
                except Exception:
                    continue
            monthly[key][sc] += paid

        # Sort months
        months = sorted(monthly.keys(), key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))

        # Build cumulative sums per subcontract
        cum = {sc: 0.0 for sc in subcontract_list}
        rows = []
        for m in months:
            row = {'Month': m}
            total = 0.0
            for sc in subcontract_list:
                cum[sc] += monthly[m].get(sc, 0.0)
                row[sc] = cum[sc]
                total += row[sc]
            row['Total'] = total
            rows.append(row)

        # Final total paid to subcontractors (accumulated latest month total)
        total_paid_sc = rows[-1]['Total'] if rows else 0.0
        # Return subcontract list as tuples (no, name) for UI header labels
        result = (months, [(s['sc_no'], s.get('sc_name', '')) for s in scs], rows, total_paid_sc)
        return result

    def export_cashflow_to_excel(self, file_path):
        """Export client and subcontract cashflow tables to an Excel file with number formatting."""
        client_rows, total_paid_client = self.get_cashflow_client()
        months, sc_list, sc_rows, total_paid_sc = self.get_cashflow_subcontracts()

        # Build DataFrames
        df_client = pd.DataFrame(client_rows)
        # ensure column order
        if not df_client.empty:
            df_client = df_client[['Date', 'IP', 'Applied Amount', 'Certified Amount', 'Paid Amount']]

        # Subcontract DF: rows is list of dicts with Month, SC columns and Total
        df_sc = pd.DataFrame(sc_rows)
        # Reorder columns: Month, Total, then SCs
        sc_cols = [sc_no for sc_no, _ in sc_list]
        cols = ['Month', 'Total'] + sc_cols
        # If df_sc empty, create empty with headers
        if df_sc.empty:
            df_sc = pd.DataFrame(columns=cols)
        else:
            df_sc = df_sc[cols]

        # Ensure output directory exists
        out_dir = os.path.dirname(file_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        try:
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                # Write client sheet
                df_client.to_excel(writer, index=False, sheet_name='Client Cash Flow')
                ws_client = writer.sheets['Client Cash Flow']

                # Write subcontract sheet
                # Build header with names: 'SCno' on first line and '(name)' on second line
                sc_header_names = [f"{no}\n({name})" if name else no for no, name in sc_list]
                # Assign display headers
                df_sc.columns = ['Month', 'Total'] + sc_header_names
                df_sc.to_excel(writer, index=False, sheet_name='Subcontract Cash Flow')
                ws_sc = writer.sheets['Subcontract Cash Flow']

                # Formats
                money_fmt = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'align': 'right'})
                header_fmt = workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center'})
                red_money = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'font_color': 'red', 'align': 'right'})

                # Apply formatting to client sheet columns and set widths
                import pandas as _pd
                def autofit_and_format(ws, df):
                    for idx, col in enumerate(df.columns):
                        col_vals = df[col].astype(str).map(len)
                        maxlen = max(col_vals.max() if not df.empty else 0, len(str(col))) + 2
                        ws.set_column(idx, idx, min(maxlen, 50))
                        # if column is numeric, apply money_fmt
                        try:
                            if _pd.api.types.is_numeric_dtype(df[col]):
                                ws.set_column(idx, idx, min(maxlen, 50), money_fmt)
                        except Exception:
                            pass

                autofit_and_format(ws_client, df_client)
                # Set wrapped header row on SC sheet to respect newline
                ws_sc.set_row(0, None, header_fmt)
                autofit_and_format(ws_sc, df_sc)

                # Add subtotal / total rows on Subcontract sheet
                # Find last row index (1-based header + rows)
                start_row = 1 + len(df_sc)
                # Write subtotal line
                subtotal_label = 'Total Payment to Subcontractor'
                ws_sc.write(start_row, 0, subtotal_label, header_fmt)
                # subtotal color red if negative
                if total_paid_sc < 0:
                    ws_sc.write(start_row, 1, total_paid_sc, red_money)
                else:
                    ws_sc.write(start_row, 1, total_paid_sc, money_fmt)
                # Write Total Cash Flow (client total - subcontract total) below
                total_cash_flow = total_paid_client - total_paid_sc
                total_label = 'Total Cash Flow'
                ws_sc.write(start_row + 2, 0, total_label, header_fmt)
                # Format negative in parentheses is handled by money_fmt
                if total_cash_flow < 0:
                    ws_sc.write(start_row + 2, 1, total_cash_flow, red_money)
                else:
                    ws_sc.write(start_row + 2, 1, total_cash_flow, money_fmt)

        except Exception:
            # Fallback - write simple excel without formatting
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_client.to_excel(writer, index=False, sheet_name='Client Cash Flow')
                df_sc.to_excel(writer, index=False, sheet_name='Subcontract Cash Flow')
        return file_path
