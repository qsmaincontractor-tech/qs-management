from PyQt5.QtWidgets import QWidget, QListWidgetItem, QTableWidgetItem, QHBoxLayout, QPushButton, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QDialogButtonBox
from PyQt5.QtCore import QDate
from PyQt5 import uic
import os
import datetime

class Ui_AbortiveManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Set root path
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the .ui file
        ui_path = os.path.join(root_path, 'ui', 'Abortive_Manager.ui')
        uic.loadUi(ui_path, self)
        
        # Add buttons for links
        self.add_link_buttons()
        
        # Set default dates to today
        today = datetime.date.today().isoformat()
        self.dateEdit_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        self.dateEdit_issue_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        self.dateEdit_inspection_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        
        # Connect signals
        self.btn_create.clicked.connect(self.add_record)
        self.btn_update.clicked.connect(self.update_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.recordList.itemClicked.connect(self.load_details)
        
        # Connect table clicks
        self.table_docs.cellClicked.connect(self.on_doc_link_clicked)
        self.table_vo.cellClicked.connect(self.on_vo_link_clicked)
        
        # Initial Load
        self.refresh_list()

    def add_link_buttons(self):
        # Add buttons to docs tab
        docs_layout = self.tab_docs.layout()
        btn_layout_docs = QHBoxLayout()
        self.btn_add_doc = QPushButton("Add Document Link")
        self.btn_delete_doc = QPushButton("Delete Document Link")
        btn_layout_docs.addWidget(self.btn_add_doc)
        btn_layout_docs.addWidget(self.btn_delete_doc)
        docs_layout.addLayout(btn_layout_docs)
        
        # Add buttons to vo tab
        vo_layout = self.tab_vo.layout()
        btn_layout_vo = QHBoxLayout()
        self.btn_add_vo = QPushButton("Add VO Link")
        self.btn_delete_vo = QPushButton("Delete VO Link")
        btn_layout_vo.addWidget(self.btn_add_vo)
        btn_layout_vo.addWidget(self.btn_delete_vo)
        vo_layout.addLayout(btn_layout_vo)
        
        # Connect link buttons
        self.btn_add_doc.clicked.connect(self.add_doc_link)
        self.btn_delete_doc.clicked.connect(self.delete_doc_link)
        self.btn_add_vo.clicked.connect(self.add_vo_link)
        self.btn_delete_vo.clicked.connect(self.delete_vo_link)

    def refresh_list(self):
        self.recordList.clear()
        records = self.manager.get_all_abortive_works()
        for rec in records:
            item = QListWidgetItem(f"{rec['Abortive Ref']} - {rec['Description'][:20]}...")
            item.setData(32, rec['Abortive Ref'])
            self.recordList.addItem(item)

    def add_record(self):
        # Get next ref
        ref = self.manager.get_next_abortive_ref()
        
        # Get the last record to copy data
        records = self.manager.get_all_abortive_works()
        if records:
            last_rec = records[-1]
            # Copy data with new ref and today's dates
            date = datetime.date.today().isoformat()
            issue_date = datetime.date.today().isoformat()
            coordinator = last_rec['Project Coordinator']
            cost_imp = last_rec['Cost Implication']
            time_imp = last_rec['Time Implication']
            inspection = last_rec['Inspection Date']
            endorsement = last_rec['Endorsement']
            desc = last_rec['Description']
        else:
            # Defaults
            date = datetime.date.today().isoformat()
            issue_date = datetime.date.today().isoformat()
            coordinator = ""
            cost_imp = False
            time_imp = False
            inspection = datetime.date.today().isoformat()
            endorsement = False
            desc = ""
        
        # Add the new record
        self.manager.add_abortive_work(ref, date, issue_date, coordinator, cost_imp, time_imp, inspection, endorsement, desc)
        self.refresh_list()
        # Select the new item
        for i in range(self.recordList.count()):
            item = self.recordList.item(i)
            if item.data(32) == ref:
                self.recordList.setCurrentItem(item)
                self.load_details(item)
                break

    def update_record(self):
        ref = self.lineEdit_ref.text()
        date = self.dateEdit_date.date().toString("yyyy-MM-dd")
        issue_date = self.dateEdit_issue_date.date().toString("yyyy-MM-dd")
        coordinator = self.lineEdit_coordinator.text()
        cost_imp = self.checkBox_cost.isChecked()
        time_imp = self.checkBox_time.isChecked()
        inspection = self.dateEdit_inspection_date.date().toString("yyyy-MM-dd")
        endorsement = self.checkBox_endorsement.isChecked()
        desc = self.textEdit_desc.toPlainText()
        
        data = {
            "Date": date,
            "Issue Date": issue_date,
            "Project Coordinator": coordinator,
            "Cost Implication": cost_imp,
            "Time Implication": time_imp,
            "Inspection Date": inspection,
            "Endorsement": endorsement,
            "Description": desc
        }
        self.manager.update_abortive_work(ref, data)
        self.refresh_list()

    def load_details(self, item):
        ref = item.data(32)
        rec = self.manager.get_abortive_work(ref)
        if rec:
            self.lineEdit_ref.setText(rec['Abortive Ref'])
            self.dateEdit_date.setDate(QDate.fromString(rec['Date'], "yyyy-MM-dd"))
            self.dateEdit_issue_date.setDate(QDate.fromString(rec['Issue Date'], "yyyy-MM-dd"))
            self.lineEdit_coordinator.setText(rec['Project Coordinator'])
            self.checkBox_cost.setChecked(rec['Cost Implication'])
            self.checkBox_time.setChecked(rec['Time Implication'])
            inspection_date = rec.get('Inspection Date', '')
            if inspection_date:
                self.dateEdit_inspection_date.setDate(QDate.fromString(str(inspection_date), "yyyy-MM-dd"))
            self.checkBox_endorsement.setChecked(rec['Endorsement'])
            self.textEdit_desc.setPlainText(rec['Description'])
            
            # Populate linked records
            self.populate_doc_table(ref)
            self.populate_vo_table(ref)

    def populate_doc_table(self, abortive_ref):
        links = self.manager.get_document_links(abortive_ref)
        self.table_docs.setRowCount(len(links))
        self.table_docs.setColumnCount(3)
        self.table_docs.setHorizontalHeaderLabels(["Doc Ref", "Title", "Remark"])
        for row, link in enumerate(links):
            self.table_docs.setItem(row, 0, QTableWidgetItem(link['Doc Ref']))
            self.table_docs.setItem(row, 1, QTableWidgetItem(link.get('Title', '')))
            self.table_docs.setItem(row, 2, QTableWidgetItem(link.get('Remark', '')))

    def populate_vo_table(self, abortive_ref):
        links = self.manager.get_vo_links(abortive_ref)
        self.table_vo.setRowCount(len(links))
        self.table_vo.setColumnCount(3)
        self.table_vo.setHorizontalHeaderLabels(["VO Ref", "Description", "Remark"])
        for row, link in enumerate(links):
            self.table_vo.setItem(row, 0, QTableWidgetItem(link['VO ref']))
            self.table_vo.setItem(row, 1, QTableWidgetItem(link.get('Description', '')))
            self.table_vo.setItem(row, 2, QTableWidgetItem(link.get('Remark', '')))

    def load_by_ref(self, ref):
        rec = self.manager.get_abortive_work(ref)
        if rec:
            self.lineEdit_ref.setText(rec['Abortive Ref'])
            self.dateEdit_date.setDate(QDate.fromString(rec['Date'], "yyyy-MM-dd"))
            self.dateEdit_issue_date.setDate(QDate.fromString(rec['Issue Date'], "yyyy-MM-dd"))
            self.lineEdit_coordinator.setText(rec['Project Coordinator'])
            self.checkBox_cost.setChecked(rec['Cost Implication'])
            self.checkBox_time.setChecked(rec['Time Implication'])
            # Inspection is a date field; set the date editor instead of a missing checkbox
            inspection_date = rec.get('Inspection Date', '')
            if inspection_date:
                try:
                    self.dateEdit_inspection_date.setDate(QDate.fromString(str(inspection_date), "yyyy-MM-dd"))
                except Exception:
                    pass
            self.checkBox_endorsement.setChecked(rec['Endorsement'])
            self.textEdit_desc.setPlainText(rec['Description'])
            # Populate linked records
            self.populate_doc_table(ref)
            self.populate_vo_table(ref)
            # Select the item in the list
            for i in range(self.recordList.count()):
                item = self.recordList.item(i)
                if item.data(32) == ref:
                    self.recordList.setCurrentItem(item)
                    break

    def add_doc_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Abortive Work Selected", "Please select an abortive work first.")
            return
        abortive_ref = current_item.data(32)
        docs = self.window().ui_doc.manager.get_all_documents()
        if not docs:
            QMessageBox.information(self, "No Documents", "No documents available to link.")
            return
        selected_ref, remark = self.show_add_link_dialog("Add Document Link", "Select Document:", docs, "File")
        if selected_ref:
            self.manager.add_document_link(abortive_ref, selected_ref, remark)
            self.populate_doc_table(abortive_ref)

    def delete_doc_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Abortive Work Selected", "Please select an abortive work first.")
            return
        abortive_ref = current_item.data(32)
        selected = self.table_docs.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Link Selected", "Please select a link to delete.")
            return
        row = selected[0].row()
        doc_ref = self.table_docs.item(row, 0).text()
        self.manager.delete_document_link(abortive_ref, doc_ref)
        self.populate_doc_table(abortive_ref)

    def add_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Abortive Work Selected", "Please select an abortive work first.")
            return
        abortive_ref = current_item.data(32)
        vos = self.window().ui_payment.manager.get_all_vos()
        if not vos:
            QMessageBox.information(self, "No VOs", "No VOs available to link.")
            return
        selected_ref, remark = self.show_add_link_dialog("Add VO Link", "Select VO:", vos, "VO ref")
        if selected_ref:
            self.manager.add_vo_link(selected_ref, abortive_ref, remark)
            self.populate_vo_table(abortive_ref)

    def delete_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Abortive Work Selected", "Please select an abortive work first.")
            return
        abortive_ref = current_item.data(32)
        selected = self.table_vo.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Link Selected", "Please select a link to delete.")
            return
        row = selected[0].row()
        vo_ref = self.table_vo.item(row, 0).text()
        self.manager.delete_vo_link(vo_ref, abortive_ref)
        self.populate_vo_table(abortive_ref)

    def on_doc_link_clicked(self, row, column):
        doc_ref = self.table_docs.item(row, 0).text()
        main_window = self.window()
        main_window.tabWidget.setCurrentIndex(0)  # Document Manager tab
        main_window.ui_doc.load_by_ref(doc_ref)

    def on_vo_link_clicked(self, row, column):
        vo_ref = self.table_vo.item(row, 0).text()
        main_window = self.window()
        main_window.tabWidget.setCurrentIndex(2)  # Payment Application tab
        main_window.ui_payment.load_vo_by_ref(vo_ref)

    def show_add_link_dialog(self, title, label, items, ref_key):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        
        combo = QComboBox()
        combo.addItems([item[ref_key] for item in items])
        layout.addWidget(combo)
        
        remark_label = QLabel("Remark:")
        layout.addWidget(remark_label)
        
        remark_edit = QLineEdit()
        layout.addWidget(remark_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_ref = combo.currentText()
            remark = remark_edit.text()
            return selected_ref, remark
        return None, None

    def delete_record(self):
        current_item = self.recordList.currentItem()
        if current_item:
            ref = current_item.data(32)
            self.manager.delete_abortive_work(ref)
            self.refresh_list()
            self.clear_form()

    def clear_form(self):
        self.lineEdit_ref.clear()
        self.lineEdit_coordinator.clear()
        self.textEdit_desc.clear()
        self.checkBox_cost.setChecked(False)
        self.checkBox_time.setChecked(False)
        self.dateEdit_inspection_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        self.checkBox_endorsement.setChecked(False)
        today = datetime.date.today().isoformat()
        self.dateEdit_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        self.dateEdit_issue_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        # Clear tables
        self.table_docs.setRowCount(0)
        self.table_vo.setRowCount(0)
