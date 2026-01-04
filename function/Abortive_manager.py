from .DB_manager import DB_Manager

class Abortive_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    def add_abortive_work(self, abortive_ref, date, issue_date, coordinator, cost_imp, time_imp, inspection_date, endorsement, description):
        data = {
            "Abortive Ref": abortive_ref,
            "Date": date,
            "Issue Date": issue_date,
            "Project Coordinator": coordinator,
            "Cost Implication": cost_imp,
            "Time Implication": time_imp,
            "Inspection Date": inspection_date,
            "Endorsement": endorsement,
            "Description": description
        }
        return self.db.insert("Abortive Work Record", data)

    def get_abortive_work(self, abortive_ref):
        return self.db.fetch_one("SELECT * FROM \"Abortive Work Record\" WHERE \"Abortive Ref\" = ?", (abortive_ref,))

    def get_all_abortive_works(self):
        return self.db.fetch_all("SELECT * FROM \"Abortive Work Record\"")

    def update_abortive_work(self, abortive_ref, data):
        self.db.update("Abortive Work Record", data, "\"Abortive Ref\" = ?", (abortive_ref,))

    def delete_abortive_work(self, abortive_ref):
        self.db.delete("Abortive Work Record", "\"Abortive Ref\" = ?", (abortive_ref,))

    def get_next_abortive_ref(self):
        result = self.db.fetch_one("SELECT \"Abortive Ref\" FROM \"Abortive Work Record\" ORDER BY rowid DESC LIMIT 1")
        if result:
            last_ref = result['Abortive Ref']
            num = int(last_ref[2:]) + 1
        else:
            num = 1
        return f"AW{num:03d}"

    def link_to_vo(self, vo_ref, abortive_ref, remark=""):
        data = {"VO ref": vo_ref, "Abortive Work ref": abortive_ref, "Remark": remark}
        return self.db.insert("VO Abortive Record", data)

    def get_vo_links(self, abortive_ref):
        query = """
        SELECT voar."VO ref", mcv."Description", voar."Remark"
        FROM "VO Abortive Record" voar
        JOIN "Main Contract VO" mcv ON voar."VO ref" = mcv."VO ref"
        WHERE voar."Abortive Work ref" = ?
        """
        return self.db.fetch_all(query, (abortive_ref,))

    def add_vo_link(self, vo_ref, abortive_ref, remark=""):
        return self.link_to_vo(vo_ref, abortive_ref, remark)

    def delete_vo_link(self, vo_ref, abortive_ref):
        self.db.delete("VO Abortive Record", "\"VO ref\" = ? AND \"Abortive Work ref\" = ?", (vo_ref, abortive_ref))

    def get_document_links(self, abortive_ref):
        query = """
        SELECT awd."Doc Ref", dm."Title", awd."Remark"
        FROM "Abortive Work_Document" awd
        JOIN "Document Manager" dm ON awd."Doc Ref" = dm."File"
        WHERE awd."Abortive Ref" = ?
        """
        return self.db.fetch_all(query, (abortive_ref,))

    def add_document_link(self, abortive_ref, doc_ref, remark=""):
        data = {"Abortive Ref": abortive_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("Abortive Work_Document", data)

    def delete_document_link(self, abortive_ref, doc_ref):
        self.db.delete("Abortive Work_Document", "\"Abortive Ref\" = ? AND \"Doc Ref\" = ?", (abortive_ref, doc_ref))
