import sys
import os
sys.path.append(os.path.dirname(__file__))

from function.DB_manager import DB_Manager

def add_more_fake_data():
    root_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(root_path, "database", "QS_Project.db")
    db = DB_Manager(db_path)

    # Insert more Contract Types
    db.insert("Contract Type", {"Contract Type": "Cost Plus"})
    db.insert("Contract Type", {"Contract Type": "Target Cost"})

    # Insert more Document Types
    db.insert("Document Type", {"Type": "Email", "Description": "Electronic communication"})
    db.insert("Document Type", {"Type": "Minutes", "Description": "Meeting minutes"})
    db.insert("Document Type", {"Type": "Report", "Description": "Progress report"})

    # Insert more MC IP Types
    db.insert("MC IP Type", {"Type": "Rejected", "remark": "Not approved"})

    # Insert more SC IP Types
    db.insert("SC IP Type", {"Type": "Rejected", "remark": "Not approved"})

    # Insert more Units
    db.insert("Unit Table", {"Order": 5, "Unit": "m", "Description": "Meter"})
    db.insert("Unit Table", {"Order": 6, "Unit": "hr", "Description": "Hour"})
    db.insert("Unit Table", {"Order": 7, "Unit": "ls", "Description": "Lump Sum"})

    # Insert more Trade Budget
    db.insert("Trade Budget", {"Trade": "Plumbing", "Description": "Plumbing works", "Qty": 150.0, "Unit": 4, "Rate": 100.0, "Discount Factor": 0.04})
    db.insert("Trade Budget", {"Trade": "Painting", "Description": "Painting works", "Qty": 300.0, "Unit": 1, "Rate": 50.0, "Discount Factor": 0.02})

    # Insert more Sub Contracts
    db.insert("Sub Contract", {"Sub Contract No": "SC003", "Sub Contract Name": "Plumbing Installation", "Company Name": "Plumb Masters", "Contract Type": "Remeasurement", "Contract Sum": 25000.0, "Final Account Amount": 26000.0})
    db.insert("Sub Contract", {"Sub Contract No": "SC004", "Sub Contract Name": "Painting Services", "Company Name": "Paint Pros", "Contract Type": "Lump Sum", "Contract Sum": 15000.0, "Final Account Amount": 14800.0})

    # Insert more Sub Contract Persons
    db.insert("Sub Contract Person", {"Sub Contract": "SC003", "Name": "Bob Wilson", "Position": "Supervisor", "Tel": "11223344", "Fax": "44332211", "Email": "bob@plumb.com"})
    db.insert("Sub Contract Person", {"Sub Contract": "SC004", "Name": "Alice Brown", "Position": "Foreman", "Tel": "55667788", "Fax": "88776655", "Email": "alice@paint.com"})

    # Insert more Documents
    db.insert("Document Manager", {"File": "DOC003", "Date": "2023-03-01", "Type": "Email", "Title": "Schedule Update", "From": "QS", "To": "Contractor", "Cost Implication": False, "Time Implication": True, "Remark": "Revised timeline"})
    db.insert("Document Manager", {"File": "DOC004", "Date": "2023-04-01", "Type": "Minutes", "Title": "Progress Meeting", "From": "PM", "To": "Team", "Cost Implication": True, "Time Implication": False, "Remark": "Cost overrun discussion"})
    db.insert("Document Manager", {"File": "DOC005", "Date": "2023-05-01", "Type": "Report", "Title": "Monthly Progress", "From": "Site Manager", "To": "Client", "Cost Implication": False, "Time Implication": False, "Remark": "On schedule"})

    # Insert more Abortive Work Records
    db.insert("Abortive Work Record", {"Abortive Ref": "AW003", "Date": "2023-05-01", "Issue Date": "2023-05-10", "Project Coordinator": "Coordinator C", "Cost Implication": True, "Time Implication": False, "Inspection Date": True, "Endorsement": True, "Description": "Material defect"})
    db.insert("Abortive Work Record", {"Abortive Ref": "AW004", "Date": "2023-06-01", "Issue Date": "2023-06-15", "Project Coordinator": "Coordinator D", "Cost Implication": False, "Time Implication": True, "Inspection Date": False, "Endorsement": False, "Description": "Weather delay"})

    # Insert more Main Contract VO
    db.insert("Main Contract VO", {"VO ref": "VO003", "Date": "2023-07-01", "Issue Date": "2023-07-20", "Description": "Plumbing addition", "Application Amount": 8000.0, "Agree Amount": 7500.0, "Receive Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})
    db.insert("Main Contract VO", {"VO ref": "VO004", "Date": "2023-08-01", "Issue Date": "2023-08-25", "Description": "Painting extension", "Application Amount": 3000.0, "Agree Amount": 2900.0, "Receive Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})

    # Insert more Main Contract BQ
    db.insert("Main Contract BQ", {"BQ ID": "BQ003", "Bill": "Bill 3", "Section": "Sec 3", "Page": "Pg 3", "Item": "Item 3", "description": "Plumbing pipes", "Qty": 100.0, "Unit": "m", "Rate": 80.0, "Trade": "Plumbing", "Remark": "Standard pipes"})
    db.insert("Main Contract BQ", {"BQ ID": "BQ004", "Bill": "Bill 4", "Section": "Sec 4", "Page": "Pg 4", "Item": "Item 4", "description": "Wall painting", "Qty": 200.0, "Unit": "m2", "Rate": 40.0, "Trade": "Painting", "Remark": "Interior paint"})

    # Insert more VO Items
    db.insert("VO Item", {"VO ref": "VO003", "Item": "VO Item 3", "Description": "Extra plumbing", "Qty": "20", "Unit": "m", "Rate": 85.0, "Trade": "Plumbing", "Star Rate": False, "BQ ref": "BQ003", "Agree": True})
    db.insert("VO Item", {"VO ref": "VO004", "Item": "VO Item 4", "Description": "Additional painting", "Qty": "50", "Unit": "m2", "Rate": 45.0, "Trade": "Painting", "Star Rate": False, "BQ ref": "BQ004", "Agree": True})

    # Insert more Main Contract IP (Immediate Payments)
    db.insert("Main Contract IP", {"IP": 2, "Item": 1, "Date": "2023-08-01", "Type": "Approved", "BQ ref": "BQ003", "Vo ref": "VO003", "Applied Amount": 16000.0, "Certified Amount": 15500.0, "Remark": 0})
    db.insert("Main Contract IP", {"IP": 2, "Item": 2, "Date": "2023-08-01", "Type": "Pending", "BQ ref": "BQ004", "Vo ref": "VO004", "Applied Amount": 8000.0, "Certified Amount": 0.0, "Remark": 0})
    db.insert("Main Contract IP", {"IP": 3, "Item": 1, "Date": "2023-09-01", "Type": "Budgetive", "BQ ref": "BQ001", "Vo ref": "VO001", "Applied Amount": 25000.0, "Certified Amount": 0.0, "Remark": 0})

    # Insert more Sub Contract VO
    db.insert("Sub Contract VO", {"VO ref": "SCVO002", "Subcontract": "SC003", "Date": "2023-09-01", "Receive Date": "2023-09-10", "Description": "Extra plumbing for sub", "Application Amount": 4000.0, "Agree Amount": 3800.0, "Issue Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})
    db.insert("Sub Contract VO", {"VO ref": "SCVO003", "Subcontract": "SC004", "Date": "2023-10-01", "Receive Date": "2023-10-15", "Description": "Painting adjustment", "Application Amount": 2000.0, "Agree Amount": 1950.0, "Issue Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})

    # Insert more Sub Con Works
    db.insert("Sub Con Works", {"Subcontract": "SC003", "Works": "Pipe Installation", "Qty": 80.0, "Unit": "m", "Rate": 75.0, "Discount": 0.04, "Trade": "Plumbing"})
    db.insert("Sub Con Works", {"Subcontract": "SC004", "Works": "Interior Painting", "Qty": 150.0, "Unit": "m2", "Rate": 35.0, "Discount": 0.03, "Trade": "Painting"})

    # Insert more SC VO Item
    db.insert("SC VO Item", {"VO ref": "SCVO002", "Item": "SC VO Item 2", "Description": "Extra sub plumbing", "Qty": "15", "Unit": "m", "Rate": 78.0, "Trade": "Plumbing", "Star Rate": False, "BQ ref": "Pipe Installation", "Agree": True})
    db.insert("SC VO Item", {"VO ref": "SCVO003", "Item": "SC VO Item 3", "Description": "Additional sub painting", "Qty": "30", "Unit": "m2", "Rate": 38.0, "Trade": "Painting", "Star Rate": False, "BQ ref": "Interior Painting", "Agree": True})

    # Insert more Sub Contract IP
    db.insert("Sub Contract IP", {"IP": 2, "Item": 1, "Date": "2023-10-01", "Type": "Approved", "Contract Work ref": "Pipe Installation", "VO ref": "SCVO002", "Applied Amount": 6000.0, "Certified Amount": 5800.0, "Remark": 0})
    db.insert("Sub Contract IP", {"IP": 3, "Item": 1, "Date": "2023-11-01", "Type": "Pending", "Contract Work ref": "Interior Painting", "VO ref": "SCVO003", "Applied Amount": 5250.0, "Certified Amount": 0.0, "Remark": 0})

    # Insert more Contra Charge
    db.insert("Contra Charge", {"CC No": "CC002", "Date": "2023-11-01", "Title": "Quality Issue", "Reason": "Poor workmanship", "Agree Amount": 500.0, "Deduct To": "SC003"})
    db.insert("Contra Charge", {"CC No": "CC003", "Date": "2023-12-01", "Title": "Material Waste", "Reason": "Excess usage", "Agree Amount": 300.0, "Deduct To": "SC004"})

    # Insert more Contra Charge Item
    db.insert("Contra Charge Item", {"CC No": "CC002", "Description": "Deduction for quality", "Qty": 1.0, "Unit": "no", "Rate": 500.0, "Give to": "Pipe Installation"})
    db.insert("Contra Charge Item", {"CC No": "CC003", "Description": "Waste deduction", "Qty": 1.0, "Unit": "no", "Rate": 300.0, "Give to": "Interior Painting"})

    # Insert more Document Cover
    db.insert("Document Cover", {"Parent Doc": "DOC003", "Child Document": "DOC004"})
    db.insert("Document Cover", {"Parent Doc": "DOC004", "Child Document": "DOC005"})

    # Insert more VO Document
    db.insert("VO Document", {"VO Ref": "VO003", "Doc Ref": "DOC003", "Remark": "VO supporting doc"})
    db.insert("VO Document", {"VO Ref": "VO004", "Doc Ref": "DOC004", "Remark": "VO evidence"})

    # Insert more Abortive Work_Document
    db.insert("Abortive Work_Document", {"Abortive Ref": "AW003", "Doc Ref": "DOC005", "Remark": "Abortive evidence"})
    db.insert("Abortive Work_Document", {"Abortive Ref": "AW004", "Doc Ref": "DOC003", "Remark": "Related document"})

    # Insert more SC VO Document
    db.insert("SC VO Document", {"VO Ref": "SCVO002", "Doc Ref": "DOC004", "Remark": "Sub VO support"})
    db.insert("SC VO Document", {"VO Ref": "SCVO003", "Doc Ref": "DOC005", "Remark": "Sub VO document"})

    # Insert more VO Abortive Record
    db.insert("VO Abortive Record", {"VO ref": "VO003", "Abortive Work ref": "AW003", "Remark": "VO related abortive"})
    db.insert("VO Abortive Record", {"VO ref": "VO004", "Abortive Work ref": "AW004", "Remark": "VO abortive link"})

    print("Additional fake data populated successfully!")
    db.close()

if __name__ == "__main__":
    add_more_fake_data()