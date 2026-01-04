class Contra_Charge_Manager:
    def __init__(self, db):
        self.db = db

    def get_all_contra_charges(self):
        return self.db.fetch_all('SELECT * FROM "Contra Charge" ORDER BY "CC No"')

    def get_contra_charge(self, cc_no):
        return self.db.fetch_one('SELECT * FROM "Contra Charge" WHERE "CC No" = ?', (cc_no,))

    def create_contra_charge(self, cc_no, date, title, reason, agree_amount, deduct_to):
        data = {
            'CC No': cc_no,
            'Date': date,
            'Title': title,
            'Reason': reason,
            'Agree Amount': agree_amount,
            'Deduct To': deduct_to
        }
        return self.db.insert('Contra Charge', data)

    def update_contra_charge(self, cc_no, data):
        return self.db.update('Contra Charge', data, '"CC No" = ?', (cc_no,))

    def delete_contra_charge(self, cc_no):
        return self.db.delete('Contra Charge', '"CC No" = ?', (cc_no,))

    def get_items(self, cc_no):
        return self.db.fetch_all('SELECT * FROM "Contra Charge Item" WHERE "CC No" = ? ORDER BY "Item ID"', (cc_no,))

    def add_item(self, cc_no, description, qty, unit, rate, give_to, admin_rate=0.15):
        data = {
            'CC No': cc_no,
            'Description': description,
            'Qty': qty,
            'Unit': unit,
            'Rate': rate,
            'Admin Rate': admin_rate,
            'Give to': give_to
        }
        return self.db.insert('"Contra Charge Item"', data) if 'Contra Charge Item' in [] else self.db.insert('Contra Charge Item', data)

    def update_item(self, item_id, data):
        return self.db.update('"Contra Charge Item"' if False else 'Contra Charge Item', data, '"Item ID" = ?', (item_id,))

    def delete_item(self, item_id):
        return self.db.delete('Contra Charge Item', '"Item ID" = ?', (item_id,))

    def link_document(self, cc_no, doc_ref, remark=""):
        data = {'CC No': cc_no, 'Doc Ref': doc_ref, 'Remark': remark}
        return self.db.insert('"Contra Charge Document"' if False else 'Contra Charge Document', data)

    def get_document_links(self, cc_no):
        return self.db.fetch_all('SELECT ccd."Doc Ref" as "Doc Ref", dm.Title as Title, ccd.Remark as Remark FROM "Contra Charge Document" ccd LEFT JOIN "Document Manager" dm ON ccd."Doc Ref" = dm.File WHERE ccd."CC No" = ?', (cc_no,))

    def delete_document_link(self, cc_no, doc_ref):
        return self.db.delete('Contra Charge Document', '"CC No" = ? AND "Doc Ref" = ?', (cc_no, doc_ref))
