import sys
sys.path.append(r'c:\Users\mokts\OneDrive - The Hong Kong Polytechnic University\Desktop\Programme\04 QS Management')
from function.Subcontract_manager import Subcontract_Manager
from function.Subcontract_Payment_manager import Subcontract_Payment_Manager
from function.DB_manager import DB_Manager

db = DB_Manager(r'c:\Users\mokts\OneDrive - The Hong Kong Polytechnic University\Desktop\Programme\04 QS Management\database\QS_Project.db')
scm = Subcontract_Manager(db)
spm = Subcontract_Payment_Manager(db)

subs = scm.get_all_subcontracts()
print('Total subcontracts:', len(subs))
for s in subs:
    sc_no = s['Sub Contract No']
    apps = spm.get_all_payment_applications(sc_no)
    print(sc_no, 'IPs:', len(apps))
    for app in apps:
        print('  IP', app['IP'], 'Draft:', app['Draft Date'])
        items = spm.get_ip_items(sc_no, app['IP'])
        print('   items:', len(items))

