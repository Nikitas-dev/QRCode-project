import pandas as pd
import json
import random

df = pd.read_csv(testing.csv)
activities = ["penalty","keepy","sponge"]

for i, row in df.iterrows():
    activity_status = {}
    qr_token = random.randint(1,10000)
    student_name = row["student_name"]
    year_group = row["year_group"]
    for item in activities:
        activity_status[f"paid_{item}"] = False

    entry = {
        "model": "QRCode_Main.student",
        "pk": None,
        "fields": {
            "qr_token": qr_token,
            "student_name": student_name,
            "year_group": year_group,
            **activity_status
        }
    }
    fixtures = []
    fixtures.append(entry)

with open("test.json", "w") as jaden:
        json.dump(fixtures, jaden)


