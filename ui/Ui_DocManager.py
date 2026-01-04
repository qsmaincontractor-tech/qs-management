from PyQt5.QtWidgets import QWidget, QListWidgetItem, QTableWidgetItem, QHBoxLayout, QPushButton, QInputDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QDialogButtonBox, QFormLayout, QSizePolicy
from PyQt5.QtCore import QDate
from PyQt5 import uic
import os
import datetime

class Ui_DocManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Set root path
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the .ui file
        ui_path = os.path.join(root_path, 'ui', 'Doc_Manager.ui')
        uic.loadUi(ui_path, self)
        
        # Add SC VO tab
        from PyQt5.QtWidgets import QTableWidget
        self.tab_sc_vo = QWidget()
        self.tab_sc_vo.setLayout(QVBoxLayout())
        self.table_sc_vo = QTableWidget()
        self.tab_sc_vo.layout().addWidget(self.table_sc_vo)
        self.intermediateTabs.addTab(self.tab_sc_vo, "SC VO")
        
        # Setup document types combo
        self.refresh_types()
        
        # Find the buttons safely (some UI variants don't expose a parent container)
        self.btn_add_type = self.findChild(QPushButton, "btn_add_type") or getattr(self, 'btn_add_type', None)
        self.btn_delete_type = self.findChild(QPushButton, "btn_delete_type") or getattr(self, 'btn_delete_type', None)
        
        # Connect buttons if present
        if self.btn_add_type:
            self.btn_add_type.clicked.connect(self.add_new_type)
        if self.btn_delete_type:
            self.btn_delete_type.clicked.connect(self.delete_type)
        
        # Add buttons for links
        self.add_link_buttons()
        
        # Set default date to today
        today = datetime.date.today().isoformat()
        self.dateEdit_date.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        
        # Connect signals
        self.btn_create.clicked.connect(self.add_document)
        self.btn_update.clicked.connect(self.update_document)
        self.btn_delete.clicked.connect(self.delete_document)
        self.recordList.itemClicked.connect(self.load_details)
        
        # Connect table clicks
        self.table_abortive.cellClicked.connect(self.on_abortive_link_clicked)
        self.table_vo.cellClicked.connect(self.on_vo_link_clicked)
        self.table_sc_vo.cellClicked.connect(self.on_sc_vo_link_clicked)
        
        # Initial Load
        self.refresh_list()

    def add_link_buttons(self):
        # Add buttons to abortive tab
        abortive_layout = self.tab_abortive.layout()
        btn_layout = QHBoxLayout()
        self.btn_add_abortive = QPushButton("Add Abortive Link")
        self.btn_delete_abortive = QPushButton("Delete Abortive Link")
        btn_layout.addWidget(self.btn_add_abortive)
        btn_layout.addWidget(self.btn_delete_abortive)
        abortive_layout.addLayout(btn_layout)
        
        # Add buttons to vo tab
        vo_layout = self.tab_vo.layout()
        btn_layout_vo = QHBoxLayout()
        self.btn_add_vo = QPushButton("Add VO Link")
        self.btn_delete_vo = QPushButton("Delete VO Link")
        btn_layout_vo.addWidget(self.btn_add_vo)
        btn_layout_vo.addWidget(self.btn_delete_vo)
        vo_layout.addLayout(btn_layout_vo)
        
        # Add buttons to sc vo tab
        sc_vo_layout = self.tab_sc_vo.layout()
        btn_layout_sc_vo = QHBoxLayout()
        self.btn_add_sc_vo = QPushButton("Add SC VO Link")
        self.btn_delete_sc_vo = QPushButton("Delete SC VO Link")
        btn_layout_sc_vo.addWidget(self.btn_add_sc_vo)
        btn_layout_sc_vo.addWidget(self.btn_delete_sc_vo)
        sc_vo_layout.addLayout(btn_layout_sc_vo)
        
        # Connect link buttons
        self.btn_add_abortive.clicked.connect(self.add_abortive_link)
        self.btn_delete_abortive.clicked.connect(self.delete_abortive_link)
        self.btn_add_vo.clicked.connect(self.add_vo_link)
        self.btn_delete_vo.clicked.connect(self.delete_vo_link)
        self.btn_add_sc_vo.clicked.connect(self.add_sc_vo_link)
        self.btn_delete_sc_vo.clicked.connect(self.delete_sc_vo_link)

    def refresh_list(self):
        self.recordList.clear()
        docs = self.manager.get_all_documents()
        for doc in docs:
            item = QListWidgetItem(f"{doc['File']} - {doc['Title']}")
            item.setData(32, doc['File']) # Store ID in UserRole (32)
            self.recordList.addItem(item)

    def add_document(self):
        # Get next file ref
        file_ref = self.manager.get_next_file_ref()
        
        # Get the last document to copy data
        docs = self.manager.get_all_documents()
        if docs:
            last_doc = docs[-1]
            # Copy data with new file_ref and today's date
            title = last_doc['Title']
            date = datetime.date.today().isoformat()
            doc_type = last_doc['Type']
            from_party = last_doc['From']
            to_party = last_doc['To']
            cost_imp = last_doc['Cost Implication']
            time_imp = last_doc['Time Implication']
            remark = last_doc['Remark']
        else:
            # If no documents, use defaults
            title = ""
            date = datetime.date.today().isoformat()
            doc_type = ""
            from_party = ""
            to_party = ""
            cost_imp = False
            time_imp = False
            remark = ""
        
        # Add the new document
        self.manager.add_document(file_ref, date, doc_type, title, from_party, to_party, cost_imp, time_imp, remark)
        self.refresh_list()
        # Select the new item
        for i in range(self.recordList.count()):
            item = self.recordList.item(i)
            if item.data(32) == file_ref:
                self.recordList.setCurrentItem(item)
                self.load_details(item)
                break

    def update_document(self):
        file_ref = self.lineEdit_file.text()
        title = self.lineEdit_title.text()
        date = self.dateEdit_date.date().toString("yyyy-MM-dd")
        doc_type = self.comboBox_type.currentText()
        from_party = self.lineEdit_from.text()
        to_party = self.lineEdit_to.text()
        cost_imp = self.checkBox_cost.isChecked()
        time_imp = self.checkBox_time.isChecked()
        remark = self.textEdit_remark.toPlainText()
        
        data = {
            "Date": date,
            "Type": doc_type,
            "Title": title,
            "From": from_party,
            "To": to_party,
            "Cost Implication": cost_imp,
            "Time Implication": time_imp,
            "Remark": remark
        }
        self.manager.update_document(file_ref, data)
        self.refresh_list()

    def load_details(self, item):
        file_ref = item.data(32)
        doc = self.manager.get_document(file_ref)
        if doc:
            self.lineEdit_file.setText(doc['File'])
            self.dateEdit_date.setDate(QDate.fromString(doc['Date'], "yyyy-MM-dd"))
            self.comboBox_type.setCurrentText(doc['Type'])
            self.lineEdit_title.setText(doc['Title'])
            self.lineEdit_from.setText(doc['From'])
            self.lineEdit_to.setText(doc['To'])
            self.checkBox_cost.setChecked(doc['Cost Implication'])
            self.checkBox_time.setChecked(doc['Time Implication'])
            self.textEdit_remark.setPlainText(doc['Remark'])
            
            # Populate linked records
            self.populate_abortive_table(file_ref)
            self.populate_vo_table(file_ref)
            self.populate_sc_vo_table(file_ref)

    def delete_document(self):
        current_item = self.recordList.currentItem()
        if current_item:
            file_ref = current_item.data(32)
            self.manager.delete_document(file_ref)
            self.refresh_list()
            self.clear_form()

    def populate_abortive_table(self, file_ref):
        links = self.manager.get_abortive_links(file_ref)
        self.table_abortive.setRowCount(len(links))
        self.table_abortive.setColumnCount(3)
        self.table_abortive.setHorizontalHeaderLabels(["Abortive Ref", "Description", "Remark"])
        for row, link in enumerate(links):
            self.table_abortive.setItem(row, 0, QTableWidgetItem(link['Abortive Ref']))
            self.table_abortive.setItem(row, 1, QTableWidgetItem(link.get('Description', '')))
            self.table_abortive.setItem(row, 2, QTableWidgetItem(link.get('Remark', '')))

    def populate_vo_table(self, file_ref):
        links = self.manager.get_vo_links(file_ref)
        self.table_vo.setRowCount(len(links))
        self.table_vo.setColumnCount(3)
        self.table_vo.setHorizontalHeaderLabels(["VO Ref", "Description", "Remark"])
        for row, link in enumerate(links):
            self.table_vo.setItem(row, 0, QTableWidgetItem(link['VO Ref']))
            self.table_vo.setItem(row, 1, QTableWidgetItem(link.get('Description', '')))
            self.table_vo.setItem(row, 2, QTableWidgetItem(link.get('Remark', '')))

    def populate_sc_vo_table(self, file_ref):
        links = self.manager.get_sc_vo_links(file_ref)
        self.table_sc_vo.setRowCount(len(links))
        self.table_sc_vo.setColumnCount(3)
        self.table_sc_vo.setHorizontalHeaderLabels(["SC VO Ref", "Description", "Remark"])
        for row, link in enumerate(links):
            self.table_sc_vo.setItem(row, 0, QTableWidgetItem(link['VO Ref']))
            self.table_sc_vo.setItem(row, 1, QTableWidgetItem(link.get('Description', '')))
            self.table_sc_vo.setItem(row, 2, QTableWidgetItem(link.get('Remark', '')))

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

    def add_abortive_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        abortive_works = self.manager.get_all_abortive_works()
        if not abortive_works:
            QMessageBox.information(self, "No Abortive Works", "No abortive works available to link.")
            return
        selected_ref, remark = self.show_add_link_dialog("Add Abortive Link", "Select Abortive Ref:", abortive_works, "Abortive Ref")
        if selected_ref:
            self.manager.link_abortive_work(selected_ref, file_ref, remark)
            self.populate_abortive_table(file_ref)

    def delete_abortive_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        selected = self.table_abortive.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Link Selected", "Please select a link to delete.")
            return
        row = selected[0].row()
        abortive_ref = self.table_abortive.item(row, 0).text()
        self.manager.delete_abortive_link(abortive_ref, file_ref)
        self.populate_abortive_table(file_ref)

    def add_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        vos = self.manager.get_all_vos()
        if not vos:
            QMessageBox.information(self, "No VOs", "No VOs available to link.")
            return
        selected_ref, remark = self.show_add_link_dialog("Add VO Link", "Select VO Ref:", vos, "VO ref")
        if selected_ref:
            self.manager.link_vo(selected_ref, file_ref, remark)
            self.populate_vo_table(file_ref)

    def delete_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        selected = self.table_vo.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Link Selected", "Please select a link to delete.")
            return
        row = selected[0].row()
        vo_ref = self.table_vo.item(row, 0).text()
        self.manager.delete_vo_link(vo_ref, file_ref)
        self.populate_vo_table(file_ref)

    def add_sc_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        sc_vos = self.manager.get_all_sc_vos()
        if not sc_vos:
            QMessageBox.information(self, "No SC VOs", "No SC VOs available to link.")
            return
        selected_ref, remark = self.show_add_link_dialog("Add SC VO Link", "Select SC VO Ref:", sc_vos, "VO ref")
        if selected_ref:
            self.manager.link_sc_vo(selected_ref, file_ref, remark)
            self.populate_sc_vo_table(file_ref)

    def delete_sc_vo_link(self):
        current_item = self.recordList.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Document Selected", "Please select a document first.")
            return
        file_ref = current_item.data(32)
        selected = self.table_sc_vo.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Link Selected", "Please select a link to delete.")
            return
        row = selected[0].row()
        sc_vo_ref = self.table_sc_vo.item(row, 0).text()
        self.manager.delete_sc_vo_link(sc_vo_ref, file_ref)
        self.populate_sc_vo_table(file_ref)

    def on_abortive_link_clicked(self, row, column):
        ref = self.table_abortive.item(row, 0).text()
        main_window = self.window()
        main_window.tabWidget.setCurrentIndex(1)  # Abortive Work tab
        main_window.ui_abortive.load_by_ref(ref)

    def on_vo_link_clicked(self, row, column):
        ref = self.table_vo.item(row, 0).text()
        main_window = self.window()
        # Switch to Main Contract VO tab and select the VO
        main_window.tabWidget.setCurrentIndex(3)  # Main Contract VO tab
        try:
            if hasattr(main_window, 'ui_mc_vo') and hasattr(main_window.ui_mc_vo, 'load_vo_by_ref'):
                main_window.ui_mc_vo.load_vo_by_ref(ref)
            else:
                QMessageBox.information(self, 'Navigation', 'Main Contract VO page is not available.')
        except Exception as e:
            QMessageBox.critical(self, 'Navigation Error', f'Failed to open Main Contract VO: {e}')

    def on_sc_vo_link_clicked(self, row, column):
        ref = self.table_sc_vo.item(row, 0).text()
        main_window = self.window()
        # Switch to Subcontract tab and load the SC VO
        main_window.tabWidget.setCurrentIndex(4)  # Subcontract tab
        try:
            if hasattr(main_window, 'ui_subcontract') and hasattr(main_window.ui_subcontract, 'load_sc_vo_by_ref'):
                main_window.ui_subcontract.load_sc_vo_by_ref(ref)
            else:
                QMessageBox.information(self, 'Navigation', 'Subcontract page is not available.')
        except Exception as e:
            QMessageBox.critical(self, 'Navigation Error', f'Failed to open Subcontract page: {e}')

    def refresh_types(self):
        self.comboBox_type.clear()
        types = self.manager.get_doc_types()
        type_names = [t['Type'] for t in types]
        if "Undefined" not in type_names:
            self.manager.add_doc_type("Undefined", "Undefined type")
            types = self.manager.get_doc_types()
        for t in types:
            self.comboBox_type.addItem(t['Type'])

    def add_new_type(self):
        name, ok = QInputDialog.getText(self, "Add New Document Type", "Type Name:")
        if ok and name:
            desc, ok2 = QInputDialog.getText(self, "Description", "Description:")
            if ok2:
                self.manager.add_doc_type(name, desc)
                self.refresh_types()
                # Set the new type as current
                self.comboBox_type.setCurrentText(name)

    def delete_type(self):
        current = self.comboBox_type.currentText()
        if current and current != "Add New Type...":
            if self.manager.is_type_used(current):
                reply = QMessageBox.question(self, "Type in Use", f"This type is used by documents. Set those documents' type to 'Undefined' and delete the type '{current}'?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.manager.update_documents_type(current, "Undefined")
                    self.manager.delete_doc_type(current)
                    self.refresh_types()
            else:
                reply = QMessageBox.question(self, "Confirm Delete", f"Delete document type '{current}'?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.manager.delete_doc_type(current)
                    self.refresh_types()

    def load_by_ref(self, file_ref):
        doc = self.manager.get_document(file_ref)
        if doc:
            self.lineEdit_file.setText(doc['File'])
            self.dateEdit_date.setDate(QDate.fromString(doc['Date'], "yyyy-MM-dd"))
            self.comboBox_type.setCurrentText(doc['Type'])
            self.lineEdit_title.setText(doc['Title'])
            self.lineEdit_from.setText(doc['From'])
            self.lineEdit_to.setText(doc['To'])
            self.checkBox_cost.setChecked(doc['Cost Implication'])
            self.checkBox_time.setChecked(doc['Time Implication'])
            self.textEdit_remark.setPlainText(doc['Remark'])
            # Populate linked records
            self.populate_abortive_table(file_ref)
            self.populate_vo_table(file_ref)
            self.populate_sc_vo_table(file_ref)
            # Select the item in the list
            for i in range(self.recordList.count()):
                item = self.recordList.item(i)
                if item.data(32) == file_ref:
                    self.recordList.setCurrentItem(item)
                    break

    def clear_form(self):
        self.lineEdit_file.clear()
        self.lineEdit_title.clear()
        self.lineEdit_from.clear()
        self.lineEdit_to.clear()
        self.textEdit_remark.clear()
        self.checkBox_cost.setChecked(False)
        self.checkBox_time.setChecked(False)
        # Clear tables
        self.table_abortive.setRowCount(0)
        self.table_vo.setRowCount(0)
        self.table_sc_vo.setRowCount(0)
