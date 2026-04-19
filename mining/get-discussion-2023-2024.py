from pymongo import MongoClient
import pandas as pd

# --------------------------------------------------
# MongoDB connection
# --------------------------------------------------
client = MongoClient(
    host="145.108.225.21",
    port=26452,
    username="user",
    password="goGreenS2!2025",
    authSource="admin"
)

db = client["admin"]

# --------------------------------------------------
# Collections to analyze
# --------------------------------------------------
collections_config = {
    "ROSAnswers": {
        "discussion_type": "ros_answers",
        "date_field": "time",
        "title_field": "title"
    },
    "StackOverflow": {
        "discussion_type": "stackoverflow",
        "date_field": "time",
        "title_field": "title"
    }
}

results = []

# --------------------------------------------------
# Process collections
# --------------------------------------------------
for collection_name, config in collections_config.items():
    collection = db[collection_name]

    discussion_type = config["discussion_type"]
    date_field = config["date_field"]
    title_field = config["title_field"]

    print(f"Processing {collection_name} ...")

    for doc in collection.find({}, {
        date_field: 1,
        title_field: 1,
        "_id": 0
    }):
        raw_date = doc.get(date_field)
        title = doc.get(title_field, "")

        if raw_date:
            parsed_date = pd.to_datetime(raw_date, errors="coerce", utc=True)

            if pd.notna(parsed_date):
                year = parsed_date.year

                if year in [2023, 2024]:
                    results.append({
                        "date": parsed_date,
                        "year": year,
                        "discussion_type": discussion_type,
                        "title": title
                    })

# --------------------------------------------------
# Create dataframe
# --------------------------------------------------
df = pd.DataFrame(results)

# Sort by date
df = df.sort_values("date")

# Save complete CSV
df.to_csv("discussion_titles_2023_2024.csv", index=False)

# Save separate CSVs by year
df[df["year"] == 2023].to_csv(
    "discussion_titles_2023.csv",
    index=False
)

df[df["year"] == 2024].to_csv(
    "discussion_titles_2024.csv",
    index=False
)

# Save separate CSVs by type
df[df["discussion_type"] == "ros_answers"].to_csv(
    "ros_answers_titles_2023_2024.csv",
    index=False
)

df[df["discussion_type"] == "stackoverflow"].to_csv(
    "stackoverflow_titles_2023_2024.csv",
    index=False
)

# --------------------------------------------------
# Print summary
# --------------------------------------------------
print("\nTotal records:", len(df))
print("\nCounts by year:")
print(df["year"].value_counts().sort_index())

print("\nCounts by discussion type:")
print(df["discussion_type"].value_counts())

print("\nFirst rows:")
print(df.head())

print("\nSaved files:")
print("- discussion_titles_2023_2024.csv")
print("- discussion_titles_2023.csv")
print("- discussion_titles_2024.csv")
print("- ros_answers_titles_2023_2024.csv")
print("- stackoverflow_titles_2023_2024.csv")