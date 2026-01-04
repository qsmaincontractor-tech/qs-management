from .DB_manager import DB_Manager

class SC_VO_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    # Sub Contract VO operations
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

    def get_sc_vo(self, vo_ref):
        return self.db.fetch_one('''SELECT * FROM "Sub Contract VO" WHERE "VO ref" = ?''', (vo_ref,))

    def get_all_sc_vos(self):
        return self.db.fetch_all('''SELECT * FROM "Sub Contract VO"''')

    def get_sc_vos_by_subcontract(self, sc_no):
        return self.db.fetch_all('''SELECT * FROM "Sub Contract VO" WHERE Subcontract = ?''', (sc_no,))

    def update_sc_vo(self, vo_ref, data):
        self.db.update("Sub Contract VO", data, '''"VO ref" = ?''', (vo_ref,))

    def delete_sc_vo(self, vo_ref):
        self.db.delete("Sub Contract VO", '''"VO ref" = ?''', (vo_ref,))

    def get_next_sc_vo_ref(self):
        result = self.db.fetch_one('''SELECT "VO ref" FROM "Sub Contract VO" ORDER BY rowid DESC LIMIT 1''')
        if result:
            last_ref = result['VO ref']
            num = int(last_ref[4:]) + 1  # Assuming format SCVO001
        else:
            num = 1
        return f"SCVO{num:03d}"

    # SC VO Item operations
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
        return self.db.fetch_all('''SELECT * FROM "SC VO Item" WHERE "VO ref" = ?''', (vo_ref,))

    def update_sc_vo_item(self, id, data):
        self.db.update("SC VO Item", data, "ID = ?", (id,))

    def delete_sc_vo_item(self, id):
        self.db.delete("SC VO Item", "ID = ?", (id,))

    # Link operations
    def link_to_document(self, vo_ref, doc_ref, remark=""):
        data = {"VO Ref": vo_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("SC VO Document", data)

    def get_document_links(self, vo_ref):
        query = '''
        SELECT svd."Doc Ref", dm."Title", svd."Remark"
        FROM "SC VO Document" svd
        JOIN "Document Manager" dm ON svd."Doc Ref" = dm.File
        WHERE svd."VO Ref" = ?
        '''
        return self.db.fetch_all(query, (vo_ref,))

    def delete_document_link(self, vo_ref, doc_ref):
        self.db.delete("SC VO Document", '''"VO Ref" = ? AND "Doc Ref" = ?''', (vo_ref, doc_ref))