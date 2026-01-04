from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QPushButton, QMessageBox, QTableWidgetItem, QInputDialog, QLabel
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5 import uic
import os
import datetime

class Ui_SubcontractManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Set root path
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load the .ui file
        ui_path = os.path.join(root_path, 'ui', 'Subcontract_Manager.ui')
        uic.loadUi(ui_path, self)
        
        # Connect signals
        self.btn_create.clicked.connect(self.add_record)
        # Update button removed: Subcontract details auto-save now
        self.recordList.itemClicked.connect(self.load_details)
        
        # Format numeric spinboxes with thousands separators after editing
        try:
            # Ensure the lineEdits exist and connect editingFinished
            self.doubleSpinBox_sum.lineEdit().editingFinished.connect(self.on_sum_edited)
            self.doubleSpinBox_final.lineEdit().editingFinished.connect(self.on_final_edited)
        except Exception:
            pass

        # Add autosave hooks for detail fields
        self.loading_details = False
        try:
            self.lineEdit_name.editingFinished.connect(self.auto_save_subcontract)
            self.lineEdit_company.editingFinished.connect(self.auto_save_subcontract)
            self.comboBox_type.currentIndexChanged.connect(lambda: self.auto_save_subcontract())
        except Exception:
            pass

        # Add buttons for links
        self.add_link_buttons()
        
        # Connect table clicks
        self.table_person.cellClicked.connect(self.on_person_link_clicked)
        self.table_payment.cellClicked.connect(self.on_payment_link_clicked)
        self.table_works.cellClicked.connect(self.on_works_link_clicked)
        self.table_vo.cellClicked.connect(self.on_vo_link_clicked)
        
        # Loading flags
        self.loading_persons = False
        self.loading_details = False

        # Autosave debounce timer + UI save status
        try:
            self._autosave_timer = QTimer(self)
            self._autosave_timer.setSingleShot(True)
            self._autosave_timer.timeout.connect(self.auto_save_subcontract)

            # Connect live-change signals to start autosave debounce
            self.lineEdit_name.textChanged.connect(self._start_autosave)
            self.lineEdit_company.textChanged.connect(self._start_autosave)
            # For spinboxes, use their lineEdit text changes
            try:
                self.doubleSpinBox_sum.lineEdit().textChanged.connect(self._start_autosave)
                self.doubleSpinBox_final.lineEdit().textChanged.connect(self._start_autosave)
            except Exception:
                pass
            # ComboBox changes already call auto_save directly on index change
        except Exception:
            # If UI widgets are missing, ignore
            self._autosave_timer = None

        # Initial Load
        self.refresh_list()

    def refresh_list(self):
        self.recordList.clear()
        # Need get_all_subcontracts in manager
        records = self.manager.get_all_subcontracts()
        for rec in records:
            item = QListWidgetItem(f"{rec['Sub Contract No']} - {rec['Sub Contract Name']}")
            item.setData(32, rec['Sub Contract No'])
            self.recordList.addItem(item)

    def populate_person_links(self, sc_no):
        """Populate the Contact Person table from the 'Sub Contract Person' table."""
        # Prevent itemChanged handlers during population
        self.loading_persons = True
        self.table_person.setRowCount(0)
        # Ensure columns are set
        try:
            self.table_person.setColumnCount(6)
            self.table_person.setHorizontalHeaderLabels(["ID", "Name", "Position", "Tel", "Fax", "Email"])
            # Make ID column narrow
            try:
                self.table_person.setColumnWidth(0, 60)
            except Exception:
                pass
        except Exception:
            pass

        try:
            persons = self.manager.get_subcontract_persons(sc_no)
            for p in persons:
                row = self.table_person.rowCount()
                self.table_person.insertRow(row)
                id_item = QTableWidgetItem(str(p.get('ID', '')))
                # ID should not be editable
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.table_person.setItem(row, 0, id_item)
                self.table_person.setItem(row, 1, QTableWidgetItem(str(p.get('Name', ''))))
                self.table_person.setItem(row, 2, QTableWidgetItem(str(p.get('Position', ''))))
                self.table_person.setItem(row, 3, QTableWidgetItem(str(p.get('Tel', ''))))
                self.table_person.setItem(row, 4, QTableWidgetItem(str(p.get('Fax', ''))))
                self.table_person.setItem(row, 5, QTableWidgetItem(str(p.get('Email', ''))))
        except Exception:
            # Table might not exist or query may fail
            pass
        finally:
            self.loading_persons = False

    def populate_payment_links(self, sc_no):
        """Populate the payment tab with payment application history.
           Prefer to load from Subcontract_Payment_manager (full history). If not available,
           fall back to the older SC Payment Links table."""
        self.table_payment.setRowCount(0)
        # Ensure columns are present even if no data
        self.table_payment.setColumnCount(4)
        self.table_payment.setHorizontalHeaderLabels(["IP", "Draft Date", "This Applied", "Accumulated"])

        # Prefer direct payment applications if payment manager is wired
        apps = []
        if hasattr(self, '_sc_payment_ui') and hasattr(self._sc_payment_ui, 'manager'):
            try:
                apps = self._sc_payment_ui.manager.get_all_payment_applications(sc_no)
            except Exception:
                apps = []

        # debug logging removed

        if apps:
            # Table columns: IP | Draft Date | This Applied Amount | Accumulated Applied
            self.table_payment.setColumnCount(4)
            self.table_payment.setHorizontalHeaderLabels(["IP", "Draft Date", "This Applied", "Accumulated"])
            for app in apps:
                row = self.table_payment.rowCount()
                self.table_payment.insertRow(row)
                try:
                    ip = str(app.get('IP', ''))
                    draft = str(app.get('Draft Date', ''))

                    # Handle possible inconsistent field names for "This Applied Amount"
                    this_applied = None
                    for k in ('This Applied Amount', 'This Appli ed Amount', 'ThisAppliedAmount', 'This Applied'):
                        if k in app:
                            this_applied = app.get(k)
                            break
                    if this_applied is None:
                        this_applied = 0

                    # Handle possible inconsistent field names for "Accumulated Applied Amount"
                    accumulated = None
                    for k in ('Accumulated Applied Amount', 'AccumulatedAppliedAmount', 'Accumulated', 'Accumulated Applied'):
                        if k in app:
                            accumulated = app.get(k)
                            break
                    if accumulated is None:
                        accumulated = 0

                    self.table_payment.setItem(row, 0, QTableWidgetItem(ip))
                    self.table_payment.setItem(row, 1, QTableWidgetItem(draft))
                    self.table_payment.setItem(row, 2, QTableWidgetItem(self.format_number(this_applied)))
                    self.table_payment.setItem(row, 3, QTableWidgetItem(self.format_number(accumulated)))
                except Exception:
                    # Skip problematic row but don't abort whole function
                    continue
        else:
            # Fallback to payment links table (older method)
            links = self.manager.get_sc_payment_links(sc_no)
            # Use same columns but we will only fill IP and Remark; Applied/Accumulated blank
            self.table_payment.setColumnCount(4)
            self.table_payment.setHorizontalHeaderLabels(["IP", "Remark", "This Applied", "Accumulated"])
            for link in links:
                row = self.table_payment.rowCount()
                self.table_payment.insertRow(row)
                self.table_payment.setItem(row, 0, QTableWidgetItem(str(link.get('IP', ''))))
                self.table_payment.setItem(row, 1, QTableWidgetItem(str(link.get('Remark', ''))))
                self.table_payment.setItem(row, 2, QTableWidgetItem(self.format_number(0)))
                self.table_payment.setItem(row, 3, QTableWidgetItem(self.format_number(0)))

    def populate_works_links(self, sc_no):
        """Populate the Works table from the 'Sub Con Works' table (preferred) and fall back to links.

        Columns: Works | Qty | Unit | Rate | Discount | Trade
        """
        # Prevent itemChanged handlers while populating
        self.loading_works = True
        try:
            self.table_works.setRowCount(0)
            # Ensure columns are present
            try:
                # Columns: Works | Qty | Unit | Rate | Discount | Amount | Budget Amount | Trade
                self.table_works.setColumnCount(8)
                self.table_works.setHorizontalHeaderLabels(["Works", "Qty", "Unit", "Rate", "Discount", "Amount", "Budget Amount", "Trade"])
            except Exception:
                pass

            # Prefer direct Sub Con Works table
            try:
                works = self.manager.get_sc_works(sc_no)
            except Exception:
                works = []

            if works:
                for w in works:
                    row = self.table_works.rowCount()
                    self.table_works.insertRow(row)
                    # Works cell — store original value in UserRole for change detection
                    item_works = QTableWidgetItem(str(w.get('Works', '')))
                    item_works.setData(32, w.get('Works', ''))
                    self.table_works.setItem(row, 0, item_works)

                    # Qty, Unit, Rate, Discount
                    self.table_works.setItem(row, 1, QTableWidgetItem(self.format_number(w.get('Qty', 0))))
                    self.table_works.setItem(row, 2, QTableWidgetItem(str(w.get('Unit', ''))))
                    self.table_works.setItem(row, 3, QTableWidgetItem(self.format_number(w.get('Rate', 0))))
                    self.table_works.setItem(row, 4, QTableWidgetItem(self.format_number(w.get('Discount', 0))))

                    # Amount and Budget Amount (read-only)
                    try:
                        amount_item = QTableWidgetItem(self.format_number(w.get('Amount', 0)))
                        amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
                        self.table_works.setItem(row, 5, amount_item)
                    except Exception:
                        self.table_works.setItem(row, 5, QTableWidgetItem(self.format_number(0)))
                    try:
                        # Budget Amount is editable during planning
                        budget_item = QTableWidgetItem(self.format_number(w.get('Budget Amount', 0)))
                        # Ensure the item is editable
                        try:
                            budget_item.setFlags(budget_item.flags() | Qt.ItemIsEditable)
                        except Exception:
                            pass
                        self.table_works.setItem(row, 6, budget_item)
                    except Exception:
                        self.table_works.setItem(row, 6, QTableWidgetItem(self.format_number(0)))

                    self.table_works.setItem(row, 7, QTableWidgetItem(str(w.get('Trade', ''))))
            else:
                # Fallback to older link table
                links = self.manager.get_sc_works_links(sc_no)
                for link in links:
                    row = self.table_works.rowCount()
                    self.table_works.insertRow(row)
                    item_works = QTableWidgetItem(str(link.get('Works Ref', '')))
                    item_works.setData(32, link.get('Works Ref', ''))
                    self.table_works.setItem(row, 0, item_works)
                    self.table_works.setItem(row, 1, QTableWidgetItem('0.00'))
                    self.table_works.setItem(row, 2, QTableWidgetItem(''))
                    self.table_works.setItem(row, 3, QTableWidgetItem('0.00'))
                    self.table_works.setItem(row, 4, QTableWidgetItem('0.00'))
                    amount_item = QTableWidgetItem('0.00')
                    amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
                    self.table_works.setItem(row, 5, amount_item)
                    budget_item = QTableWidgetItem('0.00')
                    try:
                        budget_item.setFlags(budget_item.flags() | Qt.ItemIsEditable)
                    except Exception:
                        pass
                    self.table_works.setItem(row, 6, budget_item)
                    self.table_works.setItem(row, 7, QTableWidgetItem(str(link.get('Remark', ''))))

            try:
                self.table_works.resizeColumnsToContents()
            except Exception:
                pass

            # Ensure the Works column is reasonably wide on initial show
            try:
                # Set the Works column to a comfortable default width
                self.table_works.setColumnWidth(0, 300)
                # Make Trade column slightly wider if present
                if self.table_works.columnCount() > 7:
                    self.table_works.setColumnWidth(7, 140)
            except Exception:
                pass
        finally:
            self.loading_works = False

    def populate_vo_links(self, sc_no):
        """Show SC VO links for the subcontract and expand them to show basic VO info.

        Columns: VO Ref | Description | Application Amount | Agree Amount | Remark
        """
        self.table_vo.setRowCount(0)
        try:
            # Ensure correct columns and headers
            try:
                self.table_vo.setColumnCount(5)
                self.table_vo.setHorizontalHeaderLabels(["VO Ref", "Description", "Application Amount", "Agree Amount", "Remark"])
            except Exception:
                pass

            # Combine linked VO refs from SC VO Links table and direct SC VO records for the subcontract
            vo_refs = []
            try:
                links = self.manager.get_sc_vo_links(sc_no)
                for link in links:
                    ref = link.get('VO ref')
                    if ref and ref not in vo_refs:
                        vo_refs.append(ref)
            except Exception:
                links = []

            try:
                direct_vos = self.manager.get_sc_vos(sc_no)
                for vo in direct_vos:
                    ref = vo.get('VO ref')
                    if ref and ref not in vo_refs:
                        vo_refs.append(ref)
            except Exception:
                direct_vos = []

            # Populate rows for each referenced VO
            for ref in vo_refs:
                vo = None
                try:
                    vo = self.manager.get_sc_vo(ref)
                except Exception:
                    vo = None

                row = self.table_vo.rowCount()
                self.table_vo.insertRow(row)
                # VO Ref
                self.table_vo.setItem(row, 0, QTableWidgetItem(str(ref or '')))
                # Description (from VO record if present)
                desc = ''
                if vo:
                    desc = str(vo.get('Description', ''))
                self.table_vo.setItem(row, 1, QTableWidgetItem(desc))

                # Application Amount and Agree Amount from VO record when available
                app_amt = vo.get('Application Amount', 0) if vo else 0
                agree_amt = vo.get('Agree Amount', 0) if vo else 0
                try:
                    self.table_vo.setItem(row, 2, QTableWidgetItem(self.format_number(app_amt)))
                except Exception:
                    self.table_vo.setItem(row, 2, QTableWidgetItem(str(app_amt)))
                try:
                    self.table_vo.setItem(row, 3, QTableWidgetItem(self.format_number(agree_amt)))
                except Exception:
                    self.table_vo.setItem(row, 3, QTableWidgetItem(str(agree_amt)))

                # Remark column: try to use link remark if present
                remark = ''
                try:
                    for l in links:
                        if l.get('VO ref') == ref:
                            remark = str(l.get('Remark', ''))
                            break
                except Exception:
                    pass
                self.table_vo.setItem(row, 4, QTableWidgetItem(remark))

            # Resize columns to contents for readability
            try:
                self.table_vo.resizeColumnsToContents()
            except Exception:
                pass
        except Exception as e:
            # Table might not exist yet, just leave table empty
            pass

    def add_record(self):
        # Get next SC no
        no = self.manager.get_next_sc_no()
        
        # Get the last record to copy data
        records = self.manager.get_all_subcontracts()
        if records:
            last_rec = records[-1]
            # Copy data with new no
            name = last_rec['Sub Contract Name']
            company = last_rec['Company Name']
            ctype = last_rec['Contract Type']
            sum_val = last_rec['Contract Sum']
            final_val = last_rec['Final Account Amount']
        else:
            # Defaults
            name = ""
            company = ""
            ctype = ""
            sum_val = 0.0
            final_val = 0.0
        
        # Add the new record
        self.manager.add_subcontract(no, name, company, ctype, sum_val, final_val)
        self.refresh_list()
        # Select the new item
        for i in range(self.recordList.count()):
            item = self.recordList.item(i)
            if item.data(32) == no:
                self.recordList.setCurrentItem(item)
                self.load_details(item)
                break

    def add_link_buttons(self):
        # Add buttons to person tab
        person_layout = self.tab_person.layout()
        btn_layout = QHBoxLayout()
        self.btn_add_person = QPushButton("Add Person")
        self.btn_delete_person = QPushButton("Delete Person")
        btn_layout.addWidget(self.btn_add_person)
        btn_layout.addWidget(self.btn_delete_person)
        person_layout.addLayout(btn_layout)

        # Contract Type buttons are placed next to the Contract Type combo in the form when available.
        # If the UI did not provide them (older layouts), add them as a fallback under the Person tab.
        if not hasattr(self, 'btn_add_contract_type') or not hasattr(self, 'btn_delete_contract_type'):
            type_btn_layout = QHBoxLayout()
            self.btn_add_contract_type = QPushButton("Add Contract Type")
            self.btn_delete_contract_type = QPushButton("Delete Contract Type")
            type_btn_layout.addWidget(self.btn_add_contract_type)
            type_btn_layout.addWidget(self.btn_delete_contract_type)
            person_layout.addLayout(type_btn_layout)
        
        # Add buttons to payment tab (show history only; creation happens in Sub Contract Payment)
        payment_layout = self.tab_payment.layout()
        btn_layout_payment = QHBoxLayout()
        # Apply New Payment button will navigate to Sub Contract Payment tab and prefill subcontract & date
        self.btn_apply_payment = QPushButton("Apply New Payment")
        self.btn_apply_payment.setToolTip("Open Sub Contract Payment page and start a new IP with today's date")
        btn_layout_payment.addWidget(self.btn_apply_payment)
        payment_layout.addLayout(btn_layout_payment)
        # Note: We keep the payment tab enabled to show history, but creation of new payments is handled
        # in the dedicated 'Sub Contract Payment' tab. Add/del payment link buttons removed.

        
        # Add buttons to works tab
        works_layout = self.tab_works.layout()
        btn_layout_works = QHBoxLayout()
        self.btn_add_works = QPushButton("Add Works")
        self.btn_delete_works = QPushButton("Delete Works")
        btn_layout_works.addWidget(self.btn_add_works)
        btn_layout_works.addWidget(self.btn_delete_works)
        works_layout.addLayout(btn_layout_works)
        
        # Add buttons to vo tab
        vo_layout = self.tab_vo.layout()
        btn_layout_vo = QHBoxLayout()
        # Change VO button to offer navigation to the full SC VO manager (Add New VO)
        self.btn_add_vo = QPushButton("Add New VO")
        btn_layout_vo.addWidget(self.btn_add_vo)
        vo_layout.addLayout(btn_layout_vo)
        
        # Connect link buttons
        self.btn_add_person.clicked.connect(self.add_person_link)
        self.btn_delete_person.clicked.connect(self.delete_person_link)
        # Contract type buttons
        self.btn_add_contract_type.clicked.connect(self.add_contract_type)
        self.btn_delete_contract_type.clicked.connect(self.delete_contract_type)
        # Payment add/delete removed — replaced by Apply New Payment button
        self.btn_apply_payment.clicked.connect(self.apply_new_payment)
        self.btn_add_works.clicked.connect(self.add_works_link)
        self.btn_delete_works.clicked.connect(self.delete_works_link)
        # When clicked, open the Sub Contract VO page and preselect or create VO for this subcontract
        self.btn_add_vo.clicked.connect(self.open_sc_vo_page) 

        # Autosave edits in person table
        try:
            self.table_person.itemChanged.connect(self.on_person_cell_changed)
        except Exception:
            pass

        # Autosave edits in works table
        try:
            self.table_works.itemChanged.connect(self.on_works_cell_changed)
        except Exception:
            pass

    def update_record(self):
        no = self.lineEdit_no.text()
        name = self.lineEdit_name.text()
        company = self.lineEdit_company.text()
        ctype = self.comboBox_type.currentText()
        sum_val = self.doubleSpinBox_sum.value()
        final_val = self.doubleSpinBox_final.value()
        
        data = {
            "Sub Contract Name": name,
            "Company Name": company,
            "Contract Type": ctype,
            "Contract Sum": sum_val,
            "Final Account Amount": final_val
        }
        self.manager.update_subcontract(no, data)
        self.refresh_list()

    def load_details(self, item):
        # Prevent autosave while filling UI fields
        self.loading_details = True
        try:
            no = item.data(32)
            rec = self.manager.get_subcontract(no)  # Need to add get_subcontract
            if rec:
                self.lineEdit_no.setText(rec['Sub Contract No'])
                self.lineEdit_name.setText(rec['Sub Contract Name'])
                self.lineEdit_company.setText(rec['Company Name'])
                # Contract type will be set after refreshing contract types to avoid transient wrong selections
                self.doubleSpinBox_sum.setValue(rec['Contract Sum'])
                # Show formatted in line edit
                try:
                    self.doubleSpinBox_sum.lineEdit().setText(self.format_number(rec['Contract Sum']))
                except Exception:
                    pass
                self.doubleSpinBox_final.setValue(rec['Final Account Amount'])
                try:
                    self.doubleSpinBox_final.lineEdit().setText(self.format_number(rec['Final Account Amount']))
                except Exception:
                    pass

                # Populate link tables
                self.populate_person_links(no)
                self.populate_payment_links(no)
                self.populate_works_links(no)
                self.populate_vo_links(no)

                # Refresh contract type list to ensure UI stays current
                try:
                    self.refresh_contract_types()
                except Exception:
                    pass

                # Ensure the contract type value exists in the combo, otherwise add it temporarily and set it.
                try:
                    cur_type = rec.get('Contract Type') or ''
                    found = False
                    for i in range(self.comboBox_type.count()):
                        if self.comboBox_type.itemText(i) == cur_type:
                            found = True
                            break
                    if not found and cur_type:
                        print(f"Debug: Contract type '{cur_type}' missing from combo; adding temporarily.")
                        self.comboBox_type.addItem(cur_type)
                    # Now set the combo to the desired value
                    self.comboBox_type.setCurrentText(cur_type)
                except Exception:
                    pass

                # Keep a copy of the loaded record for change detection during autosave
                try:
                    self._loaded_rec = rec.copy()
                except Exception:
                    # Fallback: build minimal dict
                    self._loaded_rec = {
                        'Sub Contract No': rec.get('Sub Contract No'),
                        'Sub Contract Name': rec.get('Sub Contract Name'),
                        'Company Name': rec.get('Company Name'),
                        'Contract Type': rec.get('Contract Type'),
                        'Contract Sum': rec.get('Contract Sum'),
                        'Final Account Amount': rec.get('Final Account Amount')
                    }
        finally:
            self.loading_details = False

    def format_number(self, value):
        """Format number with thousand separators and 2 decimals."""
        try:
            return "{:,.2f}".format(float(value))
        except Exception:
            return "0.00"

    def load_sc_vo_by_ref(self, vo_ref):
        rec = self.manager.get_sc_vo(vo_ref)
        if rec:
            # Populate the form with SC VO data, but the UI is for subcontracts
            # Perhaps the UI needs to be changed, but for now, just set what matches
            self.lineEdit_no.setText(rec['VO ref'])
            self.lineEdit_name.setText(rec['Description'])
            # etc.
            # Select in list if possible, but list is for subcontracts
            pass

    def set_sc_payment_ui(self, sc_payment_ui, tab_widget):
        """Provide reference to the Subcontract Payment UI and the main tab widget so
           we can navigate and prefill values when applying a new payment."""
        self._sc_payment_ui = sc_payment_ui
        self._main_tab_widget = tab_widget

    def set_sc_vo_ui(self, sc_vo_ui, tab_widget):
        """Provide reference to the Sub Contract VO UI and the main tab widget so
           we can navigate to the SC VO page and prefill the subcontract."""
        self._sc_vo_ui = sc_vo_ui
        self._main_tab_widget = tab_widget

    def open_sc_vo_page(self):
        """Open the Sub Contract VO page and show VO records for the current subcontract.

        If existing SC VO(s) exist, select the first one. Otherwise prefill the form to add a new VO for this subcontract.
        """
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)

        if not hasattr(self, '_sc_vo_ui') or not hasattr(self, '_main_tab_widget'):
            QMessageBox.warning(self, "Not Configured", "Sub Contract VO UI not wired. Please restart or contact admin.")
            return

        try:
            # Refresh SC VO list (always show full list) and then select the related SC VO
            self._sc_vo_ui.refresh_list()

            # Ensure subcontract combo includes the current subcontract and set it
            try:
                # Add to combo if missing
                if self._sc_vo_ui.comboBox_subcontract.findText(sc_no) == -1:
                    self._sc_vo_ui.comboBox_subcontract.addItem(sc_no)
                self._sc_vo_ui.comboBox_subcontract.setCurrentText(sc_no)
            except Exception:
                pass

            # Create a new SC VO record and link it to this subcontract, then select it
            try:
                vo_ref = self._sc_vo_ui.manager.get_next_sc_vo_ref()
                today = QDate.currentDate().toString("yyyy-MM-dd")
                # Create an empty VO record linked to this subcontract
                self._sc_vo_ui.manager.create_sc_vo(vo_ref, sc_no, today, today, "", 0, 0, False, False, False, False, "")
                # Also create a link record so Subcontract VO links show this VO
                try:
                    self.manager.add_sc_vo_link(sc_no, vo_ref, "")
                except Exception:
                    pass
                # Refresh SC VO UI (full list) and local VO links table
                self._sc_vo_ui.refresh_list()
                self.populate_vo_links(sc_no)

                # Select the newly created item and load its details (table view)
                found = False
                try:
                    for r in range(self._sc_vo_ui.table_sc_vos.rowCount()):
                        try:
                            if self._sc_vo_ui.table_sc_vos.item(r, 0).text() == vo_ref:
                                self._sc_vo_ui.table_sc_vos.selectRow(r)
                                self._sc_vo_ui.load_details_by_ref(vo_ref)
                                found = True
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

                if not found:
                    # fallback: try selecting in table view
                    try:
                        for r in range(self._sc_vo_ui.table_sc_vos.rowCount()):
                            if self._sc_vo_ui.table_sc_vos.item(r, 0).text() == vo_ref:
                                self._sc_vo_ui.table_sc_vos.selectRow(r)
                                self._sc_vo_ui.load_details_by_ref(vo_ref)
                                break
                    except Exception:
                        pass

                # Inform user of created VO ref
                try:
                    QMessageBox.information(self, "New SC VO Created", f"Created new SC VO: {vo_ref}")
                except Exception:
                    pass

                # Return the created VO ref for programmatic use
                return vo_ref
            except Exception as e:
                print(f"Error creating SC VO: {e}")
                # fallback: clear form and prefill subcontract
                try:
                    self._sc_vo_ui.clear_form()
                    self._sc_vo_ui.comboBox_subcontract.setCurrentText(sc_no)
                    try:
                        self._sc_vo_ui.lineEdit_desc.setFocus()
                    except Exception:
                        pass
                except Exception:
                    pass

            # Switch to the SC VO tab
            try:
                self._main_tab_widget.setCurrentWidget(self._sc_vo_ui)
            except Exception:
                # If main tab widget does not accept widget directly, search by tab index
                try:
                    for i in range(self._main_tab_widget.count()):
                        if self._main_tab_widget.widget(i) == self._sc_vo_ui:
                            self._main_tab_widget.setCurrentIndex(i)
                            break
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Sub Contract VO: {str(e)}")

    def apply_new_payment(self):
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)

        # Ensure target UI is wired
        if not hasattr(self, '_sc_payment_ui') or not hasattr(self, '_main_tab_widget'):
            QMessageBox.warning(self, "Not Configured", "Subcontract Payment UI not wired. Please restart or contact admin.")
            return

        try:
            # Load and select subcontract in payment UI
            self._sc_payment_ui.load_subcontracts()
            # Find index for this subcontract
            for i in range(self._sc_payment_ui.combo_subcontract.count()):
                if self._sc_payment_ui.combo_subcontract.itemData(i) == sc_no:
                    self._sc_payment_ui.combo_subcontract.setCurrentIndex(i)
                    break

            # Create a new IP (this will set draft date to today and select the new IP)
            self._sc_payment_ui.add_ip()

            # Switch to the Sub Contract Payment tab
            self._main_tab_widget.setCurrentWidget(self._sc_payment_ui)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Subcontract Payment: {str(e)}")

    def add_person_link(self):
        """Quick-add an empty contact person record (ID assigned by DB); user will edit inline."""
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)

        try:
            new_id = self.manager.add_subcontract_person(sc_no, "", "", "", "", "")
            self.populate_person_links(sc_no)
            # Select the new row and start editing Name cell
            for r in range(self.table_person.rowCount()):
                try:
                    if int(self.table_person.item(r, 0).text()) == int(new_id):
                        self.table_person.setCurrentCell(r, 1)
                        try:
                            self.table_person.editItem(self.table_person.item(r, 1))
                        except Exception:
                            pass
                        break
                except Exception:
                    continue
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add contact person: {str(e)}")

    def refresh_contract_types(self):
        """Reload contract type values into the combo box."""
        self.comboBox_type.clear()
        types = self.manager.get_contract_types()
        type_names = [t['Contract Type'] for t in types]
        if "Undefined" not in type_names:
            # ensure an Undefined exists
            try:
                self.manager.add_contract_type("Undefined")
                types = self.manager.get_contract_types()
            except Exception:
                pass
        for t in types:
            self.comboBox_type.addItem(t['Contract Type'])

    def on_sum_edited(self):
        """Normalize user input and show formatted number in the spinbox line edit."""
        try:
            text = self.doubleSpinBox_sum.lineEdit().text()
            val = self.parse_formatted_number(text)
            self.doubleSpinBox_sum.setValue(val)
            # Show formatted
            self.doubleSpinBox_sum.lineEdit().setText(self.format_number(val))
        except Exception:
            pass

    def on_final_edited(self):
        """Normalize user input and show formatted number in the spinbox line edit."""
        try:
            text = self.doubleSpinBox_final.lineEdit().text()
            val = self.parse_formatted_number(text)
            self.doubleSpinBox_final.setValue(val)
            # Show formatted
            self.doubleSpinBox_final.lineEdit().setText(self.format_number(val))
            # Autosave after user edits
            try:
                self.auto_save_subcontract()
            except Exception:
                pass
        except Exception:
            pass

    def add_contract_type(self):
        name, ok = QInputDialog.getText(self, "Add Contract Type", "Type Name:")
        if ok and name:
            try:
                self.manager.add_contract_type(name)
                self.refresh_contract_types()
                self.comboBox_type.setCurrentText(name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add contract type: {str(e)}")

    def _start_autosave(self):
        """Start or restart the autosave debounce timer."""
        try:
            if self._autosave_timer:
                self._autosave_timer.start(800)
        except Exception:
            pass

    def auto_save_subcontract(self):
        """Autosave the current subcontract detail fields into the database.

        Only changed fields will be written to avoid overwriting concurrent changes from others.
        Adds debug prints to help diagnose why Contract Type might not persist.
        """
        if getattr(self, 'loading_details', False):
            return
        current_item = self.recordList.currentItem()
        if not current_item:
            return
        sc_no = current_item.data(32)
        data = {
            "Sub Contract Name": self.lineEdit_name.text(),
            "Company Name": self.lineEdit_company.text(),
            "Contract Type": self.comboBox_type.currentText(),
            "Contract Sum": self.doubleSpinBox_sum.value(),
            "Final Account Amount": self.doubleSpinBox_final.value()
        }

        # Compute changed fields compared to the last loaded record (if available)
        base = getattr(self, '_loaded_rec', None)
        if base:
            changed = {}
            for k, v in data.items():
                if base.get(k) != v:
                    changed[k] = v
            if not changed:
                # Nothing changed; show brief saved feedback and skip DB write
                try:
                    if hasattr(self, 'label_save_status'):
                        self.label_save_status.setText('Saved')
                        QTimer.singleShot(1500, lambda: self.label_save_status.setText(''))
                except Exception:
                    pass
                return
        else:
            changed = data

        try:
            rows = self.manager.update_subcontract(sc_no, changed)

            # verify saved by reloading record and checking changed fields
            rec = None
            try:
                rec = self.manager.get_subcontract(sc_no)
                mismatch = False
                for k, v in changed.items():
                    if not rec or rec.get(k) != v:
                        mismatch = True
                        break
                if mismatch:
                    # Try retrying single-field saves (helpful when one field is problematic)
                    try:
                        for k, v in changed.items():
                            self.manager.update_subcontract(sc_no, {k: v})
                    except Exception:
                        pass
                    rec2 = self.manager.get_subcontract(sc_no)
                    for k, v in changed.items():
                        if not rec2 or rec2.get(k) != v:
                            QMessageBox.warning(self, "Save Failed", "Changes were not persisted to the database. Please try again or check DB schema.")
                            if hasattr(self, 'label_save_status'):
                                self.label_save_status.setText('Error')
                                QTimer.singleShot(1500, lambda: self.label_save_status.setText(''))
                            return
            except Exception:
                # get_subcontract failed after update - show warning
                pass

            # Update the list string for the item
            for i in range(self.recordList.count()):
                item = self.recordList.item(i)
                if item.data(32) == sc_no:
                    item.setText(f"{sc_no} - {data['Sub Contract Name']}")
                    break

            # Show saved feedback
            try:
                if hasattr(self, 'label_save_status'):
                    self.label_save_status.setText('Saved')
                    QTimer.singleShot(1500, lambda: self.label_save_status.setText(''))
            except Exception:
                pass

            # Update cached loaded record
            if rec:
                try:
                    self._loaded_rec = rec.copy()
                except Exception:
                    self._loaded_rec = {k: rec.get(k) for k in ('Sub Contract No', 'Sub Contract Name', 'Company Name', 'Contract Type', 'Contract Sum', 'Final Account Amount')}
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to autosave: {e}")

    def delete_contract_type(self):
        current = self.comboBox_type.currentText()
        if not current:
            return
        if current == "Undefined":
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the 'Undefined' type.")
            return

        if self.manager.is_contract_type_used(current):
            reply = QMessageBox.question(self, "Type in Use", f"This type is used by subcontracts. Set those subcontracts' type to 'Undefined' and delete the type '{current}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.manager.update_subcontracts_type(current, "Undefined")
                    self.manager.delete_contract_type(current)
                    self.refresh_contract_types()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete contract type: {str(e)}")
        else:
            reply = QMessageBox.question(self, "Confirm Delete", f"Delete contract type '{current}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.manager.delete_contract_type(current)
                    self.refresh_contract_types()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete contract type: {str(e)}")

    def delete_person_link(self):
        """Delete the selected contact person record from 'Sub Contract Person'."""
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)
        row = self.table_person.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Person Selected", "Please select a contact person to delete.")
            return
        try:
            person_id = int(self.table_person.item(row, 0).text())
        except Exception:
            QMessageBox.warning(self, "Invalid Selection", "Selected row does not contain a valid ID.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete contact person ID {person_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            self.manager.delete_subcontract_person(person_id)
            QMessageBox.information(self, "Deleted", f"Deleted contact person {person_id}.")
            self.populate_person_links(sc_no)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete contact person: {str(e)}")

    def on_person_cell_changed(self, item):
        """Autosave changes to a contact person cell into database."""
        if getattr(self, 'loading_persons', False):
            return
        row = item.row()
        col = item.column()
        # Column mapping: 1=Name,2=Position,3=Tel,4=Fax,5=Email
        col_map = {1: 'Name', 2: 'Position', 3: 'Tel', 4: 'Fax', 5: 'Email'}
        if col == 0:
            # ID column is not editable
            return
        field = col_map.get(col)
        if not field:
            return
        try:
            person_id = int(self.table_person.item(row, 0).text())
        except Exception:
            return
        value = item.text()
        try:
            self.manager.update_subcontract_person(person_id, {field: value})
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save change: {e}")

    def on_works_cell_changed(self, item):
        """Autosave changes to a works cell into database. Works row is identified by Subcontract + original Works value stored in UserRole of column 0."""
        if getattr(self, 'loading_works', False):
            return
        row = item.row()
        col = item.column()
        # Column mapping: 0=Works,1=Qty,2=Unit,3=Rate,4=Discount,5=Amount,6=Budget Amount,7=Trade
        col_map = {0: 'Works', 1: 'Qty', 2: 'Unit', 3: 'Rate', 4: 'Discount', 5: 'Amount', 6: 'Budget Amount', 7: 'Trade'}
        field = col_map.get(col)
        if not field:
            return
        # Amount is computed and read-only in the UI; ignore manual edits
        if field == 'Amount':
            return
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            return
        sc_no = current_sc_item.data(32)

        # Determine original works key from stored UserRole on column 0
        try:
            original_item = self.table_works.item(row, 0)
            original_key = original_item.data(32) if original_item and original_item.data(32) else original_item.text()
        except Exception:
            original_key = None

        # Build data to update
        try:
            # For numeric fields, try to parse
            if field in ('Rate', 'Discount'):
                try:
                    value = float(item.text().replace(',', ''))
                except Exception:
                    value = 0
            elif field == 'Qty':
                try:
                    value = float(item.text().replace(',', ''))
                except Exception:
                    value = 0
            else:
                value = item.text()

            # If updating the Works name (column 0), need to replace the key
            if field == 'Works':
                # Use original_key to identify row and new name as value
                if not original_key:
                    return
                data = {'Works': value}
                try:
                    self.manager.update_sc_work(sc_no, original_key, data)
                    # Update stored key to new value so future edits find the row
                    try:
                        self.table_works.item(row, 0).setData(32, value)
                    except Exception:
                        pass
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save change: {e}")
            else:
                # For other fields, update using the original Works key
                if not original_key:
                    return
                data = {field: value}
                try:
                    self.manager.update_sc_work(sc_no, original_key, data)
                    # After updating numeric fields, refresh Amount and Budget Amount from DB for this work row
                    try:
                        works_rows = self.manager.get_sc_works(sc_no)
                        found_row = None
                        key_to_find = value if field == 'Works' else original_key
                        for wr in works_rows:
                            if wr.get('Works') == key_to_find:
                                found_row = wr
                                break
                        if found_row:
                            # update Amount and Budget Amount cells in UI
                                amt = found_row.get('Amount', 0)
                                bud = found_row.get('Budget Amount', 0)
                                # Find the UI row that matches
                                for r in range(self.table_works.rowCount()):
                                    try:
                                        ui_key = self.table_works.item(r, 0).data(32) if self.table_works.item(r, 0) and self.table_works.item(r, 0).data(32) else self.table_works.item(r, 0).text()
                                        if ui_key == key_to_find:
                                            # Format and set amount cells
                                            try:
                                                self.loading_works = True
                                                amt_item = QTableWidgetItem(self.format_number(amt))
                                                amt_item.setFlags(amt_item.flags() & ~Qt.ItemIsEditable)
                                                self.table_works.setItem(r, 5, amt_item)
                                                # Budget is editable by user during planning
                                                bud_item = QTableWidgetItem(self.format_number(bud))
                                                try:
                                                    bud_item.setFlags(bud_item.flags() | Qt.ItemIsEditable)
                                                except Exception:
                                                    pass
                                                self.table_works.setItem(r, 6, bud_item)
                                                # Also update edited cell display
                                                if field in ('Rate', 'Discount', 'Qty', 'Budget Amount'):
                                                    item.setText(self.format_number(value))
                                                else:
                                                    item.setText(str(value))
                                            finally:
                                                self.loading_works = False
                                            break
                                    except Exception:
                                        continue
                    except Exception:
                        pass
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save change: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save change: {e}")
    def add_payment_link(self):
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)
        
        # Get IP number from user input
        ip_no, ok = QInputDialog.getInt(self, "Add Payment Link", "Enter IP Number:")
        if ok:
            remark, ok2 = QInputDialog.getText(self, "Add Payment Link", "Enter remark (optional):")
            if ok2:
                try:
                    self.manager.add_sc_payment_link(sc_no, ip_no, remark)
                    QMessageBox.information(self, "Link Added", f"Linked IP {ip_no} to subcontract {sc_no}")
                    self.populate_payment_links(sc_no)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add payment link: {str(e)}")

    def delete_payment_link(self):
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)
        row = self.table_payment.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Payment Selected", "Please select a payment link to delete.")
            return
        ip_no = self.table_payment.item(row, 0).text()
        try:
            self.manager.delete_sc_payment_link(sc_no, int(ip_no))
            QMessageBox.information(self, "Deleted", f"Deleted payment link {ip_no}.")
            self.populate_payment_links(sc_no)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete payment link: {str(e)}")

    def add_works_link(self):
        """Add a new Sub Con Works record linked to the selected subcontract and start editing it."""
        import uuid
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)

        try:
            # Create a unique placeholder for the Works field to ensure we can reliably update this row later
            placeholder = f"__NEWWORK_{uuid.uuid4().hex[:8]}"
            new_rowid = self.manager.add_sc_work(sc_no, placeholder, 0, "", 0, 0, "")
            # Refresh works table from direct table
            self.populate_works_links(sc_no)

            # Find the placeholder row and start editing its Works cell
            try:
                for r in range(self.table_works.rowCount()):
                    try:
                        if self.table_works.item(r, 0).data(32) == placeholder or self.table_works.item(r, 0).text() == placeholder:
                            self.table_works.setCurrentCell(r, 0)
                            try:
                                self.table_works.editItem(self.table_works.item(r, 0))
                            except Exception:
                                pass
                            break
                    except Exception:
                        continue
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add works record: {str(e)}")

    def delete_works_link(self):
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
            return
        sc_no = current_sc_item.data(32)
        row = self.table_works.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Works Selected", "Please select a works link to delete.")
            return
        # Use the stored original works value when available
        try:
            works_item = self.table_works.item(row, 0)
            works_ref = works_item.data(32) if works_item and works_item.data(32) else works_item.text()
        except Exception:
            works_ref = self.table_works.item(row, 0).text()
        try:
            # Prefer deleting from direct table
            try:
                self.manager.delete_sc_work(sc_no, works_ref)
            except Exception:
                # fallback to link deletion
                self.manager.delete_sc_works_link(sc_no, works_ref)
            QMessageBox.information(self, "Deleted", f"Deleted works link {works_ref}.")
            self.populate_works_links(sc_no)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete works link: {str(e)}")



    def on_person_link_clicked(self, row, column):
        # Handle person table click
        pass

    def on_payment_link_clicked(self, row, column):
        # Handle payment table click: open Subcontract Payment UI and select the payment (IP)
        current_sc_item = self.recordList.currentItem()
        if not current_sc_item:
            return
        sc_no = current_sc_item.data(32)
        # Get selected IP
        try:
            ip_text = self.table_payment.item(row, 0).text()
            ip_no = int(ip_text)
        except Exception:
            return

        # Ensure target UI is wired
        if not hasattr(self, '_sc_payment_ui') or not hasattr(self, '_main_tab_widget'):
            QMessageBox.warning(self, "Not Configured", "Subcontract Payment UI not wired. Please restart or contact admin.")
            return

        try:
            # Load subcontracts and select this subcontract
            self._sc_payment_ui.load_subcontracts()
            for i in range(self._sc_payment_ui.combo_subcontract.count()):
                if self._sc_payment_ui.combo_subcontract.itemData(i) == sc_no:
                    self._sc_payment_ui.combo_subcontract.setCurrentIndex(i)
                    break

            # Refresh IPs and select the IP if exists
            self._sc_payment_ui.refresh_ips()
            for i in range(self._sc_payment_ui.ip_list.count()):
                item = self._sc_payment_ui.ip_list.item(i)
                if item.data(Qt.UserRole) == ip_no:
                    self._sc_payment_ui.ip_list.setCurrentItem(item)
                    self._sc_payment_ui.on_ip_selected(item)
                    break

            # Switch to the Sub Contract Payment tab
            self._main_tab_widget.setCurrentWidget(self._sc_payment_ui)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Subcontract Payment: {str(e)}")

    def on_works_link_clicked(self, row, column):
        # Handle works table click
        pass

    def on_vo_link_clicked(self, row, column):
        """Handle VO table click: open the Sub Contract VO page and select the clicked VO."""
        try:
            # Get VO ref from clicked row
            try:
                vo_ref = self.table_vo.item(row, 0).text()
            except Exception:
                return

            current_sc_item = self.recordList.currentItem()
            if not current_sc_item:
                QMessageBox.warning(self, "No Subcontract Selected", "Please select a subcontract first.")
                return
            sc_no = current_sc_item.data(32)

            # Ensure target UI is wired
            if not hasattr(self, '_sc_vo_ui') or not hasattr(self, '_main_tab_widget'):
                QMessageBox.warning(self, "Not Configured", "Sub Contract VO UI not wired. Please restart or contact admin.")
                return

            # Refresh SC VO UI (full list) so the VO appears in its list/table
            try:
                self._sc_vo_ui.refresh_list()
            except Exception:
                pass

            # Ensure subcontract combo includes the current subcontract and set it
            try:
                if self._sc_vo_ui.comboBox_subcontract.findText(sc_no) == -1:
                    self._sc_vo_ui.comboBox_subcontract.addItem(sc_no)
                self._sc_vo_ui.comboBox_subcontract.setCurrentText(sc_no)
            except Exception:
                pass

            # Try to find VO in the SC VO table
            found = False
            try:
                for r in range(self._sc_vo_ui.table_sc_vos.rowCount()):
                    try:
                        if self._sc_vo_ui.table_sc_vos.item(r, 0).text() == vo_ref:
                            self._sc_vo_ui.table_sc_vos.selectRow(r)
                            self._sc_vo_ui.load_details_by_ref(vo_ref)
                            found = True
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # Fallback: try selecting in the table view
            if not found:
                try:
                    for r in range(self._sc_vo_ui.table_sc_vos.rowCount()):
                        try:
                            if self._sc_vo_ui.table_sc_vos.item(r, 0).text() == vo_ref:
                                self._sc_vo_ui.table_sc_vos.selectRow(r)
                                self._sc_vo_ui.load_details_by_ref(vo_ref)
                                found = True
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

            # Switch to the SC VO tab
            try:
                self._main_tab_widget.setCurrentWidget(self._sc_vo_ui)
            except Exception:
                try:
                    for i in range(self._main_tab_widget.count()):
                        if self._main_tab_widget.widget(i) == self._sc_vo_ui:
                            self._main_tab_widget.setCurrentIndex(i)
                            break
                except Exception:
                    pass

            if not found:
                QMessageBox.information(self, "VO Not Found", f"VO {vo_ref} was not found in the SC VO list, but the page was opened.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Subcontract VO: {str(e)}")

    def show_add_link_dialog(self, title, label, items, ref_key):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QLineEdit, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        
        label_widget = QLabel(label)
        layout.addWidget(label_widget)
        
        combo = QComboBox()
        combo.addItems([str(item[ref_key]) for item in items])
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
        self.lineEdit_no.clear()
        self.lineEdit_name.clear()
        self.lineEdit_company.clear()
        self.doubleSpinBox_sum.setValue(0)
        self.doubleSpinBox_final.setValue(0)
