import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PyQt5 import uic

# Set root path
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from function.DB_manager import DB_Manager
from function.Doc_manager import Doc_Manager
from function.Abortive_manager import Abortive_Manager
from function.Payment_Application_manager import Payment_Application_Manager
from function.Subcontract_manager import Subcontract_Manager
from function.Budget_manager import Budget_Manager
from function.BQ_manager import BQ_Manager
from function.MC_VO_manager import MC_VO_Manager
from function.SC_VO_manager import SC_VO_Manager
from function.Subcontract_Payment_manager import Subcontract_Payment_Manager
from function.Contra_Charge_manager import Contra_Charge_Manager
from ui.Ui_SC_ContraChargeManager import Ui_SC_ContraChargeManager

# Import UI classes
from ui.Ui_DocManager import Ui_DocManager
from ui.Ui_AbortiveManager import Ui_AbortiveManager
from ui.Ui_PaymentManager import Ui_PaymentManager
from ui.Ui_SubcontractManager import Ui_SubcontractManager
from ui.Ui_BudgetManager import Ui_BudgetManager
from ui.Ui_BQManager import Ui_BQManager
from ui.Ui_MC_VOManager import Ui_MC_VOManager
from ui.Ui_SC_VOManager import Ui_SC_VOManager
from ui.Ui_SubcontractPaymentManager import Ui_SubcontractPaymentManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the Main Window UI
        ui_path = os.path.join(ROOT_PATH, 'ui', 'Main.ui')
        uic.loadUi(ui_path, self)

        # Initialize Database
        db_path = os.path.join(ROOT_PATH, "database", "QS_Project.db")
        self.db_manager = DB_Manager(db_path)
        # Create tables if they don't exist (using the schema file)
        # self.db_manager.create_tables_from_schema(os.path.join(root_path, "database", "Project_db_Schema.txt")) 

        # Initialize Managers
        self.doc_manager = Doc_Manager(self.db_manager)
        self.abortive_manager = Abortive_Manager(self.db_manager)
        self.payment_manager = Payment_Application_Manager(self.db_manager)
        self.mc_vo_manager = MC_VO_Manager(self.db_manager)
        self.subcontract_manager = Subcontract_Manager(self.db_manager)
        self.sc_vo_manager = SC_VO_Manager(self.db_manager)
        self.budget_manager = Budget_Manager(self.db_manager)
        self.bq_manager = BQ_Manager(self.db_manager)
        self.sc_payment_manager = Subcontract_Payment_Manager(self.db_manager)
        # Contra Charge manager
        self.contra_charge_manager = Contra_Charge_Manager(self.db_manager)
        # Ensure "Contra Charge Document" link table exists (migration)
        try:
            create_sql = '''CREATE TABLE IF NOT EXISTS "Contra Charge Document" ("CC No" TEXT REFERENCES "Contra Charge" ("CC No") ON DELETE CASCADE ON UPDATE CASCADE, "Doc Ref" TEXT REFERENCES "Document Manager" (File) ON DELETE CASCADE ON UPDATE CASCADE, Remark TEXT, PRIMARY KEY ("CC No", "Doc Ref"))'''
            # Use DB manager's execute_query to run SQL
            self.db_manager.execute_query(create_sql)
        except Exception as e:
            # Log migration failure but continue
            print(f"Failed to ensure Contra Charge Document table exists: {e}")
        

        # Setup UI Tabs
        # Access the tabWidget defined in Main.ui
        
        # Set tab position (options: North, South, West, East)
        self.tabWidget.setTabPosition(QTabWidget.North)  # Change to desired position
        
        self.ui_doc = Ui_DocManager(self.doc_manager)
        self.ui_abortive = Ui_AbortiveManager(self.abortive_manager)
        self.ui_payment = Ui_PaymentManager(self.payment_manager)
        self.ui_subcontract = Ui_SubcontractManager(self.subcontract_manager)
        self.ui_budget = Ui_BudgetManager(self.budget_manager)
        self.ui_bq = Ui_BQManager(self.bq_manager)
        self.ui_mc_vo = Ui_MC_VOManager(self.mc_vo_manager)
        self.ui_sc_vo = Ui_SC_VOManager(self.sc_vo_manager)
        self.ui_sc_payment = Ui_SubcontractPaymentManager(self.sc_payment_manager, self.subcontract_manager)
        self.ui_sc_contra = Ui_SC_ContraChargeManager(self.contra_charge_manager, self.subcontract_manager)
        
        # Wire Subcontract UI to Subcontract Payment UI so Apply New button can navigate & prefill
        try:
            self.ui_subcontract.set_sc_payment_ui(self.ui_sc_payment, self.tabWidget)
        except Exception:
            pass

        # Wire Subcontract UI to Subcontract VO UI so Add New VO button can navigate & prefill
        try:
            self.ui_subcontract.set_sc_vo_ui(self.ui_sc_vo, self.tabWidget)
        except Exception:
            pass

        self.tabWidget.addTab(self.ui_doc, "Document")
        self.tabWidget.addTab(self.ui_abortive, "Abortive Work")
        self.tabWidget.addTab(self.ui_payment, "Payment Application")
        self.tabWidget.addTab(self.ui_mc_vo, "Variation Order")
        self.tabWidget.addTab(self.ui_subcontract, "Subcontract")
        self.tabWidget.addTab(self.ui_sc_payment, "SC Payment")
        self.tabWidget.addTab(self.ui_sc_vo, "SC VO")
        self.tabWidget.addTab(self.ui_sc_contra, "SC Contra Charge")
        self.tabWidget.addTab(self.ui_budget, "Budget")
        self.tabWidget.addTab(self.ui_bq, "Bill of Quantities")

        # Hide native tab bar; navigation will be via left tree
        try:
            try:
                self.tabWidget.tabBar().hide()
            except Exception:
                pass
            # Populate navigation tree
            try:
                # navTree is declared in Main.ui and loaded by uic
                from PyQt5.QtWidgets import QTreeWidgetItem
                groups = [
                    ("Site Record", ["Document", "Abortive Work"]),
                    ("Main Contract", ["Bill of Quantities", "Payment Application", "Variation Order"]),
                    ("Sub-Contract", ["Subcontract", "SC Payment", "SC VO", "SC Contra Charge"]),
                    ("Summary", ["Budget"])
                ]
                self.navTree.clear()
                # Keep a mapping name->tab index for quick lookup
                self._nav_map = {}
                for g, children in groups:
                    gitem = QTreeWidgetItem([g])
                    gitem.setData(0, 1, g)
                    self.navTree.addTopLevelItem(gitem)
                    for child in children:
                        citem = QTreeWidgetItem([child])
                        citem.setData(0, 1, child)
                        gitem.addChild(citem)
                        # find mapping from tab text to index
                        for i in range(self.tabWidget.count()):
                            try:
                                if self.tabWidget.tabText(i) == child:
                                    self._nav_map[child] = i
                                    break
                            except Exception:
                                continue
                # Expand top-level
                for i in range(self.navTree.topLevelItemCount()):
                    self.navTree.topLevelItem(i).setExpanded(True)

                # Connect click
                def on_nav_clicked(item, column):
                    try:
                        name = item.data(0, 1)
                        if not name:
                            return
                        # If this is top-level group, expand/collapse
                        if item.parent() is None:
                            item.setExpanded(not item.isExpanded())
                            return
                        # Find mapping
                        idx = self._nav_map.get(name)
                        if idx is not None:
                            self.tabWidget.setCurrentIndex(idx)
                    except Exception:
                        pass

                self.navTree.itemClicked.connect(on_nav_clicked)
            except Exception:
                pass
        except Exception:
            pass

        # Add refresh action to menu bar
        self.setup_menu_bar()

    def setup_menu_bar(self):
        """Setup menu bar with refresh functionality"""
        # Get or create View menu
        view_menu = self.menuBar().addMenu("Tool")
        
        # Create refresh action
        refresh_action = view_menu.addAction("Refresh Data")
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh all data from database")
        refresh_action.triggered.connect(self.refresh_all_data)
        
        # Create new database action
        create_db_action = view_menu.addAction("Create New Database")
        create_db_action.setStatusTip("Create a new database from schema file")
        create_db_action.triggered.connect(self.create_new_database)

    def refresh_all_data(self):
        """Refresh all data across all tabs"""
        try:
            # Refresh each tab's data
            if hasattr(self.ui_doc, 'refresh_list'):
                self.ui_doc.refresh_list()
            
            if hasattr(self.ui_abortive, 'refresh_list'):
                self.ui_abortive.refresh_list()
            
            if hasattr(self.ui_payment, 'refresh_ips'):
                self.ui_payment.refresh_ips()
            
            if hasattr(self.ui_subcontract, 'refresh_list'):
                self.ui_subcontract.refresh_list()
            
            if hasattr(self.ui_budget, 'refresh_list'):
                self.ui_budget.refresh_list()
            
            if hasattr(self.ui_bq, 'refresh_table'):
                self.ui_bq.refresh_table()
            
            if hasattr(self.ui_mc_vo, 'refresh_list'):
                self.ui_mc_vo.refresh_list()
            
            if hasattr(self.ui_sc_vo, 'refresh_list'):
                self.ui_sc_vo.refresh_list()
            if hasattr(self, 'ui_sc_contra') and hasattr(self.ui_sc_contra, 'refresh_list'):
                self.ui_sc_contra.refresh_list()
            
            if hasattr(self.ui_sc_payment, 'load_subcontracts'):
                self.ui_sc_payment.load_subcontracts()
            
            # Show status message
            self.statusBar().showMessage("All data refreshed from database", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing data: {str(e)}")

    def create_new_database(self):
        """Create a new database from the schema file"""
        reply = QMessageBox.question(
            self, 
            "Create New Database",
            "This will create a new database from the schema file. All existing data will be lost. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Close current connection
                if hasattr(self, 'db_manager'):
                    self.db_manager.close()
                
                # Delete existing database file
                db_path = os.path.join(ROOT_PATH, "database", "QS_Project.db")
                if os.path.exists(db_path):
                    os.remove(db_path)
                
                # Create new database manager and schema
                self.db_manager = DB_Manager(db_path)
                schema_path = os.path.join(ROOT_PATH, "database", "Project_db_Schema.txt")
                self.db_manager.create_tables_from_schema(schema_path)
                
                # Refresh all data after creating new database
                self.refresh_all_data()
                QMessageBox.information(self, "Success", "New database created successfully from schema.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create database: {str(e)}")

    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
