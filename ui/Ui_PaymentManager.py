from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
                             QListWidgetItem, QFormLayout, QLabel, QLineEdit, QDateEdit, 
                             QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QMessageBox, QMenu, QAction, QComboBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QColor
from PyQt5 import uic
import os
import datetime

class Ui_PaymentManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()
        self.refresh_ips()

    def init_ui(self):
        # Load UI from .ui file so it can be reviewed in Qt Designer
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ui_path = os.path.join(root_path, 'ui', 'Payment_Manager.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception:
            # Fall back to dynamic UI if load fails (keeps backwards compatibility)
            pass

        # Prepare item table columns and headers (13 columns expected)
        self.item_table.setColumnCount(13)
        headers = ["Item", "Type", "BQ Ref", "VO Ref", "DOC Ref", "Description",
                   "BQ Amount", "VO Amount", "Applied", "Certified", "Paid", "Remark", "ID"]
        try:
            self.item_table.setHorizontalHeaderLabels(headers)
            self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.item_table.hideColumn(12)  # hide ID column
        except Exception:
            pass

        # Connect signals
        try:
            self.ip_list.itemClicked.connect(self.on_ip_selected)
            self.btn_add_ip.clicked.connect(self.add_ip)
            self.btn_copy_ip.clicked.connect(self.copy_previous_ip)
            self.btn_delete_ip.clicked.connect(self.delete_ip)

            self.btn_add_item.clicked.connect(self.add_item)
            self.btn_delete_item.clicked.connect(self.delete_item)
            self.btn_calc_totals.clicked.connect(self.calculate_totals)

            self.item_table.itemChanged.connect(self.on_item_changed)

            # Auto-save signals
            self.date_draft.dateChanged.connect(self.auto_save_header)
            self.date_issue.dateChanged.connect(self.auto_save_header)
            self.date_approved.dateChanged.connect(self.auto_save_header)
            self.date_payment.dateChanged.connect(self.auto_save_header)
            self.spin_certified.textChanged.connect(self.auto_save_header)
            self.spin_paid.textChanged.connect(self.auto_save_header)
            self.text_remark.textChanged.connect(self.auto_save_header)
        except Exception:
            pass

        # Validators for numeric fields
        try:
            validator = QDoubleValidator(0, 1e12, 2)
            self.spin_certified.setValidator(validator)
            self.spin_paid.setValidator(validator)
        except Exception:
            pass

        # Initial state
        self.current_ip = None
        self.loading_item = False

    def format_number(self, value):
        """Format number with thousand separators and 2 decimal places (e.g., 123456.78 -> 123,456.78)"""
        try:
            return "{:,.2f}".format(float(value))
        except (ValueError, TypeError):
            return "0.00"

    def parse_formatted_number(self, formatted_str):
        """Parse formatted number string back to float (e.g., '123,456.78' -> 123456.78)"""
        try:
            # Remove commas and convert to float
            return float(formatted_str.replace(',', ''))
        except (ValueError, TypeError):
            return 0.0

    def update_field_locking(self, ip_no):
        """Lock fields for all IPs except the newest one"""
        # Get all IPs to find the newest (highest IP number)
        all_apps = self.manager.get_all_payment_applications()
        if all_apps:
            newest_ip = max(app['IP'] for app in all_apps)
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
        apps = self.manager.get_all_payment_applications()
        for app in apps:
            item = QListWidgetItem(f"IP {app['IP']} - {app['Draft Date']}")
            item.setData(Qt.UserRole, app['IP'])
            self.ip_list.addItem(item)

    def on_ip_selected(self, item):
        ip_no = item.data(Qt.UserRole)
        self.current_ip = ip_no
        self.load_ip_data(ip_no)

    def load_ip_data(self, ip_no):
        app = self.manager.get_payment_application(ip_no)
        if not app:
            return
            
        self.edit_ip_no.setText(str(app['IP']))
        self.set_date(self.date_draft, app['Draft Date'])
        self.set_date(self.date_issue, app['Issue Date'])
        self.set_date(self.date_approved, app['Approved Date'])
        self.set_date(self.date_payment, app['Payment Date'])
        
        self.spin_accumulated.setText(self.format_number(app['Accumulated Applied Amount'] or 0))
        self.spin_previous.setText(self.format_number(app['Previous Applied Amount'] or 0))
        self.spin_this.setText(self.format_number(app['This Applied Amount'] or 0))
        self.spin_certified.setText(self.format_number(app['Certified Amount'] or 0))
        self.spin_paid.setText(self.format_number(app['Paid Amount'] or 0))
        self.text_remark.setPlainText(app['Remark'] or "")
        
        self.refresh_item_table(ip_no)
        self.update_field_locking(ip_no)

    def set_date(self, date_edit, date_str):
        if date_str:
            date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        else:
            date_edit.setDate(QDate.currentDate())

    def refresh_item_table(self, ip_no):
        self.loading_item = True
        self.item_table.setRowCount(0)
        items = self.manager.get_ip_items(ip_no)
        
        # Check if this is the newest IP
        all_apps = self.manager.get_all_payment_applications()
        if all_apps:
            newest_ip = max(app['IP'] for app in all_apps)
            is_newest_ip = (ip_no == newest_ip)
        else:
            is_newest_ip = True
        
        # Get existing refs for dropdowns
        bq_refs = [""] + self.manager.get_existing_bq_refs()
        vo_refs = [""] + self.manager.get_existing_vo_refs()
        doc_refs = [""] + self.manager.get_existing_doc_refs()
        
        self.item_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.item_table.setItem(row, 0, QTableWidgetItem(str(item['Item'])))
            self.item_table.setItem(row, 1, QTableWidgetItem(item['Type'] or ""))
            self.item_table.setItem(row, 5, QTableWidgetItem(item['Description'] or ""))
            
            # Applied Amount - make read-only for all IPs except newest
            applied_item = QTableWidgetItem(self.format_number(item['Applied Amount'] or 0))
            if not is_newest_ip:
                applied_item.setFlags(applied_item.flags() & ~Qt.ItemIsEditable)
                applied_item.setBackground(QColor(240, 240, 240))  # Light grey background
            # BQ Ref combobox - disable for all IPs except newest
            bq_combo = QComboBox()
            bq_combo.addItems(bq_refs)
            current_bq = item['BQ Ref'] or ""
            bq_display = next((ref for ref in bq_refs if ref.startswith(current_bq + " - ") or ref == current_bq), current_bq)
            bq_combo.setCurrentText(bq_display)
            bq_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                bq_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 2, text))
            self.item_table.setCellWidget(row, 2, bq_combo)

            # VO Ref combobox - disable for all IPs except newest
            vo_combo = QComboBox()
            vo_combo.addItems(vo_refs)
            current_vo = item['VO Ref'] or ""
            vo_display = next((ref for ref in vo_refs if ref.startswith(current_vo + " - ") or ref == current_vo), current_vo)
            vo_combo.setCurrentText(vo_display)
            vo_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                vo_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 3, text))
            self.item_table.setCellWidget(row, 3, vo_combo)

            # DOC Ref combobox
            doc_combo = QComboBox()
            doc_combo.addItems(doc_refs)
            current_doc = item['DOC Ref'] or ""
            doc_display = next((ref for ref in doc_refs if ref.startswith(current_doc + " - ") or ref == current_doc), current_doc)
            doc_combo.setCurrentText(doc_display)
            doc_combo.setEnabled(is_newest_ip)
            if is_newest_ip:
                doc_combo.currentTextChanged.connect(lambda text, r=row: self.on_ref_changed(r, 4, text))
            self.item_table.setCellWidget(row, 4, doc_combo)

            # Description
            self.item_table.setItem(row, 5, QTableWidgetItem(item['Description'] or ""))

            # BQ Amount (read-only; derived from BQ Ref)
            bq_amt = 0.0
            if current_bq:
                bq_amt = self.manager.get_bq_amount(current_bq)
            bq_item = QTableWidgetItem(self.format_number(bq_amt))
            bq_item.setFlags(bq_item.flags() & ~Qt.ItemIsEditable)
            self.item_table.setItem(row, 6, bq_item)

            # VO Amount (read-only; derived from VO Ref application amount)
            vo_amt = 0.0
            if current_vo:
                vo_amt = self.manager.get_vo_application_amount(current_vo)
            vo_item = QTableWidgetItem(self.format_number(vo_amt))
            vo_item.setFlags(vo_item.flags() & ~Qt.ItemIsEditable)
            self.item_table.setItem(row, 7, vo_item)

            # Applied Amount - make read-only for all IPs except newest (now at col 8)
            applied_item = QTableWidgetItem(self.format_number(item['Applied Amount'] or 0))
            if not is_newest_ip:
                applied_item.setFlags(applied_item.flags() & ~Qt.ItemIsEditable)
                applied_item.setBackground(QColor(240, 240, 240))  # Light grey background
            self.item_table.setItem(row, 8, applied_item)

            # Certified Amount - always editable for all IPs (now at col 9)
            certified_item = QTableWidgetItem(self.format_number(item['Certified Amount'] or 0))
            self.item_table.setItem(row, 9, certified_item)

            # Paid Amount - always editable for all IPs (now at col 10)
            paid_item = QTableWidgetItem(self.format_number(item['Paid Amount'] or 0))
            self.item_table.setItem(row, 10, paid_item)

            # Remark (now at col 11)
            self.item_table.setItem(row, 11, QTableWidgetItem(item['Remark'] or ""))

            # Hidden ID (now at col 12)
            self.item_table.setItem(row, 12, QTableWidgetItem(str(item['Item']))) # Hidden ID
            self.item_table.item(row, 0).setFlags(self.item_table.item(row, 0).flags() ^ Qt.ItemIsEditable)
            
        self.loading_item = False

    def add_ip(self):
        next_ip = self.manager.get_next_ip_no()
        today = datetime.date.today().isoformat()
        self.manager.create_payment_application(next_ip, draft_date=today)
        self.refresh_ips()
        # Select new IP
        for i in range(self.ip_list.count()):
            if self.ip_list.item(i).data(Qt.UserRole) == next_ip:
                self.ip_list.setCurrentRow(i)
                self.on_ip_selected(self.ip_list.item(i))
                break

    def copy_previous_ip(self):
        if not self.current_ip:
            return
        
        reply = QMessageBox.question(self, 'Copy Previous IP', 
                                     f"Are you sure you want to copy items from previous IP to IP {self.current_ip}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = self.manager.copy_previous_ip_items(self.current_ip)
            if success:
                self.refresh_item_table(self.current_ip)
                self.update_field_locking(self.current_ip)
                self.calculate_totals()
            else:
                QMessageBox.warning(self, "Copy Failed", "Could not copy items (maybe no previous IP or items).")

    def delete_ip(self):
        if not self.current_ip:
            return
        
        reply = QMessageBox.question(self, 'Delete IP', 
                                     f"Are you sure you want to delete IP {self.current_ip}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.manager.delete_payment_application(self.current_ip)
            self.refresh_ips()
            self.current_ip = None
            self.item_table.setRowCount(0)
            # Clear header fields...

    def auto_save_header(self):
        if not self.current_ip:
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
        self.manager.update_payment_application(self.current_ip, data)
        self.refresh_ips() # To update date in list

    def add_item(self):
        if not self.current_ip:
            return
            
        next_item = self.manager.get_next_item_no(self.current_ip)
        self.manager.add_ip_item(self.current_ip, next_item, "", "", "", "", "", 0, 0, 0, "")
        self.refresh_item_table(self.current_ip)
        self.update_field_locking(self.current_ip)

    def delete_item(self):
        row = self.item_table.currentRow()
        if row < 0:
            return
            
        item_no = int(self.item_table.item(row, 0).text())
        self.manager.delete_ip_item(self.current_ip, item_no)
        self.refresh_item_table(self.current_ip)
        self.update_field_locking(self.current_ip)

    def on_ref_changed(self, row, col, text):
        if self.loading_item or not self.current_ip:
            return

        item_no = int(self.item_table.item(row, 0).text())

        # Map column to field (updated for new columns)
        fields = ["Item", "Type", "BQ Ref", "VO Ref", "DOC Ref", "Description", "BQ Amount", "VO Amount", "Applied Amount", "Certified Amount", "Paid Amount", "Remark"]
        field = fields[col]

        # Extract the ref part from the display text (before " - ")
        ref_value = text.split(" - ")[0] if " - " in text else text

        # Update the underlying ref field in DB
        data = {field: ref_value} if field in ["BQ Ref", "VO Ref", "DOC Ref", "Description", "Type"] else {}
        if data:
            self.manager.update_ip_item(self.current_ip, item_no, data)

        # If BQ ref changed, update BQ Amount display
        if col == 2:
            bq_amt = self.manager.get_bq_amount(ref_value)
            bq_item = QTableWidgetItem(self.format_number(bq_amt))
            bq_item.setFlags(bq_item.flags() & ~Qt.ItemIsEditable)
            self.loading_item = True
            self.item_table.setItem(row, 6, bq_item)
            self.loading_item = False

        # If VO ref changed, update VO Amount display
        if col == 3:
            vo_amt = self.manager.get_vo_application_amount(ref_value)
            vo_item = QTableWidgetItem(self.format_number(vo_amt))
            vo_item.setFlags(vo_item.flags() & ~Qt.ItemIsEditable)
            self.loading_item = True
            self.item_table.setItem(row, 7, vo_item)
            self.loading_item = False

    def on_item_changed(self, item):
        if self.loading_item:
            return

        row = item.row()
        col = item.column()

        # Skip combobox columns (2,3,4) as they are handled separately
        if col in [2, 3, 4]:
            return

        # Check if this IP is NOT the newest - if so, Applied Amount should be locked
        # Certified Amount and Paid Amount are always editable for all IPs
        all_apps = self.manager.get_all_payment_applications()
        if all_apps:
            newest_ip = max(app['IP'] for app in all_apps)
            is_newest_ip = (self.current_ip == newest_ip)
        else:
            is_newest_ip = True

        # Applied Amount is now at col 8
        if not is_newest_ip and col == 8:
            return  # Don't allow editing of Applied Amount for non-newest IPs

        item_no = int(self.item_table.item(row, 0).text())

        # Map column to field (updated for new table layout)
        fields = ["Item", "Type", "BQ Ref", "VO Ref", "DOC Ref", "Description", "BQ Amount", "VO Amount", "Applied Amount", "Certified Amount", "Paid Amount", "Remark"]
        field = fields[col]
        value = item.text()

        # Handle numeric fields
        if field in ["Applied Amount", "Certified Amount", "Paid Amount"]:
            try:
                # Remove commas from formatted numbers before converting to float
                value = float(value.replace(',', ''))
            except ValueError:
                value = 0.0

        # Do not allow editing of derived columns
        if field in ["BQ Amount", "VO Amount"]:
            return

        data = {field: value}
        self.manager.update_ip_item(self.current_ip, item_no, data)

        # If Applied changed, recalc totals
        if field == "Applied Amount":
            self.calculate_totals()

    def calculate_totals(self):
        if not self.current_ip:
            return
            
        self.manager.calculate_ip_totals(self.current_ip)
        self.load_ip_data(self.current_ip) # Reload header to show new totals

    def load_vo_by_ref(self, vo_ref):
        """Find a payment application (IP) that contains an item referencing `vo_ref`,
        select that IP and highlight the corresponding item row. Returns True if found."""
        try:
            apps = self.manager.get_all_payment_applications()
            if not apps:
                QMessageBox.information(self, 'VO Not Found', f'VO {vo_ref} was not found in any Payment Application.')
                return False

            for app in apps:
                ip_no = app['IP']
                items = self.manager.get_ip_items(ip_no)
                for idx, itm in enumerate(items):
                    if (itm.get('VO Ref') or '') == vo_ref:
                        # Select IP in list
                        for i in range(self.ip_list.count()):
                            if self.ip_list.item(i).data(Qt.UserRole) == ip_no:
                                self.ip_list.setCurrentRow(i)
                                # Load IP data (synchronously) and then select the row
                                self.on_ip_selected(self.ip_list.item(i))
                                try:
                                    self.item_table.selectRow(idx)
                                    if self.item_table.item(idx, 0):
                                        self.item_table.scrollToItem(self.item_table.item(idx, 0))
                                except Exception:
                                    pass
                                return True
            QMessageBox.information(self, 'VO Not Found', f'VO {vo_ref} was not found in any Payment Application.')
            return False
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to locate VO in payments: {e}')
            return False
