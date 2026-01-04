from .DB_manager import DB_Manager

class Doc_Manager:
    def __init__(self, db_manager: DB_Manager):
        self.db = db_manager

    def add_document(self, file_ref, date, doc_type, title, from_party, to_party, cost_imp, time_imp, remark):
        data = {
            "File": file_ref,
            "Date": date,
            "Type": doc_type,
            "Title": title,
            "From": from_party,
            "To": to_party,
            "Cost Implication": cost_imp,
            "Time Implication": time_imp,
            "Remark": remark
        }
        return self.db.insert("Document Manager", data)

    def get_document(self, file_ref):
        return self.db.fetch_one("SELECT * FROM \"Document Manager\" WHERE File = ?", (file_ref,))

    def get_all_documents(self):
        return self.db.fetch_all("SELECT * FROM \"Document Manager\"")

    def update_document(self, file_ref, data):
        self.db.update("Document Manager", data, "File = ?", (file_ref,))

    def delete_document(self, file_ref):
        self.db.delete("Document Manager", "File = ?", (file_ref,))

    def get_next_file_ref(self):
        result = self.db.fetch_one("SELECT \"File\" FROM \"Document Manager\" ORDER BY rowid DESC LIMIT 1")
        if result:
            last_file = result['File']
            num = int(last_file[3:]) + 1
        else:
            num = 1
        return f"DOC{num:03d}"

    # Intermediate table operations
    def link_abortive_work(self, abortive_ref, doc_ref, remark=""):
        data = {"Abortive Ref": abortive_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("Abortive Work_Document", data)

    def get_abortive_links(self, doc_ref):
        query = """
        SELECT awd."Abortive Ref", awr."Description", awd."Remark"
        FROM "Abortive Work_Document" awd
        JOIN "Abortive Work Record" awr ON awd."Abortive Ref" = awr."Abortive Ref"
        WHERE awd."Doc Ref" = ?
        """
        return self.db.fetch_all(query, (doc_ref,))

    def delete_abortive_link(self, abortive_ref, doc_ref):
        self.db.delete("Abortive Work_Document", "\"Abortive Ref\" = ? AND \"Doc Ref\" = ?", (abortive_ref, doc_ref))

    def link_vo(self, vo_ref, doc_ref, remark=""):
        data = {"VO Ref": vo_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("VO Document", data)

    def get_vo_links(self, doc_ref):
        query = """
        SELECT vod."VO Ref", mcv."Description", vod."Remark"
        FROM "VO Document" vod
        JOIN "Main Contract VO" mcv ON vod."VO Ref" = mcv."VO ref"
        WHERE vod."Doc Ref" = ?
        """
        return self.db.fetch_all(query, (doc_ref,))

    def delete_vo_link(self, vo_ref, doc_ref):
        self.db.delete("VO Document", "\"VO Ref\" = ? AND \"Doc Ref\" = ?", (vo_ref, doc_ref))
    
    def link_sc_vo(self, vo_ref, doc_ref, remark=""):
        data = {"VO Ref": vo_ref, "Doc Ref": doc_ref, "Remark": remark}
        return self.db.insert("SC VO Document", data)

    def get_sc_vo_links(self, doc_ref):
        query = """
        SELECT scvod."VO Ref", scv."Description", scvod."Remark"
        FROM "SC VO Document" scvod
        JOIN "Sub Contract VO" scv ON scvod."VO Ref" = scv."VO ref"
        WHERE scvod."Doc Ref" = ?
        """
        return self.db.fetch_all(query, (doc_ref,))

    def delete_sc_vo_link(self, vo_ref, doc_ref):
        self.db.delete("SC VO Document", "\"VO Ref\" = ? AND \"Doc Ref\" = ?", (vo_ref, doc_ref))

    def link_document_hierarchy(self, parent_doc, child_doc):
        data = {"Parent Doc": parent_doc, "Child Document": child_doc}
        return self.db.insert("Document Cover", data)

    def get_child_documents(self, parent_doc):
        return self.db.fetch_all("SELECT * FROM \"Document Cover\" WHERE \"Parent Doc\" = ?", (parent_doc,))

    def get_parent_documents(self, child_doc):
        return self.db.fetch_all("SELECT * FROM \"Document Cover\" WHERE \"Child Document\" = ?", (child_doc,))

    def delete_document_link(self, parent_doc, child_doc):
        self.db.delete("Document Cover", "\"Parent Doc\" = ? AND \"Child Document\" = ?", (parent_doc, child_doc))

    def get_doc_types(self):
        return self.db.fetch_all("SELECT * FROM \"Document Type\"")

    def add_doc_type(self, type_name, desc):
        data = {"Type": type_name, "Description": desc}
        return self.db.insert("Document Type", data)

    def delete_doc_type(self, type_name):
        self.db.delete("Document Type", "Type = ?", (type_name,))

    def is_type_used(self, type_name):
        result = self.db.fetch_one("SELECT COUNT(*) as count FROM \"Document Manager\" WHERE Type = ?", (type_name,))
        return result['count'] > 0

    def update_documents_type(self, old_type, new_type):
        self.db.update("Document Manager", {"Type": new_type}, "Type = ?", (old_type,))

    def get_all_abortive_works(self):
        return self.db.fetch_all("SELECT \"Abortive Ref\" FROM \"Abortive Work Record\"")

    def get_all_vos(self):
        return self.db.fetch_all("SELECT \"VO ref\" FROM \"Main Contract VO\"")

    def get_all_sc_vos(self):
        return self.db.fetch_all("SELECT \"VO ref\" FROM \"Sub Contract VO\"")
