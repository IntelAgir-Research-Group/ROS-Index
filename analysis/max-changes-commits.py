import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV
df = pd.read_csv("../mining/data/popularity/github_commits.csv")

# Convert commit_date to datetime
df["commit_date"] = pd.to_datetime(df["commit_date"], errors="coerce")

# Extract year
df["year"] = df["commit_date"].dt.year

# Remove rows with missing values
df = df.dropna(subset=["median_file_changes", "year"])

# Convert median_file_changes to numeric
df["median_file_changes"] = pd.to_numeric(df["median_file_changes"], errors="coerce")

# Remove invalid values
df = df.dropna(subset=["median_file_changes"])

# Define an upper threshold to remove extreme outliers
upper_threshold = 1000

# Keep only values below the threshold
df = df[df["median_file_changes"] <= upper_threshold]

# Get the row with the maximum median_file_changes for each year
idx = df.groupby("year")["median_file_changes"].idxmax()
yearly_max_rows = df.loc[idx].sort_values("year")

# Print repository and commit sha for each maximum
print("Maximum commit per year:")
for _, row in yearly_max_rows.iterrows():
    print(
        f"Year: {int(row['year'])} | "
        f"Repository: {row['repository']} | "
        f"Commit SHA: {row['commit_sha']} | "
        f"Total Changes: {int(row['median_file_changes'])}"
    )

# Create figure
plt.figure(figsize=(12, 6))

# Bar plot
plt.bar(
    yearly_max_rows["year"].astype(str),
    yearly_max_rows["median_file_changes"]
)

# Add trend line
z = np.polyfit(yearly_max_rows["year"], yearly_max_rows["median_file_changes"], 1)
p = np.poly1d(z)

plt.plot(
    yearly_max_rows["year"].astype(str),
    p(yearly_max_rows["year"]),
    linewidth=2,
    marker="o"
)

# Labels and title
plt.xlabel("Year")
plt.ylabel("Maximum Total Changes")
plt.title(f"Maximum Total Changes per Year (<= {upper_threshold})")

plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

plt.show()