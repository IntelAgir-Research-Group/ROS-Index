import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("../mining/data/popularity/github_commits-top10.csv")

# Convert commit_date to datetime
df["commit_date"] = pd.to_datetime(df["commit_date"], errors="coerce")

# Extract year
df["year"] = df["commit_date"].dt.year

# Remove rows with missing values in total: or year
df = df.dropna(subset=["avg_file_changes", "year"])

# Convert total_changes to numeric
df["total_changes"] = pd.to_numeric(df["avg_file_changes"], errors="coerce")

# Remove invalid values
df = df.dropna(subset=["avg_file_changes"])

# Define an upper threshold to remove extreme outliers
upper_threshold = 500

# Keep only values below the threshold
df = df[df["avg_file_changes"] <= upper_threshold]

# Sort years
years = sorted(df["year"].unique())

# Prepare data for violin plot
violin_data = [
    df[df["year"] == year]["avg_file_changes"]
    for year in years
]

# Create figure
plt.figure(figsize=(12, 6))

parts = plt.violinplot(
    violin_data,
    showmeans=True,
    showmedians=True,
    showextrema=False
)

# Set x-axis labels
plt.xticks(range(1, len(years) + 1), years)

plt.xlabel("Year")
plt.ylabel("Total Changes")
plt.title(f"Distribution of Total Changes per Commit by Year (<= {upper_threshold})")

plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.show()