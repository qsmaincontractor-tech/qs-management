from .DB_manager import DB_Manager

class Payment_Application_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    # Main Contract IP Application (Header)
    def create_payment_application(self, ip_no, draft_date=None, issue_date=None, approved_date=None, payment_date=None, remark=""):
        data = {
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
        return self.db.insert("Main Contract IP Application", data)

    def get_payment_application(self, ip_no):
        return self.db.fetch_one("SELECT * FROM \"Main Contract IP Application\" WHERE IP = ?", (ip_no,))

    def get_all_payment_applications(self):
        return self.db.fetch_all("SELECT * FROM \"Main Contract IP Application\" ORDER BY IP ASC")

    def update_payment_application(self, ip_no, data):
        self.db.update("Main Contract IP Application", data, "IP = ?", (ip_no,))

    def delete_payment_application(self, ip_no):
        # Items should be deleted by CASCADE, but let's be safe
        self.db.delete("Main Contract IP Item", "IP = ?", (ip_no,))
        self.db.delete("Main Contract IP Application", "IP = ?", (ip_no,))

    def get_next_ip_no(self):
        result = self.db.fetch_one("SELECT IP FROM \"Main Contract IP Application\" ORDER BY IP DESC LIMIT 1")
        if result:
            last_ip = result['IP']
            return last_ip + 1
        else:
            return 1

    # Main Contract IP Item (Details)
    def add_ip_item(self, ip_no, item_no, item_type, bq_ref, vo_ref, doc_ref, description, applied_amt, certified_amt, paid_amt, remark):
        data = {
            "IP": ip_no,
            "Item": item_no,
            "Type": item_type,
            "BQ Ref": bq_ref,
            "VO Ref": vo_ref,
            "DOC Ref": doc_ref,
            "Description": description,
            "Applied Amount": applied_amt,
            "Certified Amount": certified_amt,
            "Paid Amount": paid_amt,
            "Remark": remark
        }
        return self.db.insert("Main Contract IP Item", data)

    def get_ip_items(self, ip_no):
        return self.db.fetch_all("SELECT * FROM \"Main Contract IP Item\" WHERE IP = ? ORDER BY Item ASC", (ip_no,))

    def update_ip_item(self, ip_no, item_no, data):
        self.db.update("Main Contract IP Item", data, "IP = ? AND Item = ?", (ip_no, item_no))

    def delete_ip_item(self, ip_no, item_no):
        self.db.delete("Main Contract IP Item", "IP = ? AND Item = ?", (ip_no, item_no))

    def get_next_item_no(self, ip_no):
        result = self.db.fetch_one("SELECT Item FROM \"Main Contract IP Item\" WHERE IP = ? ORDER BY Item DESC LIMIT 1", (ip_no,))
        if result:
            return result['Item'] + 1
        else:
            return 1

    def copy_previous_ip_items(self, current_ip):
        if current_ip <= 1:
            return False
        
        prev_ip = current_ip - 1
        prev_items = self.get_ip_items(prev_ip)
        
        if not prev_items:
            return False
            
        for item in prev_items:
            self.add_ip_item(
                current_ip,
                item['Item'],
                item['Type'],
                item['BQ Ref'],
                item['VO Ref'],
                item['DOC Ref'],
                item['Description'],
                item['Applied Amount'], 
                item['Certified Amount'], 
                item['Paid Amount'], 
                item['Remark']
            )
        return True

    def calculate_ip_totals(self, ip_no):
        items = self.get_ip_items(ip_no)
        total_applied = sum(item['Applied Amount'] for item in items if item['Applied Amount'])
        total_certified = sum(item['Certified Amount'] for item in items if item['Certified Amount'])
        total_paid = sum(item['Paid Amount'] for item in items if item['Paid Amount'])
        
        # Get previous IP totals for "Previous Applied Amount"
        prev_applied = 0.0
        if ip_no > 1:
            prev_app = self.get_payment_application(ip_no - 1)
            if prev_app:
                prev_applied = prev_app['Accumulated Applied Amount']
        
        # Update Header
        data = {
            "Accumulated Applied Amount": total_applied,
            "Previous Applied Amount": prev_applied,
            "This Applied Amount": total_applied - prev_applied,
            "Certified Amount": total_certified,
            "Paid Amount": total_paid
        }
        self.update_payment_application(ip_no, data)

    # Main Contract BQ (Unchanged)
    def add_bq_item(self, bq_id, bill, section, page, item, description, qty, unit, rate, trade, remark, discount=0):
        data = {
            "BQ ID": bq_id,
            "Bill": bill,
            "Section": section,
            "Page": page,
            "Item": item,
            "description": description,
            "Qty": qty,
            "Unit": unit,
            "Rate": rate,
            "Discount": discount,
            "Trade": trade,
            "Remark": remark
        }
        return self.db.insert("Main Contract BQ", data)

    def get_all_bq_items(self):
        return self.db.fetch_all("SELECT * FROM \"Main Contract BQ\"")

    # Main Contract VO (Unchanged)
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
        return self.db.fetch_one("SELECT * FROM \"Main Contract VO\" WHERE \"VO ref\" = ?", (vo_ref,))

    def get_all_vos(self):
        return self.db.fetch_all("SELECT * FROM \"Main Contract VO\"")

    def update_vo(self, vo_ref, data):
        self.db.update("Main Contract VO", data, "\"VO ref\" = ?", (vo_ref,))

    def delete_vo(self, vo_ref):
        self.db.delete("Main Contract VO", "\"VO ref\" = ?", (vo_ref,))

    def get_next_vo_ref(self):
        result = self.db.fetch_one("SELECT \"VO ref\" FROM \"Main Contract VO\" ORDER BY rowid DESC LIMIT 1")
        if result:
            last_ref = result['VO ref']
            try:
                num = int(last_ref[2:]) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        return f"VO{num:03d}"

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
        return self.db.fetch_all("SELECT * FROM \"VO Item\" WHERE \"VO ref\" = ?", (vo_ref,))

    def update_vo_item(self, id, data):
        self.db.update("VO Item", data, "ID = ?", (id,))

    def delete_vo_item(self, id):
        self.db.delete("VO Item", "ID = ?", (id,))

    def get_existing_bq_refs(self):
        """Get all existing BQ IDs with descriptions for dropdown"""
        results = self.db.fetch_all("SELECT \"BQ ID\", description FROM \"Main Contract BQ\" WHERE \"BQ ID\" IS NOT NULL AND \"BQ ID\" != '' ORDER BY \"BQ ID\"")
        refs = []
        for row in results:
            bq_id = row['BQ ID']
            desc = row.get('description', '').strip()
            if desc:
                display = f"{bq_id} - {desc}"
            else:
                display = bq_id
            refs.append(display)
        return list(set(refs))  # Remove duplicates

    def get_existing_vo_refs(self):
        """Get all existing VO refs with descriptions for dropdown"""
        results = self.db.fetch_all("SELECT \"VO ref\", \"Description\" FROM \"Main Contract VO\" WHERE \"VO ref\" IS NOT NULL AND \"VO ref\" != '' ORDER BY \"VO ref\"")
        refs = []
        for row in results:
            vo_ref = row['VO ref']
            desc = row.get('Description', '').strip()
            if desc:
                display = f"{vo_ref} - {desc}"
            else:
                display = vo_ref
            refs.append(display)
        return list(set(refs))  # Remove duplicates

    def get_existing_doc_refs(self):
        """Get all existing DOC refs with titles for dropdown"""
        results = self.db.fetch_all("SELECT \"File\", \"Title\" FROM \"Document Manager\" WHERE \"File\" IS NOT NULL AND \"File\" != '' ORDER BY \"File\"")
        refs = []
        for row in results:
            doc_ref = row['File']
            title = row.get('Title', '').strip()
            if title:
                display = f"{doc_ref} - {title}"
            else:
                display = doc_ref
            refs.append(display)
        return list(set(refs))  # Remove duplicates

    def get_bq_amount(self, bq_id):
        """Return the BQ item amount (stored 'Amount' column) for a given BQ ID. Returns 0.0 if not found."""
        if not bq_id:
            return 0.0
        # bq_id may be display like 'BQ001 - desc' so extract before ' - '
        bq_key = bq_id.split(' - ')[0] if ' - ' in bq_id else bq_id
        row = self.db.fetch_one('SELECT "Amount" as amount FROM "Main Contract BQ" WHERE "BQ ID" = ?', (bq_key,))
        if row and row.get('amount') is not None:
            return row['amount']
        # Fallback: try compute from Qty, Rate, Discount
        row2 = self.db.fetch_one('SELECT Qty, Rate, "Discount" FROM "Main Contract BQ" WHERE "BQ ID" = ?', (bq_key,))
        if row2:
            try:
                qty = float(row2.get('Qty') or 0)
                rate = float(row2.get('Rate') or 0)
                discount = float(row2.get('Discount') or 0)
                return qty * rate * (1 - discount)
            except Exception:
                return 0.0
        return 0.0

    def get_vo_application_amount(self, vo_ref):
        """Return the VO header Application Amount for a given VO ref. Returns 0.0 if not found."""
        if not vo_ref:
            return 0.0
        vo_key = vo_ref.split(' - ')[0] if ' - ' in vo_ref else vo_ref
        row = self.db.fetch_one('SELECT "Application Amount" as app FROM "Main Contract VO" WHERE "VO ref" = ?', (vo_key,))
        if row and row.get('app') is not None:
            return row['app']
        return 0.0
