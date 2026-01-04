import sys
from PyQt5.QtWidgets import QApplication
sys.path.append(r'c:\Users\mokts\OneDrive - The Hong Kong Polytechnic University\Desktop\Programme\04 QS Management')
from function.DB_manager import DB_Manager
from function.Subcontract_manager import Subcontract_Manager
from function.Subcontract_Payment_manager import Subcontract_Payment_Manager
from ui.Ui_SubcontractManager import Ui_SubcontractManager
from ui.Ui_SubcontractPaymentManager import Ui_SubcontractPaymentManager

app = QApplication.instance() or QApplication([])
db = DB_Manager(r'c:\Users\mokts\OneDrive - The Hong Kong Polytechnic University\Desktop\Programme\04 QS Management\database\QS_Project.db')
sm = Subcontract_Manager(db)
spm = Subcontract_Payment_Manager(db)
ui_sc = Ui_SubcontractManager(sm)
ui_sc_payment = Ui_SubcontractPaymentManager(spm, sm)
ui_sc.set_sc_payment_ui(ui_sc_payment, None)

# Load subcontracts and pick first
ui_sc.refresh_list()
if ui_sc.recordList.count() == 0:
    print('No subcontracts found')
else:
    item = ui_sc.recordList.item(0)
    ui_sc.recordList.setCurrentItem(item)
    ui_sc.load_details(item)
    # Print payment table info
    rows = ui_sc.table_payment.rowCount()
    cols = ui_sc.table_payment.columnCount()
    headers = [ui_sc.table_payment.horizontalHeaderItem(i).text() if ui_sc.table_payment.horizontalHeaderItem(i) else '' for i in range(cols)]
    print('Payment table rows:', rows, 'cols:', cols)
    print('Headers:', headers)
    for r in range(rows):
        row_vals = [ui_sc.table_payment.item(r,c).text() if ui_sc.table_payment.item(r,c) else '' for c in range(cols)]
        print('Row', r, row_vals)

print('Done')
