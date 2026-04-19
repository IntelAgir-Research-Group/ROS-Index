from pymongo import MongoClient
import pandas as pd

client = MongoClient(
    host="145.108.225.21",
    port=26452,
    username="user",
    password="goGreenS2!2025",
    authSource="admin"
)

db = client["admin"]

collections_config = {
    "ROSAnswers": {
        "discussion_type": "ros_answers",
        "date_field": "time"
    },
    "StackOverflow": {
        "discussion_type": "stackoverflow",
        "date_field": "time"
    }
}   

results = []

for collection_name, config in collections_config.items():
    collection = db[collection_name]
    date_field = config["date_field"]
    discussion_type = config["discussion_type"]

    print(f"Processing {collection_name} ...")

    for doc in collection.find({}, {date_field: 1, "_id": 0}):
        raw_date = doc.get(date_field)

        if raw_date:
            parsed_date = pd.to_datetime(raw_date, errors="coerce", utc=True)

            if pd.notna(parsed_date):
                results.append({
                    "discussion_type": discussion_type,
                    "date": parsed_date
                })
            else:
                print(f"Failed to parse: {raw_date}")

df = pd.DataFrame(results)

df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
df = df.dropna(subset=["date"])
df = df.sort_values("date")

df.to_csv("discussion_dates.csv", index=False)

print(df.head())
print(df.groupby("discussion_type")["date"].agg(["min", "max", "count"]))
print(f"Total records: {len(df)}")