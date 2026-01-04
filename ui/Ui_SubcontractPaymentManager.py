from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
                             QListWidgetItem, QFormLayout, QLabel, QLineEdit, QDateEdit, 
                             QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QMessageBox, QMenu, QAction, QComboBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QColor
import datetime

class Ui_SubcontractPaymentManager(QWidget):
    def __init__(self, manager, subcontract_manager):
        super().__init__()
        self.manager = manager
        self.subcontract_manager = subcontract_manager
        self.sub_contract_no = None
        self.init_ui()
        self.load_subcontracts()

    def init_ui(self):
        # Load UI from .ui file for designer-friendly layout
        from PyQt5 import uic
        import os
        ui_path = os.path.join(os.path.dirname(__file__), 'Subcontract_Payment_Manager.ui')
        uic.loadUi(ui_path, self)

        # Ensure widgets are present and set up validators/formats
        self.edit_ip_no.setReadOnly(True)
        for dt in ('date_draft', 'date_issue', 'date_approved', 'date_payment'):
            getattr(self, dt).setCalendarPopup(True)
            getattr(self, dt).setDisplayFormat('yyyy-MM-dd')

        validator = QDoubleValidator(0, 1e12, 2)
        self.spin_certified.setValidator(validator)
        self.spin_paid.setValidator(validator)
        self.text_remark.setMaximumHeight(60)

        # Table setup (added amount columns for Works, VO and Contra Charge)
        self.item_table.setColumnCount(14)
        self.item_table.setHorizontalHeaderLabels([
            "Item", "Type", "Contract Work Ref", "Works Amount", "VO Ref", "VO Amount", "Contra Charge Ref", "Contra Charge Amount", "Description",
            "Applied", "Certified", "Paid", "Remark", "ID"
        ])
        self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.item_table.hideColumn(13)

        # Connect signals
        self.combo_subcontract.currentIndexChanged.connect(self.on_subcontract_changed)
        self.ip_list.itemClicked.connect(self.on_ip_selected)
        self.btn_add_ip.clicked.connect(self.add_ip)
        self.btn_copy_ip.clicked.connect(self.copy_previous_ip)
        self.btn_delete_ip.clicked.connect(self.delete_ip)

        self.date_draft.dateChanged.connect(self.auto_save_header)
        self.date_issue.dateChanged.connect(self.auto_save_header)
        self.date_approved.dateChanged.connect(self.auto_save_header)
        self.date_payment.dateChanged.connect(self.auto_save_header)
        self.spin_certified.textChanged.connect(self.auto_save_header)
        self.spin_paid.textChanged.connect(self.auto_save_header)
        self.text_remark.textChanged.connect(self.auto_save_header)

        self.btn_add_item.setEnabled(False)
        self.btn_add_item.clicked.connect(self.add_item)
        self.btn_delete_item.setEnabled(False)
        self.btn_delete_item.clicked.connect(self.delete_item)
        self.btn_calc_totals.setEnabled(False)
        self.btn_calc_totals.clicked.connect(self.calculate_totals)

        self.item_table.itemChanged.connect(self.on_item_changed)

        # Set initial splitter sizes: narrow left panel for payment list
        try:
            self.main_splitter.setSizes([200, 800])
        except Exception:
            pass

        self.current_ip = None
        self.loading_item = False

    def load_subcontracts(self):
        self.combo_subcontract.clear()
        subcontracts = self.subcontract_manager.get_all_subcontracts()
        for sc in subcontracts:
            self.combo_subcontract.addItem(f'{sc["Sub Contract No"]} - {sc["Sub Contract Name"]}', sc["Sub Contract No"])
        
        if self.combo_subcontract.count() > 0:
            self.sub_contract_no = self.combo_subcontract.currentData()
            self.refresh_ips()

    def on_subcontract_changed(self, index):
        self.sub_contract_no = self.combo_subcontract.currentData()
        self.current_ip = None  # Reset selection
        self.refresh_ips()
        self.clear_header()
        self.item_table.setRowCount(0)

    def format_number(self, value):
        """Format number with thousand separators and 2 decimal places (e.g., 123456.78 -> 123,456.78)"""
        try:
            return "{:,.2f}".format(float(value))
        except (ValueError, TypeError):
            return "0.00"

    def parse_formatted_number(self, formatted_str):
        """Parse formatted number string back to float (e.g., "123,456.78" -> 123456.78)"""
        try:
            # Remove commas and convert to float
            return float(formatted_str.replace(",", ""))
        except (ValueError, TypeError):
            return 0.0

    def update_field_locking(self, ip_no):
        """Lock fields for all IPs except the newest one"""
        if not self.sub_contract_no:
            return

        # Get all IPs to find the newest (highest IP number)
        all_apps = self.manager.get_all_payment_applications(self.sub_contract_no)
        if all_apps:
            newest_ip = max(app["IP"] for app in all_apps)
            is_newest_ip = (ip_no == newest_ip)
        else:
            is_newest_ip = True

        # Lock applied amount fields for all IPs except the newest
        # Previous Applied Amount is always locked (brought from last IP)
        # Certified Amount and Paid Amount are editable for ALL IPs (independent)
        self.spin_accumulated.setReadOnly(not is_newest_ip)
        self.spin_previous.setReadOnly(True)  # Always locked - comes from last IP
        self.spin_this.setReadOnly(not is_newest_ip)
        self.spin_certified.setReadOnly(False)  # Always editable for all IPs
        self.spin_paid.setReadOnly(False)  # Always editable for all IPs

        # Update button states - enabled only for the newest IP
        self.btn_add_item.setEnabled(is_newest_ip)
        self.btn_delete_item.setEnabled(is_newest_ip)
        self.btn_calc_totals.setEnabled(is_newest_ip)

    def refresh_ips(self):
        self.ip_list.clear()
        if not self.sub_contract_no:
            return
            
        apps = self.manager.get_all_payment_applications(self.sub_contract_no)
        for app in apps:
            item = QListWidgetItem(f'IP {app["IP"]} - {app["Draft Date"]}')
            item.setData(Qt.UserRole, app["IP"])
            self.ip_list.addItem(item)
        
        # Do not auto-select any IP on load — leave selection to the user
        # (previously we auto-selected the first IP which forced a selection at startup)

    def on_ip_selected(self, item):
        ip_no = item.data(Qt.UserRole)
        self.current_ip = ip_no
        self.load_ip_details(ip_no)
        self.update_field_locking(ip_no)

    def load_ip_details(self, ip_no):
        if not self.sub_contract_no:
            return

        self.loading_item = True
        app = self.manager.get_payment_application(self.sub_contract_no, ip_no)
        if app:
            self.edit_ip_no.setText(str(app["IP"]))
            self.date_draft.setDate(QDate.fromString(app["Draft Date"], "yyyy-MM-dd") if app["Draft Date"] else QDate.currentDate())
            self.date_issue.setDate(QDate.fromString(app["Issue Date"], "yyyy-MM-dd") if app["Issue Date"] else QDate.currentDate())
            self.date_approved.setDate(QDate.fromString(app["Approved Date"], "yyyy-MM-dd") if app["Approved Date"] else QDate.currentDate())
            self.date_payment.setDate(QDate.fromString(app["Payment Date"], "yyyy-MM-dd") if app["Payment Date"] else QDate.currentDate())
            
            self.spin_accumulated.setText(self.format_number(app["Accumulated Applied Amount"]))
            self.spin_previous.setText(self.format_number(app["Previous Applied Amount"]))
            self.spin_this.setText(self.format_number(app["This Applied Amount"]))
            self.spin_certified.setText(self.format_number(app["Certified Amount"]))
            self.spin_paid.setText(self.format_number(app["Paid Amount"]))
            self.text_remark.setText(app["Remark"])
            
            # Load Items (use refresh helper that provides dropdowns for refs)
            self.refresh_item_table(ip_no)
        self.loading_item = False

    def refresh_item_table(self, ip_no):
        """Populate the items table using comboboxes for reference fields."""
        self.loading_item = True
        self.item_table.setRowCount(0)
        items = self.manager.get_ip_items(self.sub_contract_no, ip_no)

        # Check if this is the newest IP
        all_apps = self.manager.get_all_payment_applications(self.sub_contract_no)
        if all_apps:
            newest_ip = max(app['IP'] for app in all_apps)
            is_newest_ip = (ip_no == newest_ip)
        else:
            is_newest_ip = True

        # Get existing refs for dropdowns
        works_refs = [""] + [w['Works'] for w in self.subcontract_manager.get_sc_works(self.sub_contract_no)]
        vo_objs = self.subcontract_manager.get_sc_vos(self.sub_contract_no)
        vo_refs = [""] + [f"{v['VO ref']} - {v.get('Description','')[:60]}" for v in vo_objs]
        try:
            cc_objs = self.subcontract_manager.db.fetch_all('SELECT * FROM "Contra Charge" WHERE "Deduct To" = ?', (self.sub_contract_no,))
        except Exception:
            cc_objs = []
        cc_refs = [""] + [f"{c['CC No']} - {c.get('Title','')}" for c in cc_objs]

        self.item_table.setRowCount(len(items))
        for row, item_data in enumerate(items):
            # Item no and Type
            self.item_table.setItem(row, 0, QTableWidgetItem(str(item_data['Item'])))
            self.item_table.item(row, 0).setFlags(self.item_table.item(row,0).flags() ^ Qt.ItemIsEditable)
            self.item_table.setItem(row, 1, QTableWidgetItem(item_data.get('Type','') or ""))

            # Contract Work Ref (dropdown)
            cw_combo = QComboBox()
            cw_combo.addItems(works_refs)
            current_cw = item_data.get('Contract Work Ref') or ""
            cw_combo.setCurrentText(current_cw)
            cw_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                cw_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 2, text))
            self.item_table.setCellWidget(row, 2, cw_combo)

            # Works Amount (computed)
            work_amt = 0.0
            if current_cw:
                try:
                    w = next((x for x in self.subcontract_manager.get_sc_works(self.sub_contract_no) if x['Works'] == current_cw), None)
                    if w:
                        qty = float(w.get('Qty') or 0)
                        rate = float(w.get('Rate') or 0)
                        discount = float(w.get('Discount') or 0)
                        work_amt = qty * rate * (1 - discount)
                except Exception:
                    work_amt = 0.0
            work_amt_item = QTableWidgetItem(self.format_number(work_amt))
            work_amt_item.setFlags(work_amt_item.flags() & ~Qt.ItemIsEditable)
            work_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 3, work_amt_item)

            # VO Ref (dropdown with description)
            vo_combo = QComboBox()
            vo_combo.addItems(vo_refs)
            current_vo = item_data.get('VO Ref') or ""
            vo_display = next((ref for ref in vo_refs if ref.startswith(current_vo + " - ") or ref == current_vo), current_vo)
            vo_combo.setCurrentText(vo_display)
            vo_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                vo_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 4, text))
            self.item_table.setCellWidget(row, 3, vo_combo)

            # VO Amount (computed)
            vo_amt = 0.0
            if current_vo:
                try:
                    vo_key = current_vo.split(' - ')[0] if ' - ' in current_vo else current_vo
                    v = self.subcontract_manager.get_sc_vo(vo_key)
                    if v and v.get('Application Amount') is not None:
                        vo_amt = float(v.get('Application Amount') or 0)
                except Exception:
                    vo_amt = 0.0
            vo_amt_item = QTableWidgetItem(self.format_number(vo_amt))
            vo_amt_item.setFlags(vo_amt_item.flags() & ~Qt.ItemIsEditable)
            vo_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 5, vo_amt_item)

            # Contra Charge Ref (dropdown with title)
            cc_combo = QComboBox()
            cc_combo.addItems(cc_refs)
            current_cc = item_data.get('Contra Charge Ref') or ""
            cc_display = next((ref for ref in cc_refs if ref.startswith(current_cc + " - ") or ref == current_cc), current_cc)
            cc_combo.setCurrentText(cc_display)
            cc_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                cc_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 6, text))
            self.item_table.setCellWidget(row, 4, cc_combo)

            # Contra Charge Amount (computed)
            cc_amt = 0.0
            if current_cc:
                try:
                    cc_key = current_cc.split(' - ')[0] if ' - ' in current_cc else current_cc
                    rc = self.subcontract_manager.db.fetch_one('SELECT "Agree Amount" as amt FROM "Contra Charge" WHERE "CC No" = ?', (cc_key,))
                    if rc and rc.get('amt') is not None:
                        cc_amt = float(rc.get('amt') or 0)
                except Exception:
                    cc_amt = 0.0
            cc_amt_item = QTableWidgetItem(self.format_number(cc_amt))
            cc_amt_item.setFlags(cc_amt_item.flags() & ~Qt.ItemIsEditable)
            cc_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 7, cc_amt_item)

            # Description
            self.item_table.setItem(row, 8, QTableWidgetItem(item_data.get('Description','') or ""))

            # Applied Amount - make read-only for all IPs except newest
            applied_item = QTableWidgetItem(self.format_number(item_data.get('Applied Amount') or 0))
            if not is_newest_ip:
                applied_item.setFlags(applied_item.flags() & ~Qt.ItemIsEditable)
                applied_item.setBackground(QColor(240, 240, 240))
            applied_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 9, applied_item)

            # Certified Amount - always editable
            certified_item = QTableWidgetItem(self.format_number(item_data.get('Certified Amount') or 0))
            certified_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 10, certified_item)

            # Paid Amount - always editable
            paid_item = QTableWidgetItem(self.format_number(item_data.get('Paid Amount') or 0))
            paid_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 11, paid_item)

            self.item_table.setItem(row, 12, QTableWidgetItem(item_data.get('Remark','') or ""))
            self.item_table.setItem(row, 13, QTableWidgetItem(str(item_data.get('Item')))) # Hidden ID

        self.loading_item = False

    def on_ref_changed(self, row, col, text):
        """Handle selection changes from reference comboboxes."""
        # Extract key (before ' - ') if display includes description
        ref_value = text.split(' - ')[0] if ' - ' in text else text
        try:
            item_no = int(self.item_table.item(row, 13).text())
        except Exception:
            return

        data = {}
        if col == 2:
            data['Contract Work Ref'] = ref_value
        elif col == 4:
            data['VO Ref'] = ref_value
        elif col == 6:
            data['Contra Charge Ref'] = ref_value
        else:
            return

        self.manager.update_ip_item(self.sub_contract_no, self.current_ip, item_no, data)
        # Update computed amount columns for this row
        self.update_amount_cells(row)

    def update_amount_cells(self, row):
        """Recompute works/VO/contra charge amount cells for a given row."""
        try:
            # Contract Work
            cw_widget = self.item_table.cellWidget(row, 2)
            current_cw = cw_widget.currentText() if cw_widget else ''
            work_amt = 0.0
            if current_cw:
                try:
                    cw_key = current_cw.split(' - ')[0] if ' - ' in current_cw else current_cw
                    w = self.subcontract_manager.db.fetch_one('SELECT Qty, Rate, "Discount" FROM "Sub Con Works" WHERE Subcontract = ? AND Works = ?', (self.sub_contract_no, cw_key))
                    if w:
                        qty = float(w.get('Qty') or 0)
                        rate = float(w.get('Rate') or 0)
                        discount = float(w.get('Discount') or 0)
                        work_amt = qty * rate * (1 - discount)
                except Exception:
                    work_amt = 0.0
            work_amt_item = QTableWidgetItem(self.format_number(work_amt))
            work_amt_item.setFlags(work_amt_item.flags() & ~Qt.ItemIsEditable)
            work_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 3, work_amt_item)

            # VO Amount
            vo_widget = self.item_table.cellWidget(row, 3) if False else self.item_table.cellWidget(row, 3)  # placeholder; vo is at col 3 combo widget
            # Actually VO combo is at col 3 (display) but VO amount is at col 5
            vo_widget = self.item_table.cellWidget(row, 3)
            current_vo = vo_widget.currentText() if vo_widget else ''
            vo_amt = 0.0
            if current_vo:
                try:
                    vo_key = current_vo.split(' - ')[0] if ' - ' in current_vo else current_vo
                    v = self.subcontract_manager.get_sc_vo(vo_key)
                    if v and v.get('Application Amount') is not None:
                        vo_amt = float(v.get('Application Amount') or 0)
                except Exception:
                    vo_amt = 0.0
            vo_amt_item = QTableWidgetItem(self.format_number(vo_amt))
            vo_amt_item.setFlags(vo_amt_item.flags() & ~Qt.ItemIsEditable)
            vo_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 5, vo_amt_item)

            # Contra Charge Amount
            cc_widget = self.item_table.cellWidget(row, 4)
            current_cc = cc_widget.currentText() if cc_widget else ''
            cc_amt = 0.0
            if current_cc:
                try:
                    cc_key = current_cc.split(' - ')[0] if ' - ' in current_cc else current_cc
                    rc = self.subcontract_manager.db.fetch_one('SELECT "Agree Amount" as amt FROM "Contra Charge" WHERE "CC No" = ?', (cc_key,))
                    if rc and rc.get('amt') is not None:
                        cc_amt = float(rc.get('amt') or 0)
                except Exception:
                    cc_amt = 0.0
            cc_amt_item = QTableWidgetItem(self.format_number(cc_amt))
            cc_amt_item.setFlags(cc_amt_item.flags() & ~Qt.ItemIsEditable)
            cc_amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.item_table.setItem(row, 7, cc_amt_item)
        except Exception:
            pass

    def add_ip(self):
        if not self.sub_contract_no:
            QMessageBox.warning(self, "Warning", "Please select a subcontract first.")
            return

        next_ip = self.manager.get_next_ip_no(self.sub_contract_no)
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.manager.create_payment_application(self.sub_contract_no, next_ip, draft_date=today)
        self.refresh_ips()
        # Select the new IP
        for i in range(self.ip_list.count()):
            item = self.ip_list.item(i)
            if item.data(Qt.UserRole) == next_ip:
                self.ip_list.setCurrentItem(item)
                self.on_ip_selected(item)
                break

    def copy_previous_ip(self):
        if not self.sub_contract_no:
            return
        
        # Create new IP first
        next_ip = self.manager.get_next_ip_no(self.sub_contract_no)
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.manager.create_payment_application(self.sub_contract_no, next_ip, draft_date=today)
        
        success = self.manager.copy_previous_ip_items(self.sub_contract_no, next_ip)
        
        self.refresh_ips()
        # Select the new IP
        for i in range(self.ip_list.count()):
            item = self.ip_list.item(i)
            if item.data(Qt.UserRole) == next_ip:
                self.ip_list.setCurrentItem(item)
                self.on_ip_selected(item)
                break
        
        if not success:
            QMessageBox.information(self, "Info", "Created new IP, but could not copy items (maybe no previous IP).")

    def delete_ip(self):
        if not self.current_ip or not self.sub_contract_no:
            return
        
        reply = QMessageBox.question(self, "Delete IP", 
                                     f"Are you sure you want to delete IP {self.current_ip}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.delete_payment_application(self.sub_contract_no, self.current_ip)
            self.refresh_ips()
            self.current_ip = None
            self.item_table.setRowCount(0)
            self.clear_header()

    def clear_header(self):
        self.edit_ip_no.clear()
        self.spin_accumulated.clear()
        self.spin_previous.clear()
        self.spin_this.clear()
        self.spin_certified.clear()
        self.spin_paid.clear()
        self.text_remark.clear()

    def add_item(self):
        if not self.current_ip or not self.sub_contract_no:
            return
        
        next_item_no = self.manager.get_next_item_no(self.sub_contract_no, self.current_ip)
        self.manager.add_ip_item(self.sub_contract_no, self.current_ip, next_item_no, "Contract Work", "", "", "", "New Item", 0.0, 0.0, 0.0, "")
        self.load_ip_details(self.current_ip)

    def delete_item(self):
        if not self.current_ip or not self.sub_contract_no:
            return
        
        current_row = self.item_table.currentRow()
        if current_row < 0:
            return
            
        item_no = int(self.item_table.item(current_row, 13).text()) # Get ID from hidden column
        self.manager.delete_ip_item(self.sub_contract_no, self.current_ip, item_no)
        self.load_ip_details(self.current_ip)

    def on_item_changed(self, item):
        if self.loading_item or not self.current_ip or not self.sub_contract_no:
            return
            
        row = item.row()
        col = item.column()
        
        try:
            item_no = int(self.item_table.item(row, 13).text())
        except Exception:
            return # Row might be initializing

        # Columns: 0=Item, 1=Type, 2=CW Ref, 3=WorksAmt, 4=VO Ref, 5=VOAmt, 6=CC Ref, 7=CCAmt, 8=Desc, 9=Applied, 10=Cert, 11=Paid, 12=Remark
        
        data = {}
        if col == 1:
            data["Type"] = item.text()
        elif col == 8:
            data["Description"] = item.text()
        elif col == 9:
            data["Applied Amount"] = self.parse_formatted_number(item.text())
        elif col == 10:
            data["Certified Amount"] = self.parse_formatted_number(item.text())
        elif col == 11:
            data["Paid Amount"] = self.parse_formatted_number(item.text())
        elif col == 12:
            data["Remark"] = item.text()
        
        if data:
            self.manager.update_ip_item(self.sub_contract_no, self.current_ip, item_no, data)
            
            # If amount changed, reformat it
            if col in [9, 10, 11]:
                self.loading_item = True
                item.setText(self.format_number(self.parse_formatted_number(item.text())))
                self.loading_item = False
                # Also update totals if applied amount changed
                if col == 9:
                    self.calculate_totals()

    def auto_save_header(self):
        if self.loading_item or not self.current_ip or not self.sub_contract_no:
            return
            
        data = {
            "Draft Date": self.date_draft.date().toString("yyyy-MM-dd"),
            "Issue Date": self.date_issue.date().toString("yyyy-MM-dd"),
            "Approved Date": self.date_approved.date().toString("yyyy-MM-dd"),
            "Payment Date": self.date_payment.date().toString("yyyy-MM-dd"),
            "Certified Amount": self.parse_formatted_number(self.spin_certified.text()),
            "Paid Amount": self.parse_formatted_number(self.spin_paid.text()),
            "Remark": self.text_remark.toPlainText()
        }
        self.manager.update_payment_application(self.sub_contract_no, self.current_ip, data)

    def calculate_totals(self):
        if not self.current_ip or not self.sub_contract_no:
            return
            
        # 1. Sum up "Applied Amount" from all items in THIS IP
        items = self.manager.get_ip_items(self.sub_contract_no, self.current_ip)
        this_applied = sum(item["Applied Amount"] for item in items)
        
        # 2. Get "Accumulated Applied Amount" from PREVIOUS IP
        prev_ip = self.current_ip - 1
        prev_app = self.manager.get_payment_application(self.sub_contract_no, prev_ip)
        prev_accumulated = prev_app["Accumulated Applied Amount"] if prev_app else 0.0
        
        # 3. Calculate New Accumulated
        new_accumulated = prev_accumulated + this_applied
        
        # 4. Update Header
        data = {
            "This Applied Amount": this_applied,
            "Previous Applied Amount": prev_accumulated,
            "Accumulated Applied Amount": new_accumulated
        }
        self.manager.update_payment_application(self.sub_contract_no, self.current_ip, data)
        
        # 5. Refresh UI
        self.loading_item = True
        self.spin_this.setText(self.format_number(this_applied))
        self.spin_previous.setText(self.format_number(prev_accumulated))
        self.spin_accumulated.setText(self.format_number(new_accumulated))
        self.loading_item = False
