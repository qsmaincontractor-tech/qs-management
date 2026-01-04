from .DB_manager import DB_Manager

class MC_VO_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    # Main Contract VO operations
    def create_vo(self, vo_ref, date, issue_date, description, app_amt, agree_amt, receive_assessment, dispute, agree, reject, remark):
        data = {
            "VO ref": vo_ref,
            "Date": date,
            "Issue Date": issue_date,
            "Description": description,
            "Application Amount": app_amt,
            "Agree Amount": agree_amt,
            "Receive Assessment": receive_assessment,
            "Dispute": dispute,
            "Agree": agree,
            "Reject": reject,
            "Remark": remark
        }
        return self.db.insert("Main Contract VO", data)

    def get_vo(self, vo_ref):
        return self.db.fetch_one('''SELECT * FROM "Main Contract VO" WHERE "VO ref" = ?''', (vo_ref,))

    def get_all_vos(self):
        return self.db.fetch_all('''SELECT * FROM "Main Contract VO"''')

    def update_vo(self, vo_ref, data):
        self.db.update("Main Contract VO", data, '''"VO ref" = ?''', (vo_ref,))

    def delete_vo(self, vo_ref):
        self.db.delete("Main Contract VO", '''"VO ref" = ?''', (vo_ref,))

    def get_next_vo_ref(self):
        result = self.db.fetch_one('''SELECT "VO ref" FROM "Main Contract VO" ORDER BY rowid DESC LIMIT 1''')
        if result:
            last_ref = result['VO ref']
            num = int(last_ref[2:]) + 1
        else:
            num = 1
        return f"VO{num:03d}"

    # VO Item operations
    def add_vo_item(self, vo_ref, item, description, qty, unit, rate, trade, remark, star_rate, bq_ref, agree, discount=0):
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
        return self.db.insert("VO Item", data)

    def get_vo_items(self, vo_ref):
        return self.db.fetch_all('''SELECT * FROM "VO Item" WHERE "VO ref" = ?''', (vo_ref,))

    def update_vo_item(self, id, data):
        self.db.update("VO Item", data, "ID = ?", (id,))

    def delete_vo_item(self, id):
        self.db.delete("VO Item", "ID = ?", (id,))

    # Link operations
    def link_to_document(self, vo_ref, doc_ref, remark=""):
        data = {"VO Ref": vo_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("VO Document", data)

    def get_document_links(self, vo_ref):
        query = '''
        SELECT vd."Doc Ref", dm."Title", vd."Remark"
        FROM "VO Document" vd
        JOIN "Document Manager" dm ON vd."Doc Ref" = dm.File
        WHERE vd."VO Ref" = ?
        '''
        return self.db.fetch_all(query, (vo_ref,))

    def delete_document_link(self, vo_ref, doc_ref):
        self.db.delete("VO Document", '''"VO Ref" = ? AND "Doc Ref" = ?''', (vo_ref, doc_ref))

    def link_to_abortive(self, vo_ref, abortive_ref, remark=""):
        data = {"VO ref": vo_ref, "Abortive Work ref": abortive_ref, "Remark": remark}
        return self.db.insert("VO Abortive Record", data)

    def get_abortive_links(self, vo_ref):
        query = '''
        SELECT var."Abortive Work ref", awr."Description", var."Remark"
        FROM "VO Abortive Record" var
        JOIN "Abortive Work Record" awr ON var."Abortive Work ref" = awr."Abortive Ref"
        WHERE var."VO ref" = ?
        '''
        return self.db.fetch_all(query, (vo_ref,))

    def delete_abortive_link(self, vo_ref, abortive_ref):
        self.db.delete("VO Abortive Record", '''"VO ref" = ? AND "Abortive Work ref" = ?''', (vo_ref, abortive_ref))

    def get_vo_payment_totals(self, vo_ref):
        """Return totals (applied, certified, paid) for a VO across all IP items."""
        query = '''
        SELECT
            COALESCE(SUM("Applied Amount"), 0.0) AS applied_total,
            COALESCE(SUM("Certified Amount"), 0.0) AS certified_total,
            COALESCE(SUM("Paid Amount"), 0.0) AS paid_total
        FROM "Main Contract IP Item"
        WHERE "VO Ref" = ?
        '''
        result = self.db.fetch_one(query, (vo_ref,))
        if not result:
            return {"Applied": 0.0, "Certified": 0.0, "Paid": 0.0}
        return {
            "Applied": result.get('applied_total', 0.0) or 0.0,
            "Certified": result.get('certified_total', 0.0) or 0.0,
            "Paid": result.get('paid_total', 0.0) or 0.0
        }