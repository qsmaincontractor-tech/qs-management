import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from function.DB_manager import DB_Manager
import traceback

try:
    print("Creating DB manager...")
    db = DB_Manager('database/QS_Project.db')
    print("DB manager created successfully")

    print("Testing insert...")
    result = db.insert('Document Manager', {
        'File': 'DOC001',
        'Date': '2026-01-04',
        'Type': '',
        'Title': '',
        'From': '',
        'To': '',
        'Cost Implication': False,
        'Time Implication': False,
        'Remark': ''
    })
    print(f'Insert result: {result}')

    print("Testing fetch...")
    records = db.fetch_all('SELECT * FROM "Document Manager"')
    print(f'Records found: {len(records)}')

    print("Closing database...")
    db.close()
    print("Test completed successfully")

except Exception as e:
    print(f"Error occurred: {e}")
    traceback.print_exc()