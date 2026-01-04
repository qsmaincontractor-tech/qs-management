from PyQt5.QtWidgets import QWidget, QListWidgetItem, QPushButton, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QLabel, QVBoxLayout
from PyQt5.QtCore import QDate, Qt
from PyQt5 import uic
import os
import datetime

class Ui_BudgetManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Set root path
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the .ui file
        ui_path = os.path.join(root_path, 'ui', 'Budget_Manager.ui')
        uic.loadUi(ui_path, self)
        
        # Connect signals
        self.btn_create.clicked.connect(self.add_record)
        self.recordList.itemClicked.connect(self.load_details)
        # Autosave description when editing finished, make trade read-only
        self.lineEdit_desc.editingFinished.connect(self.autosave)
        self.lineEdit_trade.setReadOnly(True)
        
        # Add export button to the right side layout
        self.btn_export = QPushButton("Export Analysis to Excel")
        self.btn_export.clicked.connect(self.export_analysis)
        # add below the tabs
        try:
            self.verticalLayout.addWidget(self.btn_export)
        except Exception:
            pass

        # Create Cash Flow subtab
        try:
            cf_tab = QWidget()
            cf_layout = QVBoxLayout(cf_tab)
            # Client cash flow table
            self.table_client_cf = QTableWidget()
            self.table_client_cf.setColumnCount(5)
            self.table_client_cf.setHorizontalHeaderLabels(['Payment Date', 'IP', 'Applied Amount', 'Certified Amount', 'Paid Amount'])
            cf_layout.addWidget(self.table_client_cf)
            # Total label - will show percentage relative to total project income
            self.label_total_paid = QLabel('<b>Total Amount Received from Client: $0.00 (0.00% of Project Income)</b>')
            cf_layout.addWidget(self.label_total_paid)
            # Add a spacer line
            cf_layout.addWidget(QLabel(''))
            # SC cash flow table
            self.table_sc_cf = QTableWidget()
            cf_layout.addWidget(self.table_sc_cf)
            # Sub total label for subcontract payments
            self.label_total_paid_sc = QLabel('<b>Total Payment to Subcontractor: ($0.00)</b>')
            cf_layout.addWidget(self.label_total_paid_sc)
            # Add spacer line
            cf_layout.addWidget(QLabel(''))
            # Total cash flow label
            self.label_total_cashflow = QLabel('<b>Total Cash Flow: $0.00</b>')
            cf_layout.addWidget(self.label_total_cashflow)
            # Export and Refresh buttons
            btns_layout = QVBoxLayout()
            self.btn_export_cf = QPushButton('Export Cash Flow to Excel')
            self.btn_export_cf.clicked.connect(self.export_cashflow)
            btns_layout.addWidget(self.btn_export_cf)
            self.btn_refresh_cf = QPushButton('Refresh Cash Flow')
            self.btn_refresh_cf.clicked.connect(self.refresh_cashflow)
            btns_layout.addWidget(self.btn_refresh_cf)
            cf_layout.addLayout(btns_layout)
            self.intermediateTabs.addTab(cf_tab, 'Cash Flow')
        except Exception:
            pass

        # Initial Load
        self.refresh_list()

    def refresh_list(self):
        self.recordList.clear()
        # Need get_all_trades in manager
        records = self.manager.get_all_trade_budgets()
        for rec in records:
            item = QListWidgetItem(f"{rec['Trade']} - {rec['Description']}")
            item.setData(32, rec['Trade'])
            self.recordList.addItem(item)

    def add_record(self):
        records = self.manager.get_all_trade_budgets()
        existing_trades = {rec['Trade'] for rec in records}
        base = "New Trade"
        idx = 1
        trade = base
        while trade in existing_trades:
            idx += 1
            trade = f"{base} {idx}"
        desc = ""
        # Add the new record (other fields removed from UI; defaults handled in manager)
        self.manager.add_trade_budget(trade, desc)
        self.refresh_list()
        # Select the new item
        for i in range(self.recordList.count()):
            item = self.recordList.item(i)
            if item.data(32) == trade:
                self.recordList.setCurrentItem(item)
                self.load_details(item)
                break

    def autosave(self):
        trade = self.lineEdit_trade.text()
        desc = self.lineEdit_desc.text()
        if trade:
            data = {"Description": desc}
            self.manager.update_trade_budget(trade, data)
            self.refresh_list()

    def load_details(self, item):
        trade = item.data(32)
        result = self.manager.get_budget_status(trade)
        if result:
            self.lineEdit_trade.setText(str(result['Trade']))
            self.lineEdit_trade.setReadOnly(True)
            # Populate description
            budget = self.manager.get_trade_budget(trade)
            if budget:
                self.lineEdit_desc.setText(budget.get('Description', ''))
            
            # Update Analysis Tab with formatted HTML
            analysis = self.manager.get_budget_analysis(trade)
            def fmt(v, force_paren=False):
                # Format with parentheses for negative values, or force_paren to show positive as (x)
                if v is None:
                    v = 0
                if v < 0:
                    return f"(${abs(v):,.2f})"
                if force_paren:
                    return f"({v:,.2f})"
                return f"${v:,.2f}"

            def fmt_html_currency(v, bold=False, force_paren=False):
                # Return HTML with red color if negative; supports bold and forcing parentheses
                txt = fmt(v, force_paren=force_paren)
                if v is None:
                    v = 0
                if v < 0:
                    txt = f"<span style=\"color:red\">{txt}</span>"
                if bold:
                    txt = f"<b>{txt}</b>"
                return txt

            trade_html = f"<b>Trade: {result['Trade']}</b><br><br>"

            income_html = "<u>Total Project Income</u><br>"
            income_html += f"Main Contract Works: {fmt(analysis['main_bq'])}<br>"
            income_html += f"Variation Order (Agreed): {fmt(analysis['vo_agreed'])}<br>"
            # Subtotal should be red if negative
            income_html += f"Subtotal Income: {fmt_html_currency(analysis['total_income'], bold=True)}<br><br>"

            expense_html = "<u>Total Project Expense</u><br>"
            expense_html += f"Subcontract Works: {fmt(analysis['sc_works'])}<br>"
            expense_html += f"Subcontract VO (Agreed): {fmt(analysis['sc_vo_agreed'])}<br>"
            # Contra Charge is a deduction — show in parentheses
            expense_html += f"Less Contra Charge: {fmt(analysis['contra_charge'], force_paren=True)}<br>"
            # Subtotal should be red if negative
            expense_html += f"Subtotal Expense: {fmt_html_currency(analysis['total_expense'], bold=True)}<br><br>"

            totals_html = f"Total Profit/Loss: {fmt_html_currency(analysis['net_profit'], bold=True)}<br>"
            potentials_html = "<hr>"
            potentials_html += "<b>Potential Income:</b><br>"
            potentials_html += f"Main Contract VO (not agreed): {fmt(analysis['vo_potential'])}<br>"
            potentials_html += "<b>Potential Expense:</b><br>"
            potentials_html += f"SC VO (not agreed): {fmt(analysis['sc_vo_potential'])}<br><br>"

            expected = analysis['total_income'] + analysis['vo_potential'] - (analysis['total_expense'] + analysis['sc_vo_potential'])
            potentials_html += f"Expected Total Profit/Loss: {fmt_html_currency(expected, bold=True)}"

            html = trade_html + income_html + expense_html + totals_html + potentials_html
            self.textEdit_analysis.setHtml(html)
            try:
                self.refresh_cashflow()
            except Exception:
                pass

    def export_analysis(self):
        # Ask user for file path
        fn, _ = QFileDialog.getSaveFileName(self, "Save Analysis as Excel", "budget_analysis.xlsx", "Excel Files (*.xlsx)")
        if not fn:
            return
        try:
            self.manager.export_analysis_to_excel(fn)
            QMessageBox.information(self, "Export Complete", f"Analysis exported to {fn}")
            #start the file
            os.startfile(fn)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export analysis: {e}")

    def export_cashflow(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save Cash Flow as Excel", "cash_flow.xlsx", "Excel Files (*.xlsx)")
        if not fn:
            return
        try:
            self.manager.export_cashflow_to_excel(fn)
            QMessageBox.information(self, "Export Complete", f"Cash Flow exported to {fn}")
            os.startfile(fn)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export cash flow: {e}")

    def refresh_cashflow(self):
        # Refresh client cash flow table
        try:
            rows, total_paid = self.manager.get_cashflow_client()
            self.table_client_cf.setRowCount(len(rows))
            def fmt(v):
                if v is None:
                    v = 0
                if v < 0:
                    return f"({abs(v):,.2f})"
                return f"{v:,.2f}"
            def fmt_currency(v, force_paren=False):
                if v is None:
                    v = 0
                if v < 0:
                    return f"(${abs(v):,.2f})"
                if force_paren:
                    return f"(${v:,.2f})"
                return f"${v:,.2f}"
            for r_idx, r in enumerate(rows):
                it0 = QTableWidgetItem(str(r.get('Date') or ''))
                self.table_client_cf.setItem(r_idx, 0, it0)
                it1 = QTableWidgetItem(str(r.get('IP') or ''))
                self.table_client_cf.setItem(r_idx, 1, it1)
                it2 = QTableWidgetItem(fmt(r.get('Applied Amount')))
                it2.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_client_cf.setItem(r_idx, 2, it2)
                it3 = QTableWidgetItem(fmt(r.get('Certified Amount')))
                it3.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_client_cf.setItem(r_idx, 3, it3)
                it4 = QTableWidgetItem(fmt(r.get('Paid Amount')))
                it4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_client_cf.setItem(r_idx, 4, it4)
            # Compute percentage vs current trade income (defer expense percentage until subcontract totals available)
            pct_text = '0.00%'
            try:
                trade = self.lineEdit_trade.text()
                if trade:
                    analysis = self.manager.get_budget_analysis(trade)
                    income = analysis.get('total_income', 0) if analysis else 0
                    pct = (total_paid / income * 100) if income else 0
                    pct_text = f"{pct:,.2f}%"
            except Exception:
                pass
            # Set a placeholder now; we'll update with subcontract percentage after SC totals are computed
            self.label_total_paid.setText(f"<b>Total Amount Received from Client: {fmt_currency(total_paid)} [{pct_text} of Project Income]</b>")
        except Exception:
            pass

        # Refresh subcontract cash flow pivot
        try:
            months, sc_list, rows, total_paid_sc = self.manager.get_cashflow_subcontracts()
            # build headers: Month | Total | SCXX (Subcontract Name) with two lines
            headers = ['Month', 'Total'] + [f"{no}\n({name})" if name else no for no, name in sc_list]
            self.table_sc_cf.setColumnCount(len(headers))
            self.table_sc_cf.setHorizontalHeaderLabels(headers)
            # Allow header word wrap for multi-line headers
            try:
                self.table_sc_cf.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            except Exception:
                pass
            self.table_sc_cf.setRowCount(len(rows))
            for r_idx, r in enumerate(rows):
                self.table_sc_cf.setItem(r_idx, 0, QTableWidgetItem(str(r.get('Month'))))
                # Total column moved to 2nd (numeric, right-aligned)
                it_total = QTableWidgetItem(fmt(r.get('Total', 0.0)))
                it_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_sc_cf.setItem(r_idx, 1, it_total)
                for c_idx, (sc_no, sc_name) in enumerate(sc_list, start=2):
                    val = r.get(sc_no, 0.0)
                    txt = fmt(val)
                    it_sc = QTableWidgetItem(txt)
                    it_sc.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table_sc_cf.setItem(r_idx, c_idx, it_sc)
            # Update subtotal label (show as parenthesis - deduction) and bold; color red if negative
            def fmt_html(v, bold=False, force_paren=False):
                if v is None:
                    v = 0
                if v < 0:
                    txt = f"(${abs(v):,.2f})"
                    txt = f"<span style=\"color:red\">{txt}</span>"
                else:
                    txt = f"(${v:,.2f})" if force_paren else f"${v:,.2f}"
                if bold:
                    txt = f"<b>{txt}</b>"
                return txt

            # Display subtotal as deduction (negated) and show percentage vs forecasted subcontract expense (Works + VO agreed; exclude VO potential; minus Contra Charge)
            try:
                # Compute projected subcontract expense from analysis (Works + VO agreed) and subtract Contra Charge
                proj_exp = 0
                trade = self.lineEdit_trade.text()
                if trade:
                    analysis = self.manager.get_budget_analysis(trade)
                    if analysis:
                        proj_exp = (analysis.get('sc_works', 0) + analysis.get('sc_vo_agreed', 0) - analysis.get('contra_charge', 0))
                negated_sub = -total_paid_sc
                pct_exp_text = '0.00%'
                # Only compute percentage if the projected expense is a positive number
                if proj_exp > 0:
                    pct_exp = (total_paid_sc / proj_exp * 100)
                    pct_exp_text = f"{pct_exp:,.2f}%"
            except Exception:
                proj_exp = 0
                negated_sub = -total_paid_sc
                pct_exp_text = '0.00%'

            self.label_total_paid_sc.setText(f"<b>Total Payment to Subcontractor: {fmt_html(negated_sub, bold=True, force_paren=True)} [{pct_exp_text} of Total Project Expense]</b>")

            # Update total cash flow (client total - subcontract total) and update client percentage vs subcontract payments
            try:
                _, total_paid_client = self.manager.get_cashflow_client()
                total_cash_flow = total_paid_client - total_paid_sc
                # format and color if negative
                if total_cash_flow < 0:
                    tc = f"<span style=\"color:red\">(${abs(total_cash_flow):,.2f})</span>"
                else:
                    tc = f"${total_cash_flow:,.2f}"
                self.label_total_cashflow.setText(f"<b>Total Cash Flow: {tc}</b>")

                # Compute pct of projected subcontract expense for client amounts
                pct_exp_client_text = '0.00%'
                try:
                    if proj_exp > 0:
                        pct_exp_client = (total_paid_client / proj_exp * 100)
                        pct_exp_client_text = f"{pct_exp_client:,.2f}%"
                except Exception:
                    pass

                # Compute income pct again safely
                pct_text = '0.00%'
                try:
                    trade = self.lineEdit_trade.text()
                    if trade:
                        analysis = self.manager.get_budget_analysis(trade)
                        income = analysis.get('total_income', 0) if analysis else 0
                        pct = (total_paid_client / income * 100) if income else 0
                        pct_text = f"{pct:,.2f}%"
                except Exception:
                    pass

                self.label_total_paid.setText(f"<b>Total Amount Received from Client: {fmt_currency(total_paid_client)} ({pct_text} of Project Income) [{pct_exp_client_text} of Total Project Expense]</b>")
            except Exception:
                pass
        except Exception:
            pass

    def clear_form(self):
        self.lineEdit_trade.clear()
        self.lineEdit_desc.clear()
