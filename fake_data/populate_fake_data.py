import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from function.DB_manager import DB_Manager

def populate_fake_data():
    # Use correct paths relative to the project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(project_root, "database", "QS_Project.db")
    schema_path = os.path.join(project_root, "database", "Project_db_Schema.txt")
    
    db = DB_Manager(db_path)
    # Don't recreate schema since tables already exist
    # db.create_tables_from_schema(schema_path)

    # Insert Contract Types
    db.insert("Contract Type", {"Contract Type": "Remeasurement"})
    db.insert("Contract Type", {"Contract Type": "Lump Sum"})
    db.insert("Contract Type", {"Contract Type": "SoR"})

    # Insert Document Types
    db.insert("Document Type", {"Type": "Site Memo", "Description": "Site communication"})
    db.insert("Document Type", {"Type": "AI", "Description": "Architectural Instruction"})
    db.insert("Document Type", {"Type": "RFI", "Description": "Request for Information"})
    db.insert("Document Type", {"Type": "CVI", "Description": "Contract Variation Instruction"})
    db.insert("Document Type", {"Type": "Shop Drawing", "Description": "Technical drawings"})
    db.insert("Document Type", {"Type": "Claims", "Description": "Contract claims"})
    db.insert("Document Type", {"Type": "NOD", "Description": "Notice of Delay"})
    db.insert("Document Type", {"Type": "NOE", "Description": "Notice of Extension"})

    # Insert MC IP Types
    db.insert("MC IP Type", {"Type": "Budgetive", "remark": "Initial budget"})
    db.insert("MC IP Type", {"Type": "Pending", "remark": "Awaiting approval"})
    db.insert("MC IP Type", {"Type": "Approved", "remark": "Certified"})

    # Insert SC IP Types
    db.insert("SC IP Type", {"Type": "Budgetive", "remark": "Initial budget"})
    db.insert("SC IP Type", {"Type": "Pending", "remark": "Awaiting approval"})
    db.insert("SC IP Type", {"Type": "Approved", "remark": "Certified"})

    # Insert Units
    db.insert("Unit Table", {"Order": 1, "Unit": "m2", "Description": "Square Meter"})
    db.insert("Unit Table", {"Order": 2, "Unit": "m3", "Description": "Cubic Meter"})
    db.insert("Unit Table", {"Order": 3, "Unit": "kg", "Description": "Kilogram"})
    db.insert("Unit Table", {"Order": 4, "Unit": "no", "Description": "Number"})

    # Insert Trade Budget
    db.insert("Trade Budget", {"Trade": "Concrete", "Description": "Concrete works", "Qty": 100.0, "Unit": 1, "Rate": 500.0, "Discount Factor": 0.05})
    db.insert("Trade Budget", {"Trade": "Steel", "Description": "Steel reinforcement", "Qty": 50.0, "Unit": 3, "Rate": 2000.0, "Discount Factor": 0.03})
    db.insert("Trade Budget", {"Trade": "Electrical", "Description": "Electrical installation", "Qty": 200.0, "Unit": 4, "Rate": 150.0, "Discount Factor": 0.02})

    # Insert Sub Contracts
    db.insert("Sub Contract", {"Sub Contract No": "SC001", "Sub Contract Name": "Concrete Works", "Company Name": "ABC Builders", "Contract Type": "Remeasurement", "Contract Sum": 50000.0, "Final Account Amount": 52000.0})
    db.insert("Sub Contract", {"Sub Contract No": "SC002", "Sub Contract Name": "Steel Supply", "Company Name": "Steel Corp", "Contract Type": "Lump Sum", "Contract Sum": 30000.0, "Final Account Amount": 31000.0})

    # Insert Sub Contract Persons
    db.insert("Sub Contract Person", {"Sub Contract": "SC001", "Name": "John Doe", "Position": "Manager", "Tel": "12345678", "Fax": "87654321", "Email": "john@abc.com"})
    db.insert("Sub Contract Person", {"Sub Contract": "SC002", "Name": "Jane Smith", "Position": "Engineer", "Tel": "87654321", "Fax": "12345678", "Email": "jane@steel.com"})

    # Insert Documents (check for duplicates)
    try:
        db.insert("Document Manager", {"File": "DOC001", "Date": "2023-01-01", "Type": "Site Memo", "Title": "Site Meeting Notes", "From": "PM", "To": "Contractor", "Cost Implication": False, "Time Implication": True, "Remark": "Discuss schedule"})
    except:
        pass  # Document already exists
    try:
        db.insert("Document Manager", {"File": "DOC002", "Date": "2023-02-01", "Type": "AI", "Title": "Change in Design", "From": "Architect", "To": "Contractor", "Cost Implication": True, "Time Implication": True, "Remark": "Additional works required"})
    except:
        pass  # Document already exists
    
    # Add more documents
    try:
        db.insert("Document Manager", {"File": "DOC003", "Date": "2023-03-01", "Type": "RFI", "Title": "Material Specification", "From": "Contractor", "To": "Architect", "Cost Implication": False, "Time Implication": False, "Remark": "Clarification needed"})
    except:
        pass
    try:
        db.insert("Document Manager", {"File": "DOC004", "Date": "2023-04-01", "Type": "CVI", "Title": "Variation Order Request", "From": "Contractor", "To": "PM", "Cost Implication": True, "Time Implication": True, "Remark": "Time extension required"})
    except:
        pass
    try:
        db.insert("Document Manager", {"File": "DOC005", "Date": "2023-05-01", "Type": "Shop Drawing", "Title": "Structural Drawings", "From": "Engineer", "To": "Contractor", "Cost Implication": False, "Time Implication": False, "Remark": "For approval"})
    except:
        pass

    # Insert more Abortive Work Records
    db.insert("Abortive Work Record", {"Abortive Ref": "AW005", "Date": "2023-07-01", "Issue Date": "2023-07-15", "Project Coordinator": "Coordinator E", "Cost Implication": True, "Time Implication": False, "Inspection Date": True, "Endorsement": True, "Description": "Equipment failure"})
    db.insert("Abortive Work Record", {"Abortive Ref": "AW006", "Date": "2023-08-01", "Issue Date": "2023-08-20", "Project Coordinator": "Coordinator F", "Cost Implication": False, "Time Implication": True, "Inspection Date": False, "Endorsement": False, "Description": "Supplier delay"})
    db.insert("Abortive Work Record", {"Abortive Ref": "AW007", "Date": "2023-09-01", "Issue Date": "2023-09-10", "Project Coordinator": "Coordinator G", "Cost Implication": True, "Time Implication": True, "Inspection Date": True, "Endorsement": False, "Description": "Design change required"})

    # Insert Main Contract VO
    db.insert("Main Contract VO", {"VO ref": "VO001", "Date": "2023-05-01", "Issue Date": "2023-05-15", "Description": "Additional concrete", "Application Amount": 10000.0, "Agree Amount": 9500.0, "Receive Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})
    db.insert("Main Contract VO", {"VO ref": "VO002", "Date": "2023-06-01", "Issue Date": "2023-06-20", "Description": "Steel reinforcement change", "Application Amount": 5000.0, "Agree Amount": 4800.0, "Receive Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})

    # Insert Main Contract BQ
    db.insert("Main Contract BQ", {"BQ ID": "BQ001", "Bill": "Bill 1", "Section": "Sec 1", "Page": "Pg 1", "Item": "Item 1", "description": "Concrete foundation", "Qty": 50.0, "Unit": "m3", "Rate": 400.0, "Trade": "Concrete", "Remark": "Standard work"})
    db.insert("Main Contract BQ", {"BQ ID": "BQ002", "Bill": "Bill 2", "Section": "Sec 2", "Page": "Pg 2", "Item": "Item 2", "description": "Steel bars", "Qty": 20.0, "Unit": "kg", "Rate": 1800.0, "Trade": "Steel", "Remark": "Reinforcement"})

    # Insert VO Items
    db.insert("VO Item", {"VO ref": "VO001", "Item": "VO Item 1", "Description": "Extra concrete", "Qty": "10", "Unit": "m3", "Rate": 450.0, "Trade": "Concrete", "Star Rate": False, "BQ ref": "BQ001", "Agree": True})
    db.insert("VO Item", {"VO ref": "VO002", "Item": "VO Item 2", "Description": "Additional steel", "Qty": "5", "Unit": "kg", "Rate": 1900.0, "Trade": "Steel", "Star Rate": False, "BQ ref": "BQ002", "Agree": True})

    # Insert Main Contract IP Applications
    db.insert("Main Contract IP Application", {"IP": 1, "Draft Date": "2023-06-15", "Issue Date": "2023-07-01", "Approved Date": "2023-07-10", "Payment Date": "2023-07-20", "Accumulated Applied Amount": 56000.0, "Previous Applied Amount": 0.0, "This Applied Amount": 56000.0, "Certified Amount": 54500.0, "Paid Amount": 54500.0, "Remark": "First payment"})
    db.insert("Main Contract IP Application", {"IP": 2, "Draft Date": "2023-07-15", "Issue Date": "2023-08-01", "Approved Date": "2023-08-10", "Payment Date": "2023-08-20", "Accumulated Applied Amount": 96000.0, "Previous Applied Amount": 56000.0, "This Applied Amount": 40000.0, "Certified Amount": 39000.0, "Paid Amount": 39000.0, "Remark": "Second payment"})

    # Insert Main Contract IP Items (fix table name)
    db.insert("Main Contract IP Item", {"IP": 1, "Item": 1, "Type": "Approved", "BQ Ref": "BQ001", "VO Ref": "VO001", "DOC Ref": "DOC001", "Description": "Concrete foundation work", "Applied Amount": 20000.0, "Certified Amount": 19500.0, "Paid Amount": 19500.0, "Remark": "Completed"})
    db.insert("Main Contract IP Item", {"IP": 1, "Item": 2, "Type": "Approved", "BQ Ref": "BQ002", "VO Ref": "VO002", "DOC Ref": "DOC002", "Description": "Steel reinforcement", "Applied Amount": 36000.0, "Certified Amount": 35000.0, "Paid Amount": 35000.0, "Remark": "Completed"})

    # Insert Sub Contract VO
    db.insert("Sub Contract VO", {"VO ref": "SCVO001", "Subcontract": "SC001", "Date": "2023-08-01", "Receive Date": "2023-08-05", "Description": "Extra concrete for sub", "Application Amount": 5000.0, "Agree Amount": 4800.0, "Issue Assessment": True, "Dispute": False, "Agree": True, "Reject": False, "Remark": "Approved"})

    # Insert Sub Con Works
    db.insert("Sub Con Works", {"Subcontract": "SC001", "Works": "Concrete Pouring", "Qty": 30.0, "Unit": "m3", "Rate": 420.0, "Discount": 0.05, "Trade": "Concrete"})
    db.insert("Sub Con Works", {"Subcontract": "SC002", "Works": "Steel Cutting", "Qty": 15.0, "Unit": "kg", "Rate": 1850.0, "Discount": 0.03, "Trade": "Steel"})

    # Insert SC VO Item
    db.insert("SC VO Item", {"VO ref": "SCVO001", "Item": "SC VO Item 1", "Description": "Extra sub concrete", "Qty": "5", "Unit": "m3", "Rate": 430.0, "Trade": "Concrete", "Star Rate": False, "BQ ref": "Concrete Pouring", "Agree": True})

    # Insert Sub Contract IP Applications
    db.insert("Sub Contract IP Application", {"Sub Contract No": "SC001", "IP": 1, "Draft Date": "2023-08-15", "Issue Date": "2023-09-01", "Approved Date": "2023-09-10", "Payment Date": "2023-09-20", "Accumulated Applied Amount": 12600.0, "Previous Applied Amount": 0.0, "This Applied Amount": 12600.0, "Certified Amount": 12000.0, "Paid Amount": 12000.0, "Remark": "Sub contract payment"})
    
    # Insert Sub Contract IP Items
    db.insert("Sub Contract IP Item", {"Sub Contract No": "SC001", "IP": 1, "Item": 1, "Type": "Approved", "Contract Work ref": "Concrete Pouring", "VO ref": "SCVO001", "DOC Ref": "DOC001", "Description": "Sub concrete work", "Applied Amount": 12600.0, "Certified Amount": 12000.0, "Paid Amount": 12000.0, "Remark": "Completed"})

    # Insert Contra Charge
    db.insert("Contra Charge", {"CC No": "CC001", "Date": "2023-10-01", "Title": "Delay Penalty", "Reason": "Late delivery", "Agree Amount": 1000.0, "Deduct To": "SC001"})

    # Insert Contra Charge Item
    db.insert("Contra Charge Item", {"CC No": "CC001", "Description": "Penalty for delay", "Qty": 1.0, "Unit": "no", "Rate": 1000.0, "Give to": "Concrete Pouring"})

    # Link Contra Charge to Documents (sample)
    try:
        db.insert("Contra Charge Document", {"CC No": "CC001", "Doc Ref": "DOC001", "Remark": "Penalty supporting doc"})
    except Exception:
        pass

    # Additional sample CC entries and documents
    db.insert("Contra Charge", {"CC No": "CC004", "Date": "2024-01-01", "Title": "Site Damage", "Reason": "Property damage", "Agree Amount": 1200.0, "Deduct To": "SC001"})
    db.insert("Contra Charge Item", {"CC No": "CC004", "Description": "Repair cost", "Qty": 1.0, "Unit": "no", "Rate": 1200.0, "Give to": "Concrete Pouring"})
    try:
        db.insert("Contra Charge Document", {"CC No": "CC004", "Doc Ref": "DOC002", "Remark": "Repair invoice"})
    except Exception:
        pass

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

    print("Fake data populated successfully!")
    db.close()

if __name__ == "__main__":
    populate_fake_data()
