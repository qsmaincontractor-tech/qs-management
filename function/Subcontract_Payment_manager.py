from .DB_manager import DB_Manager

class Subcontract_Payment_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    # Sub Contract IP Application (Header)
    def create_payment_application(self, sub_contract_no, ip_no, draft_date=None, issue_date=None, approved_date=None, payment_date=None, remark=""):
        data = {
            "Sub Contract No": sub_contract_no,
            "IP": ip_no,
            "Draft Date": draft_date,
            "Issue Date": issue_date,
            "Approved Date": approved_date,
            "Payment Date": payment_date,
            "Accumulated Applied Amount": 0.0,
            "Previous Applied Amount": 0.0,
            "This Applied Amount": 0.0,
            "Certified Amount": 0.0,
            "Paid Amount": 0.0,
            "Remark": remark
        }
        return self.db.insert("Sub Contract IP Application", data)

    def get_payment_application(self, sub_contract_no, ip_no):
        return self.db.fetch_one("SELECT * FROM \"Sub Contract IP Application\" WHERE \"Sub Contract No\" = ? AND IP = ?", (sub_contract_no, ip_no))

    def get_all_payment_applications(self, sub_contract_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract IP Application\" WHERE \"Sub Contract No\" = ? ORDER BY IP ASC", (sub_contract_no,))

    def update_payment_application(self, sub_contract_no, ip_no, data):
        self.db.update("Sub Contract IP Application", data, "\"Sub Contract No\" = ? AND IP = ?", (sub_contract_no, ip_no))

    def delete_payment_application(self, sub_contract_no, ip_no):
        # Items should be deleted by CASCADE, but let's be safe
        self.db.delete("Sub Contract IP Item", "\"Sub Contract No\" = ? AND IP = ?", (sub_contract_no, ip_no))
        self.db.delete("Sub Contract IP Application", "\"Sub Contract No\" = ? AND IP = ?", (sub_contract_no, ip_no))

    def get_next_ip_no(self, sub_contract_no):
        result = self.db.fetch_one("SELECT IP FROM \"Sub Contract IP Application\" WHERE \"Sub Contract No\" = ? ORDER BY IP DESC LIMIT 1", (sub_contract_no,))
        if result:
            last_ip = result['IP']
            return last_ip + 1
        else:
            return 1

    # Sub Contract IP Item (Details)
    def add_ip_item(self, sub_contract_no, ip_no, item_no, item_type, contract_work_ref, vo_ref, contra_charge_ref, description, applied_amt, certified_amt, paid_amt, remark):
        data = {
            "Sub Contract No": sub_contract_no,
            "IP": ip_no,
            "Item": item_no,
            "Type": item_type,
            "Contract Work Ref": contract_work_ref,
            "VO Ref": vo_ref,
            "Contra Charge Ref": contra_charge_ref,
            "Description": description,
            "Applied Amount": applied_amt,
            "Certified Amount": certified_amt,
            "Paid Amount": paid_amt,
            "Remark": remark
        }
        return self.db.insert("Sub Contract IP Item", data)

    def get_ip_items(self, sub_contract_no, ip_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract IP Item\" WHERE \"Sub Contract No\" = ? AND IP = ? ORDER BY Item ASC", (sub_contract_no, ip_no))

    def update_ip_item(self, sub_contract_no, ip_no, item_no, data):
        self.db.update("Sub Contract IP Item", data, "\"Sub Contract No\" = ? AND IP = ? AND Item = ?", (sub_contract_no, ip_no, item_no))

    def delete_ip_item(self, sub_contract_no, ip_no, item_no):
        self.db.delete("Sub Contract IP Item", "\"Sub Contract No\" = ? AND IP = ? AND Item = ?", (sub_contract_no, ip_no, item_no))

    def get_next_item_no(self, sub_contract_no, ip_no):
        result = self.db.fetch_one("SELECT Item FROM \"Sub Contract IP Item\" WHERE \"Sub Contract No\" = ? AND IP = ? ORDER BY Item DESC LIMIT 1", (sub_contract_no, ip_no))
        if result:
            return result['Item'] + 1
        else:
            return 1

    def copy_previous_ip_items(self, sub_contract_no, current_ip):
        if current_ip <= 1:
            return False
        
        prev_ip = current_ip - 1
        prev_items = self.get_ip_items(sub_contract_no, prev_ip)
        
        if not prev_items:
            return False
            
        for item in prev_items:
            self.add_ip_item(
                sub_contract_no,
                current_ip,
                item['Item'],
                item['Type'],
                item['Contract Work Ref'],
                item['VO Ref'],
                item['Contra Charge Ref'],
                item['Description'],
                item['Applied Amount'], 
                item['Certified Amount'], 
                item['Paid Amount'], 
                item['Remark']
            )
        return True
