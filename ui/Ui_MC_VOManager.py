from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QDialogButtonBox, QSplitter
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QDoubleValidator
import os

class Ui_MC_VOManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        # Load UI from .ui file in same directory
        from PyQt5 import uic
        import os
        ui_path = os.path.join(os.path.dirname(__file__), 'MC_VOManager.ui')
        uic.loadUi(ui_path, self)

        # Set validators for amount fields
        validator = QDoubleValidator(0, 1e12, 2)
        try:
            self.lineEdit_app.setValidator(validator)
            self.lineEdit_agree.setValidator(validator)
        except Exception:
            pass

        # Set default dates
        today = QDate.currentDate()
        try:
            self.dateEdit_date.setDate(today)
            self.dateEdit_issue.setDate(today)
        except Exception:
            pass

        # Connect signals
        self.btn_add.clicked.connect(self.add_vo)
        self.btn_update.clicked.connect(self.update_vo)
        self.btn_delete.clicked.connect(self.delete_vo)
        self.vo_list.itemClicked.connect(self.load_details)
        self.btn_add_doc_link.clicked.connect(self.add_document_link)
        self.btn_delete_doc_link.clicked.connect(self.delete_document_link)
        self.btn_add_abortive_link.clicked.connect(self.add_abortive_link)
        self.btn_delete_abortive_link.clicked.connect(self.delete_abortive_link)

        # Initial load
        self.refresh_list()

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

    def refresh_list(self):
        self.vo_list.clear()
        vos = self.manager.get_all_vos()
        for vo in vos:
            item = QListWidgetItem(f"{vo['VO ref']} - {vo['Description'][:30]}...")
            item.setData(32, vo['VO ref'])
            self.vo_list.addItem(item)

    def add_vo(self):
        vo_ref = self.manager.get_next_vo_ref()
        date = self.dateEdit_date.date().toString("yyyy-MM-dd")
        issue_date = self.dateEdit_issue.date().toString("yyyy-MM-dd")
        desc = self.lineEdit_desc.text()
        app_amt = self.parse_formatted_number(self.lineEdit_app.text())
        agree_amt = self.parse_formatted_number(self.lineEdit_agree.text())
        receive = self.checkBox_receive.isChecked()
        dispute = self.checkBox_dispute.isChecked()
        agree = self.checkBox_agree.isChecked()
        reject = self.checkBox_reject.isChecked()
        remark = self.textEdit_remark.toPlainText()

        self.manager.create_vo(vo_ref, date, issue_date, desc, app_amt, agree_amt, receive, dispute, agree, reject, remark)
        self.refresh_list()

        # Select the new VO
        for i in range(self.vo_list.count()):
            item = self.vo_list.item(i)
            if item.data(32) == vo_ref:
                self.vo_list.setCurrentItem(item)
                self.load_details(item)
                break

    def load_vo_by_ref(self, vo_ref):
        """Select the Main Contract VO by reference and load its details. Returns True if selected."""
        try:
            # Ensure list is up-to-date
            self.refresh_list()
            for i in range(self.vo_list.count()):
                item = self.vo_list.item(i)
                try:
                    if item.data(32) == vo_ref:
                        self.vo_list.setCurrentItem(item)
                        self.load_details(item)
                        return True
                except Exception:
                    continue
            QMessageBox.information(self, 'VO Not Found', f'VO {vo_ref} was not found in Main Contract VO list.')
            return False
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load VO: {e}')
            return False

    def update_vo(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO to update.")
            return

        vo_ref = current_item.data(32)
        data = {
            "Date": self.dateEdit_date.date().toString("yyyy-MM-dd"),
            "Issue Date": self.dateEdit_issue.date().toString("yyyy-MM-dd"),
            "Description": self.lineEdit_desc.text(),
            "Application Amount": self.parse_formatted_number(self.lineEdit_app.text()),
            "Agree Amount": self.parse_formatted_number(self.lineEdit_agree.text()),
            "Receive Assessment": self.checkBox_receive.isChecked(),
            "Dispute": self.checkBox_dispute.isChecked(),
            "Agree": self.checkBox_agree.isChecked(),
            "Reject": self.checkBox_reject.isChecked(),
            "Remark": self.textEdit_remark.toPlainText()
        }
        self.manager.update_vo(vo_ref, data)
        self.refresh_list()

    def delete_vo(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO to delete.")
            return

        vo_ref = current_item.data(32)
        self.manager.delete_vo(vo_ref)
        self.refresh_list()
        self.clear_form()

    def load_details(self, item):
        vo_ref = item.data(32)
        vo = self.manager.get_vo(vo_ref)
        if vo:
            self.lineEdit_ref.setText(vo['VO ref'])
            self.dateEdit_date.setDate(QDate.fromString(vo['Date'], "yyyy-MM-dd"))
            self.dateEdit_issue.setDate(QDate.fromString(vo['Issue Date'], "yyyy-MM-dd"))
            self.lineEdit_desc.setText(vo['Description'])
            self.lineEdit_app.setText(self.format_number(vo['Application Amount']))
            self.lineEdit_agree.setText(self.format_number(vo['Agree Amount']))
            self.checkBox_receive.setChecked(vo['Receive Assessment'])
            self.checkBox_dispute.setChecked(vo['Dispute'])
            self.checkBox_agree.setChecked(vo['Agree'])
            self.checkBox_reject.setChecked(vo['Reject'])
            self.textEdit_remark.setPlainText(vo['Remark'])

            # Populate link tables
            self.populate_document_table(vo_ref)
            self.populate_abortive_table(vo_ref)

            # Update IP totals for this VO
            try:
                totals = self.manager.get_vo_payment_totals(vo_ref)
                applied = totals.get('Applied', 0.0) or 0.0
                certified = totals.get('Certified', 0.0) or 0.0
                paid = totals.get('Paid', 0.0) or 0.0

                # Calculate percentages (percentage of applied)
                cert_pct = (certified / applied * 100) if applied else 0.0
                paid_pct = (paid / applied * 100) if applied else 0.0

                self.label_totals_applied.setText(self.format_number(applied))
                self.label_totals_certified.setText(f"{self.format_number(certified)} ({cert_pct:.2f}%)")
                self.label_totals_paid.setText(f"{self.format_number(paid)} ({paid_pct:.2f}%)")
            except Exception:
                # If the manager or query fails, show zeros
                self.label_totals_applied.setText("0.00")
                self.label_totals_certified.setText("0.00 (0.00%)")
                self.label_totals_paid.setText("0.00 (0.00%)")

    def clear_form(self):
        self.lineEdit_ref.clear()
        self.lineEdit_desc.clear()
        self.textEdit_remark.clear()
        self.doubleSpinBox_app.setValue(0)
        self.doubleSpinBox_agree.setValue(0)
        self.checkBox_receive.setChecked(False)
        self.checkBox_dispute.setChecked(False)
        self.checkBox_agree.setChecked(False)
        self.checkBox_reject.setChecked(False)

    def populate_document_table(self, vo_ref):
        links = self.manager.get_document_links(vo_ref)
        self.table_docs.setRowCount(len(links))
        for row, link in enumerate(links):
            self.table_docs.setItem(row, 0, QTableWidgetItem(link['Doc Ref']))
            self.table_docs.setItem(row, 1, QTableWidgetItem(link['Title']))
            self.table_docs.setItem(row, 2, QTableWidgetItem(link['Remark']))

    def populate_abortive_table(self, vo_ref):
        links = self.manager.get_abortive_links(vo_ref)
        self.table_abortive.setRowCount(len(links))
        for row, link in enumerate(links):
            self.table_abortive.setItem(row, 0, QTableWidgetItem(link['Abortive Work ref']))
            self.table_abortive.setItem(row, 1, QTableWidgetItem(link['Description']))
            self.table_abortive.setItem(row, 2, QTableWidgetItem(link['Remark']))

    def add_document_link(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO first.")
            return
        vo_ref = current_item.data(32)

        # Get documents
        docs = self.manager.db.fetch_all('SELECT File, Title FROM "Document Manager"')
        if not docs:
            QMessageBox.information(self, "No Documents", "No documents found to link.")
            return

        items = [f"{d['File']} - {d.get('Title','')}" for d in docs]
        from PyQt5.QtWidgets import QInputDialog
        selected, ok = QInputDialog.getItem(self, "Select Document", "Document:", items, 0, False)
        if not ok or not selected:
            return
        doc_ref = selected.split(' - ')[0]
        remark, ok2 = QInputDialog.getText(self, "Link Remark", "Enter remark (optional):")
        if not ok2:
            remark = ""
        try:
            self.manager.link_to_document(vo_ref, doc_ref, remark)
            QMessageBox.information(self, "Linked", f"Document {doc_ref} linked to VO {vo_ref}.")
            self.populate_document_table(vo_ref)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add document link: {str(e)}")

    def delete_document_link(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO first.")
            return
        vo_ref = current_item.data(32)
        row = self.table_docs.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Document Selected", "Please select a document link to delete.")
            return
        doc_ref = self.table_docs.item(row, 0).text()
        try:
            self.manager.delete_document_link(vo_ref, doc_ref)
            QMessageBox.information(self, "Deleted", f"Deleted link to document {doc_ref}.")
            self.populate_document_table(vo_ref)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete document link: {str(e)}")

    def add_abortive_link(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO first.")
            return
        vo_ref = current_item.data(32)

        # Get abortive works
        docs = self.manager.db.fetch_all('SELECT "Abortive Ref", Description FROM "Abortive Work Record"')
        if not docs:
            QMessageBox.information(self, "No Abortive Works", "No abortive works found to link.")
            return

        items = [f"{d['Abortive Ref']} - {d.get('Description','')}" for d in docs]
        from PyQt5.QtWidgets import QInputDialog
        selected, ok = QInputDialog.getItem(self, "Select Abortive Work", "Abortive Ref:", items, 0, False)
        if not ok or not selected:
            return
        abortive_ref = selected.split(' - ')[0]
        remark, ok2 = QInputDialog.getText(self, "Link Remark", "Enter remark (optional):")
        if not ok2:
            remark = ""
        try:
            self.manager.link_to_abortive(vo_ref, abortive_ref, remark)
            QMessageBox.information(self, "Linked", f"Abortive {abortive_ref} linked to VO {vo_ref}.")
            self.populate_abortive_table(vo_ref)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add abortive link: {str(e)}")

    def delete_abortive_link(self):
        current_item = self.vo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No VO Selected", "Please select a VO first.")
            return
        vo_ref = current_item.data(32)
        row = self.table_abortive.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Abortive Selected", "Please select an abortive link to delete.")
            return
        abortive_ref = self.table_abortive.item(row, 0).text()
        try:
            self.manager.delete_abortive_link(vo_ref, abortive_ref)
            QMessageBox.information(self, "Deleted", f"Deleted abortive link {abortive_ref}.")
            self.populate_abortive_table(vo_ref)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete abortive link: {str(e)}")