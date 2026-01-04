from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QDate, Qt, QTimer
import os

class Ui_SC_VOManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        # Load UI from .ui file
        from PyQt5 import uic
        import os
        ui_path = os.path.join(os.path.dirname(__file__), 'SC_VO_Manager.ui')
        uic.loadUi(ui_path, self)

        # Set default dates
        today = QDate.currentDate()
        try:
            self.dateEdit_date.setDate(today)
            self.dateEdit_receive.setDate(today)
        except Exception:
            pass

        # Set table headers (docs)
        try:
            self.table_docs.setColumnCount(3)
            self.table_docs.setHorizontalHeaderLabels(["Doc Ref", "Title", "Remark"])
        except Exception:
            pass

        # Configure the VO table (declared in the .ui file)
        try:
            # Table declared in UI as `table_sc_vos`
            self.table_sc_vos.setColumnCount(4)
            self.table_sc_vos.setHorizontalHeaderLabels(["VO Ref", "Description", "Application Amount", "Agree Amount"])
            self.table_sc_vos.setSelectionBehavior(self.table_sc_vos.SelectRows)
            self.table_sc_vos.setSelectionMode(self.table_sc_vos.SingleSelection)
            try:
                self.table_sc_vos.setEditTriggers(self.table_sc_vos.NoEditTriggers)
            except Exception:
                pass
            # Legacy list removed from UI; using table_sc_vos only
            # Wire table click to selection handler
            self.table_sc_vos.cellClicked.connect(self.on_table_vo_clicked)
            # UX: stretch description column, keep numeric cols sized to contents
            try:
                from PyQt5.QtWidgets import QHeaderView
                self.table_sc_vos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
                self.table_sc_vos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.table_sc_vos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                self.table_sc_vos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                try:
                    self.table_sc_vos.horizontalHeaderItem(2).setToolTip("Application amount formatted (HK$)")
                    self.table_sc_vos.horizontalHeaderItem(3).setToolTip("Agree amount formatted (HK$)")
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass

        # Populate subcontract combo
        self.populate_subcontract_combo()

        # Connect signals
        self.btn_add.clicked.connect(self.add_sc_vo)
        # Hide the Update button — autosave will be used instead
        try:
            self.btn_update.hide()
        except Exception:
            pass
        self.btn_delete.clicked.connect(self.delete_sc_vo)
        self.btn_add_doc_link.clicked.connect(self.add_document_link)
        self.btn_delete_doc_link.clicked.connect(self.delete_document_link)
        # Clicking a document row should navigate to Document Manager and select that document
        try:
            self.table_docs.cellClicked.connect(self.on_doc_link_clicked)
        except Exception:
            pass

        # Autosave hooks for VO details (no Update button required)
        try:
            self.loading_vo_details = False
            self.lineEdit_desc.editingFinished.connect(self.auto_save_vo)
            self.doubleSpinBox_app.valueChanged.connect(lambda: self.auto_save_vo())
            self.doubleSpinBox_agree.valueChanged.connect(lambda: self.auto_save_vo())
            self.dateEdit_date.dateChanged.connect(lambda: self.auto_save_vo())
            self.dateEdit_receive.dateChanged.connect(lambda: self.auto_save_vo())
            self.checkBox_issue.stateChanged.connect(lambda: self.auto_save_vo())
            self.checkBox_dispute.stateChanged.connect(lambda: self.auto_save_vo())
            self.checkBox_agree.stateChanged.connect(lambda: self.auto_save_vo())
            self.checkBox_reject.stateChanged.connect(lambda: self.auto_save_vo())
            self.comboBox_subcontract.currentIndexChanged.connect(lambda: self.auto_save_vo())
            # QTextEdit does not have editingFinished; debounce textChanged for autosave
            self.textEdit_remark.textChanged.connect(lambda: QTimer.singleShot(500, self.auto_save_vo))
            # UX polish: amount prefixes, decimals and tooltips
            try:
                self.doubleSpinBox_app.setPrefix('HK$ ')
                self.doubleSpinBox_agree.setPrefix('HK$ ')
                self.doubleSpinBox_app.setDecimals(2)
                self.doubleSpinBox_agree.setDecimals(2)
                self.doubleSpinBox_app.setSingleStep(100.0)
                self.doubleSpinBox_agree.setSingleStep(100.0)
                self.doubleSpinBox_app.setToolTip('Application amount (auto-saved)')
                self.doubleSpinBox_agree.setToolTip('Agree amount (auto-saved)')
                self.lineEdit_desc.setToolTip('VO description (auto-saved)')
                self.textEdit_remark.setToolTip('Remark (auto-saved on pause)')
            except Exception:
                pass
        except Exception:
            pass

        # Initial load
        self.refresh_list()

    def populate_subcontract_combo(self):
        # This would need access to subcontract manager
        # For now, just add some dummy data
        self.comboBox_subcontract.addItems(["SC001", "SC002", "SC003"])

    def format_number(self, value):
        """Format number with thousand separators and 2 decimals (safe)."""
        try:
            return "{:,.2f}".format(float(value))
        except Exception:
            return "0.00"

    def refresh_list(self, subcontract=None):
        # Legacy sc_vo_list removed; showing table_sc_vos only

        # Prefer direct query by subcontract when filtering to avoid relying on client-side filtering
        if subcontract:
            try:
                sc_vos = self.manager.get_sc_vos_by_subcontract(subcontract)
            except Exception:
                sc_vos = []
        else:
            sc_vos = self.manager.get_all_sc_vos()

        # Populate table view (use table_sc_vos exclusively)
        try:
            self.table_sc_vos.setRowCount(len(sc_vos))
            for row, vo in enumerate(sc_vos):
                try:
                    self.table_sc_vos.setItem(row, 0, QTableWidgetItem(str(vo.get('VO ref', ''))))
                    self.table_sc_vos.setItem(row, 1, QTableWidgetItem(str(vo.get('Description', ''))))
                    app_item = QTableWidgetItem(self.format_number(vo.get('Application Amount', 0)))
                    app_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    agree_item = QTableWidgetItem(self.format_number(vo.get('Agree Amount', 0)))
                    agree_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table_sc_vos.setItem(row, 2, app_item)
                    self.table_sc_vos.setItem(row, 3, agree_item)
                except Exception:
                    continue
        except Exception:
            # If table population fails, clear table
            try:
                self.table_sc_vos.setRowCount(0)
            except Exception:
                pass

        # Resize columns to fit contents
        try:
            self.table_sc_vos.resizeColumnsToContents()
        except Exception:
            pass

        # If filtering by subcontract and we have rows, select the first row and load its details
        try:
            if sc_vos and subcontract:
                # select first table row
                try:
                    self.table_sc_vos.selectRow(0)
                    vo_ref = self.table_sc_vos.item(0, 0).text()
                    self.load_details_by_ref(vo_ref)
                except Exception:
                    pass
        except Exception:
            pass

    def add_sc_vo(self):
        vo_ref = self.manager.get_next_sc_vo_ref()
        sc_no = self.comboBox_subcontract.currentText()
        date = self.dateEdit_date.date().toString("yyyy-MM-dd")
        receive_date = self.dateEdit_receive.date().toString("yyyy-MM-dd")
        desc = self.lineEdit_desc.text()
        app_amt = self.doubleSpinBox_app.value()
        agree_amt = self.doubleSpinBox_agree.value()
        issue = self.checkBox_issue.isChecked()
        dispute = self.checkBox_dispute.isChecked()
        agree = self.checkBox_agree.isChecked()
        reject = self.checkBox_reject.isChecked()
        remark = self.textEdit_remark.toPlainText()

        self.manager.create_sc_vo(vo_ref, sc_no, date, receive_date, desc, app_amt, agree_amt, issue, dispute, agree, reject, remark)
        # Refresh full table so the new VO is visible in the complete list
        self.refresh_list()

        # Select the new SC VO in the table and load details
        try:
            found = False
            for r in range(self.table_sc_vos.rowCount()):
                try:
                    if self.table_sc_vos.item(r, 0).text() == vo_ref:
                        self.table_sc_vos.selectRow(r)
                        self.load_details_by_ref(vo_ref)
                        found = True
                        break
                except Exception:
                    continue
            if not found:
                # If not found in table, set the ref on form
                try:
                    self.lineEdit_ref.setText(vo_ref)
                except Exception:
                    pass
        except Exception:
            pass

    def update_sc_vo(self):
        vo_ref = self.lineEdit_ref.text()
        if not vo_ref:
            QMessageBox.warning(self, "No SC VO Selected", "Please select a SC VO to update.")
            return
        data = {
            "Subcontract": self.comboBox_subcontract.currentText(),
            "Date": self.dateEdit_date.date().toString("yyyy-MM-dd"),
            "Receive Date": self.dateEdit_receive.date().toString("yyyy-MM-dd"),
            "Description": self.lineEdit_desc.text(),
            "Application Amount": self.doubleSpinBox_app.value(),
            "Agree Amount": self.doubleSpinBox_agree.value(),
            "Issue Assessment": self.checkBox_issue.isChecked(),
            "Dispute": self.checkBox_dispute.isChecked(),
            "Agree": self.checkBox_agree.isChecked(),
            "Reject": self.checkBox_reject.isChecked(),
            "Remark": self.textEdit_remark.toPlainText()
        }
        self.manager.update_sc_vo(vo_ref, data)
        self.refresh_list()

    def delete_sc_vo(self):
        vo_ref = self.lineEdit_ref.text()
        if not vo_ref:
            QMessageBox.warning(self, "No SC VO Selected", "Please select a SC VO to delete.")
            return
        self.manager.delete_sc_vo(vo_ref)
        self.refresh_list()
        self.clear_form()

    def load_details(self, item):
        # Accept QListWidgetItem or other types; extract VO ref and delegate
        try:
            if hasattr(item, 'data'):
                vo_ref = item.data(32)
            elif hasattr(item, 'text'):
                vo_ref = item.text()
            else:
                vo_ref = str(item)
            self.load_details_by_ref(vo_ref)
        except Exception:
            pass

    def load_details_by_ref(self, vo_ref):
        vo = self.manager.get_sc_vo(vo_ref)
        if vo:
            self.lineEdit_ref.setText(vo['VO ref'])
            self.comboBox_subcontract.setCurrentText(vo['Subcontract'])
            try:
                self.dateEdit_date.setDate(QDate.fromString(vo['Date'], "yyyy-MM-dd"))
            except Exception:
                pass
            try:
                self.dateEdit_receive.setDate(QDate.fromString(vo['Receive Date'], "yyyy-MM-dd"))
            except Exception:
                pass
            self.lineEdit_desc.setText(vo.get('Description', ''))
            try:
                self.doubleSpinBox_app.setValue(vo.get('Application Amount', 0))
            except Exception:
                pass
            try:
                self.doubleSpinBox_agree.setValue(vo.get('Agree Amount', 0))
            except Exception:
                pass
            try:
                self.checkBox_issue.setChecked(bool(vo.get('Issue Assessment')))
                self.checkBox_dispute.setChecked(bool(vo.get('Dispute')))
                self.checkBox_agree.setChecked(bool(vo.get('Agree')))
                self.checkBox_reject.setChecked(bool(vo.get('Reject')))
            except Exception:
                pass
            self.textEdit_remark.setPlainText(vo.get('Remark', ''))

            # Populate link tables
            self.populate_document_table(vo_ref)

            # Cache loaded VO for change detection during autosave
            try:
                self._vo_loaded_rec = vo.copy()
            except Exception:
                self._vo_loaded_rec = {
                    'VO ref': vo.get('VO ref'),
                    'Subcontract': vo.get('Subcontract'),
                    'Date': vo.get('Date'),
                    'Receive Date': vo.get('Receive Date'),
                    'Description': vo.get('Description'),
                    'Application Amount': vo.get('Application Amount'),
                    'Agree Amount': vo.get('Agree Amount'),
                    'Issue Assessment': vo.get('Issue Assessment'),
                    'Dispute': vo.get('Dispute'),
                    'Agree': vo.get('Agree'),
                    'Reject': vo.get('Reject'),
                    'Remark': vo.get('Remark')
                }

    def auto_save_vo(self):
        """Autosave the current SC VO detail fields into the database; only changed fields are written."""
        if getattr(self, 'loading_vo_details', False):
            return
        try:
            vo_ref = self.lineEdit_ref.text()
            if not vo_ref:
                return
            data = {
                'Subcontract': self.comboBox_subcontract.currentText(),
                'Date': self.dateEdit_date.date().toString('yyyy-MM-dd'),
                'Receive Date': self.dateEdit_receive.date().toString('yyyy-MM-dd'),
                'Description': self.lineEdit_desc.text(),
                'Application Amount': self.doubleSpinBox_app.value(),
                'Agree Amount': self.doubleSpinBox_agree.value(),
                'Issue Assessment': self.checkBox_issue.isChecked(),
                'Dispute': self.checkBox_dispute.isChecked(),
                'Agree': self.checkBox_agree.isChecked(),
                'Reject': self.checkBox_reject.isChecked(),
                'Remark': self.textEdit_remark.toPlainText()
            }
            base = getattr(self, '_vo_loaded_rec', None)
            if base:
                changed = {}
                for k, v in data.items():
                    if base.get(k) != v:
                        changed[k] = v
                if not changed:
                    return
            else:
                changed = data

            # Perform update
            try:
                self.manager.update_sc_vo(vo_ref, changed)
                # refresh cache
                rec = self.manager.get_sc_vo(vo_ref)
                try:
                    self._vo_loaded_rec = rec.copy()
                except Exception:
                    self._vo_loaded_rec = rec
                # Update table view for this VO so amounts stay in sync
                try:
                    for r in range(self.table_sc_vos.rowCount()):
                        try:
                            if self.table_sc_vos.item(r, 0) and self.table_sc_vos.item(r, 0).text() == vo_ref:
                                # Update application & agree amount formatting
                                try:
                                    self.table_sc_vos.item(r, 2).setText(self.format_number(rec.get('Application Amount', 0)))
                                except Exception:
                                    pass
                                try:
                                    self.table_sc_vos.item(r, 3).setText(self.format_number(rec.get('Agree Amount', 0)))
                                except Exception:
                                    pass
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
            except Exception as e:
                QMessageBox.warning(self, 'Save Failed', f'Failed to save changes: {e}')
        except Exception:
            pass

    def clear_form(self):
        self.lineEdit_ref.clear()
        self.lineEdit_desc.clear()
        self.textEdit_remark.clear()
        self.doubleSpinBox_app.setValue(0)
        self.doubleSpinBox_agree.setValue(0)
        self.checkBox_issue.setChecked(False)
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

    def on_table_vo_clicked(self, row, column):
        try:
            vo_ref = self.table_sc_vos.item(row, 0).text()
            self.load_details_by_ref(vo_ref)
        except Exception:
            pass

    def add_document_link(self):
        # Show a dialog with a combo of Document File + Title
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLineEdit, QDialogButtonBox, QLabel
            dialog = QDialog(self)
            dialog.setWindowTitle('Add Document Link')
            layout = QVBoxLayout()

            label = QLabel('Select Document:')
            layout.addWidget(label)
            combo = QComboBox()
            # Fetch documents from Document Manager table
            docs = []
            try:
                docs = self.manager.db.fetch_all('SELECT File, Title FROM "Document Manager"')
            except Exception:
                docs = []
            for d in docs:
                display = f"{d.get('File', '')} — {d.get('Title', '')}"
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
                vo_ref = self.lineEdit_ref.text()
                if not vo_ref:
                    QMessageBox.warning(self, 'No VO Selected', 'Please select or create a VO first.')
                    return
                try:
                    self.manager.link_to_document(vo_ref, doc_file, remark)
                    self.populate_document_table(vo_ref)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to link document: {e}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to open dialog: {e}')

    def delete_document_link(self):
        current_row = self.table_docs.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Document Selected', 'Please select a document link to delete.')
            return
        vo_ref = self.lineEdit_ref.text()
        doc_ref = self.table_docs.item(current_row, 0).text()
        try:
            self.manager.delete_document_link(vo_ref, doc_ref)
            self.populate_document_table(vo_ref)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to delete document link: {e}')