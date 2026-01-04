import os
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, Qt

class Ui_SC_ContraChargeManager(QWidget):
    def __init__(self, manager, subcontract_manager=None):
        super().__init__()
        self.manager = manager
        self.subcontract_manager = subcontract_manager
        self._loaded_rec = None

        # Load UI from .ui file
        from PyQt5 import uic
        ui_path = os.path.join(os.path.dirname(__file__), 'SC_ContraChargeManager.ui')
        uic.loadUi(ui_path, self)

        # Small UI defaults
        try:
            self.doubleSpinBox_agree.setPrefix('HK$ ')
            self.doubleSpinBox_agree.setDecimals(2)
            self.doubleSpinBox_agree.setToolTip('Agree amount (auto-saved)')
        except Exception:
            pass

        # Ensure table headers are labelled (UI may not include header texts)
        try:
            self.table_ccs.setHorizontalHeaderLabels(["CC No", "Title", "Agree Amount", "Deduct To"])
            self.table_items.setHorizontalHeaderLabels(["Item ID", "Description", "Qty", "Unit", "Rate", "Admin Rate", "Admin Charge", "Total Amount", "Give to"])
            self.table_docs.setHorizontalHeaderLabels(["Doc Ref", "Title", "Remark"])
        except Exception:
            pass

        # UX: column sizing and tooltips
        try:
            from PyQt5.QtWidgets import QHeaderView
            # Left list: allow user to resize columns interactively; keep Title stretching by default
            self.table_ccs.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            for col in range(self.table_ccs.columnCount()):
                if col != 1:
                    self.table_ccs.horizontalHeader().setSectionResizeMode(col, QHeaderView.Interactive)
            try:
                self.table_ccs.horizontalHeaderItem(2).setToolTip('Agree amount (HK$)')
            except Exception:
                pass

            # Items: allow user to resize all columns (including Description) and set sensible defaults
            hdr_items = self.table_items.horizontalHeader()
            try:
                # Make Description adjustable (Interactive) so users can control its width
                for col in range(self.table_items.columnCount()):
                    hdr_items.setSectionResizeMode(col, QHeaderView.Interactive)
                # Provide sensible default widths
                try:
                    self.table_items.setColumnWidth(0, 80)   # Item ID (hidden)
                    self.table_items.setColumnWidth(1, 360)  # Description
                    self.table_items.setColumnWidth(2, 80)   # Qty
                    self.table_items.setColumnWidth(3, 80)   # Unit
                    self.table_items.setColumnWidth(4, 100)  # Rate
                    self.table_items.setColumnWidth(5, 100)  # Admin Rate
                    self.table_items.setColumnWidth(6, 120)  # Admin Charge
                    self.table_items.setColumnWidth(7, 120)  # Total Amount
                    self.table_items.setColumnWidth(8, 140)  # Give to
                except Exception:
                    pass
                hdr_items.setStretchLastSection(False)
                hdr_items.setSectionsMovable(True)
                hdr_items.setSectionsClickable(True)
                try:
                    from PyQt5.QtWidgets import QAbstractItemView
                    self.table_items.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
                except Exception:
                    pass
                try:
                    self.table_items.horizontalHeaderItem(4).setToolTip('Rate (HK$)')
                    self.table_items.horizontalHeaderItem(7).setToolTip('Total amount (HK$)')
                except Exception:
                    pass
            except Exception:
                pass

            # Docs: make all columns user-interactive with default widths
            hdr = self.table_docs.horizontalHeader()
            try:
                # Set Interactive mode for all columns so users can resize any column
                for col in range(self.table_docs.columnCount()):
                    hdr.setSectionResizeMode(col, QHeaderView.Interactive)
                # Provide sensible default widths so remark column can be grabbed immediately
                try:
                    self.table_docs.setColumnWidth(0, 120)  # Doc Ref
                    self.table_docs.setColumnWidth(1, 320)  # Title
                    self.table_docs.setColumnWidth(2, 260)  # Remark
                except Exception:
                    pass
                # Allow moving sections and clickable headers
                hdr.setStretchLastSection(False)
                hdr.setSectionsMovable(True)
                hdr.setSectionsClickable(True)
                # Allow horizontal scrolling if user expands beyond available space
                try:
                    from PyQt5.QtWidgets import QAbstractItemView
                    self.table_docs.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass

        try:
            self.table_items.hideColumn(0)
            self.table_items.itemChanged.connect(self.on_item_changed)
        except Exception:
            pass
        try:
            # Clicking a document should navigate to Document Manager and select the document
            self.table_docs.cellClicked.connect(self.on_doc_link_clicked)
        except Exception:
            pass

        # Wire buttons and interactions
        try:
            self.table_ccs.cellClicked.connect(self.on_table_cc_clicked)
        except Exception:
            pass
        try:
            self.btn_add.clicked.connect(self.add_cc)
            self.btn_delete.clicked.connect(self.delete_cc)
            self.btn_add_item.clicked.connect(self.add_item)
            self.btn_delete_item.clicked.connect(self.delete_item)
            self.btn_add_doc.clicked.connect(self.add_document_link)
            self.btn_delete_doc.clicked.connect(self.delete_document_link)
        except Exception:
            pass

        # Autosave hooks
        try:
            self.lineEdit_title.editingFinished.connect(self.auto_save_cc)
            self.doubleSpinBox_agree.valueChanged.connect(lambda: self.auto_save_cc())
            self.dateEdit_date.dateChanged.connect(lambda: self.auto_save_cc())
            self.textEdit_reason.textChanged.connect(lambda: self.auto_save_cc())
            self.comboBox_deduct.currentIndexChanged.connect(lambda: self.auto_save_cc())
        except Exception:
            pass

        self.refresh_list()
        self.populate_deduct_combo()
        # Loading flag to avoid recursion when programmatically updating table_items
        self.loading_items = False

    def populate_deduct_combo(self):
        self.comboBox_deduct.clear()
        if self.subcontract_manager:
            scs = self.subcontract_manager.get_all_subcontracts() if hasattr(self.subcontract_manager, 'get_all_subcontracts') else []
            subs = [s['Sub Contract No'] for s in scs]
            self.comboBox_deduct.addItems([""] + subs)

    def format_number(self, value):
        try:
            return "{:,.2f}".format(float(value))
        except Exception:
            return "0.00"

    def refresh_list(self):
        ccs = self.manager.get_all_contra_charges()
        self.table_ccs.setRowCount(len(ccs))
        for r, cc in enumerate(ccs):
            try:
                self.table_ccs.setItem(r, 0, QTableWidgetItem(str(cc.get('CC No'))))
                self.table_ccs.setItem(r, 1, QTableWidgetItem(str(cc.get('Title'))))
                amt = QTableWidgetItem(self.format_number(cc.get('Agree Amount', 0)))
                amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_ccs.setItem(r, 2, amt)
                self.table_ccs.setItem(r, 3, QTableWidgetItem(str(cc.get('Deduct To') or "")))
            except Exception:
                continue
        try:
            self.table_ccs.resizeColumnsToContents()
        except Exception:
            pass

    def add_cc(self):
        # Create a new CC with next ref
        next_ref = f"CC-{len(self.manager.get_all_contra_charges())+1:03d}"
        today = QDate.currentDate().toString("yyyy-MM-dd")
        self.manager.create_contra_charge(next_ref, today, "", "", 0, "")
        self.refresh_list()
        # select created
        for r in range(self.table_ccs.rowCount()):
            try:
                if self.table_ccs.item(r, 0).text() == next_ref:
                    self.table_ccs.selectRow(r)
                    self.load_details_by_ref(next_ref)
                    break
            except Exception:
                continue

    def delete_cc(self):
        row = self.table_ccs.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No CC Selected', 'Please select a Contra Charge first.')
            return
        cc_no = self.table_ccs.item(row, 0).text()
        self.manager.delete_contra_charge(cc_no)
        self.refresh_list()
        self.clear_form()

    def on_table_cc_clicked(self, row, column):
        try:
            cc_no = self.table_ccs.item(row, 0).text()
            self.load_details_by_ref(cc_no)
        except Exception:
            pass

    def load_details_by_ref(self, cc_no):
        cc = self.manager.get_contra_charge(cc_no)
        if not cc:
            return
        self.lineEdit_cc_no.setText(cc.get('CC No'))
        try:
            self.dateEdit_date.setDate(QDate.fromString(cc.get('Date',''), 'yyyy-MM-dd'))
        except Exception:
            pass
        self.lineEdit_title.setText(cc.get('Title',''))
        self.textEdit_reason.setPlainText(cc.get('Reason',''))
        try:
            self.doubleSpinBox_agree.setValue(cc.get('Agree Amount') or 0)
        except Exception:
            pass
        try:
            if cc.get('Deduct To'):
                self.comboBox_deduct.setCurrentText(cc.get('Deduct To'))
        except Exception:
            pass
        # cache
        try:
            self._loaded_rec = cc.copy()
        except Exception:
            self._loaded_rec = cc
        # populate items
        self.populate_items(cc_no)

    def clear_form(self):
        self.lineEdit_cc_no.clear()
        self.lineEdit_title.clear()
        self.textEdit_reason.clear()
        self.doubleSpinBox_agree.setValue(0)
        self.comboBox_deduct.setCurrentIndex(0)
        self.table_items.setRowCount(0)

    def auto_save_cc(self):
        cc_no = self.lineEdit_cc_no.text()
        if not cc_no:
            return
        data = {
            'Date': self.dateEdit_date.date().toString('yyyy-MM-dd'),
            'Title': self.lineEdit_title.text(),
            'Reason': self.textEdit_reason.toPlainText(),
            'Agree Amount': self.doubleSpinBox_agree.value(),
            'Deduct To': self.comboBox_deduct.currentText()
        }
        base = getattr(self, '_loaded_rec', None)
        if base:
            changed = {k: v for k, v in data.items() if base.get(k) != v}
            if not changed:
                return
        else:
            changed = data
        try:
            self.manager.update_contra_charge(cc_no, changed)
            rec = self.manager.get_contra_charge(cc_no)
            try:
                self._loaded_rec = rec.copy()
            except Exception:
                self._loaded_rec = rec
            self.refresh_list()
        except Exception as e:
            QMessageBox.warning(self, 'Save Failed', f'Failed to save: {e}')

    def populate_items(self, cc_no):
        items = self.manager.get_items(cc_no)
        # Prevent on_item_changed recursion while updating table
        self.loading_items = True
        try:
            self.table_items.setRowCount(len(items))
            for r, it in enumerate(items):
                try:
                    self.table_items.setItem(r, 0, QTableWidgetItem(str(it.get('Item ID'))))
                    self.table_items.setItem(r, 1, QTableWidgetItem(str(it.get('Description',''))))
                    # Qty
                    try:
                        qty_item = QTableWidgetItem(self.format_number(it.get('Qty') or 0))
                        qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_items.setItem(r, 2, qty_item)
                    except Exception:
                        pass
                    # Unit
                    try:
                        self.table_items.setItem(r, 3, QTableWidgetItem(str(it.get('Unit',''))))
                    except Exception:
                        pass
                    # Rate
                    try:
                        rate_item = QTableWidgetItem(self.format_number(it.get('Rate') or 0))
                        rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_items.setItem(r, 4, rate_item)
                    except Exception:
                        pass
                    # Admin Rate
                    try:
                        admin_rate_item = QTableWidgetItem(self.format_number(it.get('Admin Rate') or 0))
                        admin_rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_items.setItem(r, 5, admin_rate_item)
                    except Exception:
                        pass
                    # Admin Charge
                    try:
                        admin_charge_item = QTableWidgetItem(self.format_number(it.get('Admin Charge') or 0))
                        admin_charge_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_items.setItem(r, 6, admin_charge_item)
                    except Exception:
                        pass
                    # Total Amount
                    try:
                        total_item = QTableWidgetItem(self.format_number(it.get('Total Amount') or 0))
                        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.table_items.setItem(r, 7, total_item)
                    except Exception:
                        pass
                    # Give to
                    try:
                        self.table_items.setItem(r, 8, QTableWidgetItem(str(it.get('Give to',''))))
                    except Exception:
                        pass
                except Exception:
                    continue
        finally:
            self.loading_items = False
        # Also populate documents
        self.populate_document_table(cc_no)

    def populate_document_table(self, cc_no):
        try:
            links = self.manager.get_document_links(cc_no)
        except Exception as e:
            # If table is missing, try to create it (migration) and re-fetch
            try:
                create_sql = '''CREATE TABLE IF NOT EXISTS "Contra Charge Document" ("CC No" TEXT REFERENCES "Contra Charge" ("CC No") ON DELETE CASCADE ON UPDATE CASCADE, "Doc Ref" TEXT REFERENCES "Document Manager" (File) ON DELETE CASCADE ON UPDATE CASCADE, Remark TEXT, PRIMARY KEY ("CC No", "Doc Ref"))'''
                try:
                    self.manager.db.execute_query(create_sql)
                except Exception:
                    pass
                links = self.manager.get_document_links(cc_no)
            except Exception:
                links = []
        self.table_docs.setRowCount(len(links))
        for row, link in enumerate(links):
            try:
                self.table_docs.setItem(row, 0, QTableWidgetItem(link.get('Doc Ref')))
                self.table_docs.setItem(row, 1, QTableWidgetItem(link.get('Title') or ''))
                self.table_docs.setItem(row, 2, QTableWidgetItem(link.get('Remark') or ''))
            except Exception:
                continue

    def add_document_link(self):
        # Dialog that lets user pick a document (File - Title)
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLineEdit, QDialogButtonBox, QLabel
            dialog = QDialog(self)
            dialog.setWindowTitle('Add Document Link')
            layout = QVBoxLayout()
            label = QLabel('Select Document:')
            layout.addWidget(label)
            combo = QComboBox()
            docs = []
            try:
                docs = self.manager.db.fetch_all('SELECT File, Title FROM "Document Manager"')
            except Exception:
                docs = []
            for d in docs:
                display = f"{d.get('File','')} — {d.get('Title','')}"
                combo.addItem(display, d.get('File'))
            layout.addWidget(combo)
            remark_label = QLabel('Remark:')
            layout.addWidget(remark_label)
            remark_edit = QLineEdit()
            layout.addWidget(remark_edit)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            if dialog.exec_() == QDialog.Accepted:
                doc_file = combo.currentData()
                remark = remark_edit.text()
                cc_no = self.lineEdit_cc_no.text()
                if not cc_no:
                    QMessageBox.warning(self, 'No CC Selected', 'Please select or create a Contra Charge first.')
                    return
                try:
                    self.manager.link_document(cc_no, doc_file, remark)
                    self.populate_document_table(cc_no)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to link document: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to open dialog: {e}')

    def delete_document_link(self):
        row = self.table_docs.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No Document Selected', 'Please select a document link to delete.')
            return
        cc_no = self.lineEdit_cc_no.text()
        doc_ref = self.table_docs.item(row, 0).text()
        try:
            self.manager.delete_document_link(cc_no, doc_ref)
            self.populate_document_table(cc_no)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to delete document link: {e}')

    def on_doc_link_clicked(self, row, column):
        try:
            doc_ref = self.table_docs.item(row, 0).text()
            main_window = self.window()
            main_window.tabWidget.setCurrentIndex(0)  # Document Manager tab
            try:
                if hasattr(main_window, 'ui_doc') and hasattr(main_window.ui_doc, 'load_by_ref'):
                    main_window.ui_doc.load_by_ref(doc_ref)
                else:
                    QMessageBox.information(self, 'Navigation', 'Document page is not available.')
            except Exception as e:
                QMessageBox.critical(self, 'Navigation Error', f'Failed to open Document page: {e}')
        except Exception:
            pass

    def add_item(self):
        cc_no = self.lineEdit_cc_no.text()
        if not cc_no:
            QMessageBox.warning(self, 'No CC Selected', 'Please select or create a Contra Charge first.')
            return
        # add empty item
        self.manager.add_item(cc_no, '', 0, '', 0, '')
        self.populate_items(cc_no)

    def delete_item(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'No Item Selected', 'Please select an item to delete.')
            return
        item_id_item = self.table_items.item(row, 0)
        if not item_id_item:
            return
        item_id = int(item_id_item.text())
        self.manager.delete_item(item_id)
        cc_no = self.lineEdit_cc_no.text()
        self.populate_items(cc_no)

    def on_item_changed(self, item):
        # Ignore changes caused by programmatic population
        if getattr(self, 'loading_items', False):
            return
        row = item.row()
        item_id_item = self.table_items.item(row, 0)
        if not item_id_item:
            return
        try:
            item_id = int(item_id_item.text())
        except Exception:
            return
        # Map columns
        col = item.column()
        fields = {1: 'Description', 2: 'Qty', 3: 'Unit', 4: 'Rate', 5: 'Admin Rate', 8: 'Give to'}
        if col not in fields:
            return
        value = item.text()
        if fields[col] in ['Qty', 'Rate', 'Admin Rate']:
            try:
                value = float(value.replace(',', ''))
            except Exception:
                value = 0.0
        self.manager.update_item(item_id, {fields[col]: value})
        # reload items to refresh computed columns
        cc_no = self.lineEdit_cc_no.text()
        self.populate_items(cc_no)
