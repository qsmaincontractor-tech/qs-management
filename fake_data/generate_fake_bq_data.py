import pandas as pd
import random
import string

# Generate 100 fake records for Main Contract BQ
data = []
for i in range(1, 101):
    bq_id = f"BQ{i:03d}"
    bill = f"Bill {random.randint(1, 10)}"
    section = f"Section {random.randint(1, 5)}"
    page = f"Page {random.randint(1, 20)}"
    item = f"Item {i}"
    description = f"Description for item {i}"
    qty = round(random.uniform(1, 1000), 2)
    unit = random.choice(["m2", "m3", "kg", "ton", "ls", "nr"])
    rate = round(random.uniform(10, 500), 2)
    discount = round(random.uniform(0, 0.1), 2)
    trade = random.choice(["Electrical", "Mechanical", "Civil", "Plumbing"])
    remark = random.choice(["", "Special requirement", "To be confirmed", "Approved"])

    data.append({
        "BQ ID": bq_id,
        "Bill": bill,
        "Section": section,
        "Page": page,
        "Item": item,
        "Description": description,
        "Qty": qty,
        "Unit": unit,
        "Rate": rate,
        "Discount": discount,
        "Trade": trade,
        "Remark": remark
    })

df = pd.DataFrame(data)
df.to_excel("fake_bq_data.xlsx", index=False)
print("Fake data generated: fake_bq_data.xlsx")