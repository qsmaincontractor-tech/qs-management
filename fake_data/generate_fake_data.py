from function.DB_manager import DB_Manager
from function.Payment_Application_manager import Payment_Application_Manager
import os
import datetime
import random

# Setup
db_path = os.path.join('database', 'QS_Project.db')
db = DB_Manager(db_path)
manager = Payment_Application_Manager(db)

# Fake data generation
def generate_fake_data():
    print("Generating fake data for Payment Applications...")

    # Sample data
    types = ["BQ", "VO", "DOC", "Other"]
    descriptions = [
        "Foundation works",
        "Structural steel",
        "Concrete pouring",
        "Electrical installation",
        "Plumbing works",
        "Finishing works",
        "Roofing",
        "HVAC installation"
    ]
    remarks = ["", "As per contract", "Revised amount", "Additional works", "Variation order"]

    # Create 5 IP applications
    for ip_no in range(1, 6):
        # Random dates
        draft_date = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        issue_date = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        approved_date = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        payment_date = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        remark = random.choice(remarks)

        # Create IP Application
        manager.create_payment_application(
            ip_no,
            draft_date=draft_date,
            issue_date=issue_date,
            approved_date=approved_date,
            payment_date=payment_date,
            remark=remark
        )

        # Create 2-4 items per IP
        num_items = random.randint(2, 4)
        for item_no in range(1, num_items + 1):
            item_type = random.choice(types)
            bq_ref = f"BQ{random.randint(1,50):03d}" if random.random() > 0.3 else ""
            vo_ref = f"VO{random.randint(1,20):03d}" if random.random() > 0.5 else ""
            doc_ref = f"DOC{random.randint(1,30):03d}" if random.random() > 0.6 else ""
            description = random.choice(descriptions)
            applied_amt = random.randint(5000, 100000)
            certified_amt = applied_amt * random.uniform(0.8, 1.0)
            paid_amt = certified_amt * random.uniform(0.5, 1.0) if random.random() > 0.2 else 0
            item_remark = random.choice(remarks)

            manager.add_ip_item(
                ip_no, item_no, item_type, bq_ref, vo_ref, doc_ref,
                description, applied_amt, certified_amt, paid_amt, item_remark
            )

        # Calculate totals for this IP
        manager.calculate_ip_totals(ip_no)

    print("Fake data generation completed!")

# Run the generation
generate_fake_data()

# Verify by listing
print("\nVerifying generated data:")
apps = manager.get_all_payment_applications()
for app in apps:
    print(f"IP {app['IP']}: Draft {app['Draft Date']}, Accumulated: {app['Accumulated Applied Amount']}")
    items = manager.get_ip_items(app['IP'])
    for item in items:
        print(f"  Item {item['Item']}: {item['Description']} - Applied: {item['Applied Amount']}")

db.close()