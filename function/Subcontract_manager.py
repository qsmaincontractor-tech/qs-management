from .DB_manager import DB_Manager

class Subcontract_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    # Basic Information
    def add_subcontract(self, sc_no, sc_name, company_name, contract_type, contract_sum, final_acc_amt):
        data = {
            "Sub Contract No": sc_no,
            "Sub Contract Name": sc_name,
            "Company Name": company_name,
            "Contract Type": contract_type,
            "Contract Sum": contract_sum,
            "Final Account Amount": final_acc_amt
        }
        return self.db.insert("Sub Contract", data)

    def add_subcontract_person(self, sc_no, name, position, tel, fax, email):
        data = {
            "Sub Contract": sc_no,
            "Name": name,
            "Position": position,
            "Tel": tel,
            "Fax": fax,
            "Email": email
        }
        return self.db.insert("Sub Contract Person", data)

    def get_subcontract_persons(self, sc_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract Person\" WHERE \"Sub Contract\" = ?", (sc_no,))

    def update_subcontract_person(self, id, data):
        self.db.update("Sub Contract Person", data, "ID = ?", (id,))

    def delete_subcontract_person(self, id):
        self.db.delete("Sub Contract Person", "ID = ?", (id,))

    def get_all_subcontracts(self):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract\"")

    def get_subcontract(self, sc_no):
        return self.db.fetch_one("SELECT * FROM \"Sub Contract\" WHERE \"Sub Contract No\" = ?", (sc_no,))

    def update_subcontract(self, sc_no, data):
        """Update subcontract and return number of rows affected."""
        return self.db.update("Sub Contract", data, "\"Sub Contract No\" = ?", (sc_no,))

    def delete_subcontract(self, sc_no):
        self.db.delete("Sub Contract", "\"Sub Contract No\" = ?", (sc_no,))

    def get_next_sc_no(self):
        result = self.db.fetch_one("SELECT \"Sub Contract No\" FROM \"Sub Contract\" ORDER BY rowid DESC LIMIT 1")
        if result:
            last_no = result['Sub Contract No']
            num = int(last_no[2:]) + 1
        else:
            num = 1
        return f"SC{num:03d}"

    # Payment Application
    def create_sc_payment_application(self, ip_no, item_no, date, ip_type, work_ref, vo_ref, cc_ref, applied_amt, certified_amt, remark):
        data = {
            "IP": ip_no,
            "Item": item_no,
            "Date": date,
            "Type": ip_type,
            "Contract Work ref": work_ref,
            "VO ref": vo_ref,
            "Contra Charge ref": cc_ref,
            "Applied Amount": applied_amt,
            "Certified Amount": certified_amt,
            "Remark": remark
        }
        return self.db.insert("Sub Contract IP", data)

    def get_sc_payment_applications(self, ip_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract IP\" WHERE IP = ?", (ip_no,))

    def update_sc_payment_application(self, ip_no, item_no, data):
        self.db.update("Sub Contract IP", data, "IP = ? AND Item = ?", (ip_no, item_no))

    def delete_sc_payment_application(self, ip_no, item_no):
        self.db.delete("Sub Contract IP", "IP = ? AND Item = ?", (ip_no, item_no))

    def add_sc_work(self, sc_no, works, qty, unit, rate, discount, trade):
        data = {
            "Subcontract": sc_no,
            "Works": works,
            "Qty": qty,
            "Unit": unit,
            "Rate": rate,
            "Discount": discount,
            "Trade": trade
        }
        return self.db.insert("Sub Con Works", data)

    def get_sc_works(self, sc_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Con Works\" WHERE Subcontract = ?", (sc_no,))

    def update_sc_work(self, sc_no, works, data):
        self.db.update("Sub Con Works", data, "Subcontract = ? AND Works = ?", (sc_no, works))

    def delete_sc_work(self, sc_no, works):
        self.db.delete("Sub Con Works", "Subcontract = ? AND Works = ?", (sc_no, works))

    def create_sc_vo(self, vo_ref, sc_no, date, receive_date, description, app_amt, agree_amt, issue_assessment, dispute, agree, reject, remark):
        data = {
            "VO ref": vo_ref,
            "Subcontract": sc_no,
            "Date": date,
            "Receive Date": receive_date,
            "Description": description,
            "Application Amount": app_amt,
            "Agree Amount": agree_amt,
            "Issue Assessment": issue_assessment,
            "Dispute": dispute,
            "Agree": agree,
            "Reject": reject,
            "Remark": remark
        }
        return self.db.insert("Sub Contract VO", data)

    def get_sc_vos(self, sc_no):
        return self.db.fetch_all("SELECT * FROM \"Sub Contract VO\" WHERE Subcontract = ?", (sc_no,))

    def get_sc_vo(self, vo_ref):
        return self.db.fetch_one("SELECT * FROM \"Sub Contract VO\" WHERE \"VO ref\" = ?", (vo_ref,))

    def update_sc_vo(self, vo_ref, data):
        self.db.update("Sub Contract VO", data, "\"VO ref\" = ?", (vo_ref,))

    def delete_sc_vo(self, vo_ref):
        self.db.delete("Sub Contract VO", "\"VO ref\" = ?", (vo_ref,))

    # Contract Type management
    def get_contract_types(self):
        try:
            return self.db.fetch_all("SELECT * FROM \"Contract Type\"")
        except Exception:
            return []

    def add_contract_type(self, name):
        return self.db.insert("Contract Type", {"Contract Type": name})

    def delete_contract_type(self, name):
        return self.db.delete("Contract Type", "\"Contract Type\" = ?", (name,))

    def is_contract_type_used(self, name):
        result = self.db.fetch_one("SELECT COUNT(1) as cnt FROM \"Sub Contract\" WHERE \"Contract Type\" = ?", (name,))
        return (result and result.get('cnt', 0) > 0)

    def update_subcontracts_type(self, old_type, new_type):
        return self.db.update("Sub Contract", {"Contract Type": new_type}, "\"Contract Type\" = ?", (old_type,))

    def add_sc_vo_item(self, vo_ref, item, description, qty, unit, rate, trade, remark, star_rate, bq_ref, agree, discount=0):
        data = {
            "VO ref": vo_ref,
            "Item": item,
            "Description": description,
            "Qty": qty,
            "Unit": unit,
            "Rate": rate,
            "Discount": discount,
            "Trade": trade,
            "Remark": remark,
            "Star Rate": star_rate,
            "BQ ref": bq_ref,
            "Agree": agree
        }
        return self.db.insert("SC VO Item", data)

    def get_sc_vo_items(self, vo_ref):
        return self.db.fetch_all("SELECT * FROM \"SC VO Item\" WHERE \"VO ref\" = ?", (vo_ref,))

    def update_sc_vo_item(self, id, data):
        self.db.update("SC VO Item", data, "ID = ?", (id,))

    def delete_sc_vo_item(self, id):
        self.db.delete("SC VO Item", "ID = ?", (id,))

    # Subcontract Link Management
    def add_sc_person_link(self, sc_no, person_id, remark=""):
        data = {
            "Sub Contract": sc_no,
            "Person ID": person_id,
            "Remark": remark
        }
        return self.db.insert("SC Person Links", data)

    def add_sc_payment_link(self, sc_no, ip_no, remark=""):
        data = {
            "Sub Contract": sc_no,
            "IP": ip_no,
            "Remark": remark
        }
        return self.db.insert("SC Payment Links", data)

    def add_sc_works_link(self, sc_no, works_ref, remark=""):
        data = {
            "Sub Contract": sc_no,
            "Works Ref": works_ref,
            "Remark": remark
        }
        return self.db.insert("SC Works Links", data)

    def add_sc_vo_link(self, sc_no, vo_ref, remark=""):
        data = {
            "Sub Contract": sc_no,
            "VO ref": vo_ref,
            "Remark": remark
        }
        return self.db.insert("SC VO Links", data)

    def get_sc_person_links(self, sc_no):
        try:
            return self.db.fetch_all("SELECT * FROM \"SC Person Links\" WHERE \"Sub Contract\" = ?", (sc_no,))
        except Exception as e:
            # Table might not exist yet
            return []

    def get_sc_payment_links(self, sc_no):
        try:
            return self.db.fetch_all("SELECT * FROM \"SC Payment Links\" WHERE \"Sub Contract\" = ?", (sc_no,))
        except Exception as e:
            # Table might not exist yet
            return []

    def get_sc_works_links(self, sc_no):
        try:
            return self.db.fetch_all("SELECT * FROM \"SC Works Links\" WHERE \"Sub Contract\" = ?", (sc_no,))
        except Exception as e:
            # Table might not exist yet
            return []

    def get_sc_vo_links(self, sc_no):
        try:
            return self.db.fetch_all("SELECT * FROM \"SC VO Links\" WHERE \"Sub Contract\" = ?", (sc_no,))
        except Exception as e:
            # Table might not exist yet
            return []

    def delete_sc_person_link(self, sc_no, person_id):
        self.db.delete("SC Person Links", "\"Sub Contract\" = ? AND \"Person ID\" = ?", (sc_no, person_id))

    def delete_sc_payment_link(self, sc_no, ip_no):
        self.db.delete("SC Payment Links", "\"Sub Contract\" = ? AND IP = ?", (sc_no, ip_no))

    def delete_sc_works_link(self, sc_no, works_ref):
        self.db.delete("SC Works Links", "\"Sub Contract\" = ? AND \"Works Ref\" = ?", (sc_no, works_ref))

    def delete_sc_vo_link(self, sc_no, vo_ref):
        self.db.delete("SC VO Links", "\"Sub Contract\" = ? AND \"VO ref\" = ?", (sc_no, vo_ref))
