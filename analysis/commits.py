import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("../mining/data/popularity/github_commits.csv")

# Convert commit_date to datetime
df["commit_date"] = pd.to_datetime(df["commit_date"], errors="coerce")

# Extract year
df["year"] = df["commit_date"].dt.year

# Remove rows with missing values in total_changes or year
df = df.dropna(subset=["total_changes", "year"])

# Convert total_changes to numeric
df["total_changes"] = pd.to_numeric(df["total_changes"], errors="coerce")

# Remove invalid values
df = df.dropna(subset=["total_changes"])

# Sort years
years = sorted(df["year"].unique())

# Prepare data for boxplot
boxplot_data = [
    df[df["year"] == year]["total_changes"]
    for year in years
]

# Create figure
plt.figure(figsize=(12, 6))

plt.boxplot(
    boxplot_data,
    labels=years,
    showfliers=False
)

plt.xlabel("Year")
plt.ylabel("Total Changes")
plt.title("Distribution of Total Changes per Commit by Year")

plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.show()