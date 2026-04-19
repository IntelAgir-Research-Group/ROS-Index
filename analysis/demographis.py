import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import os

# ==========================
# Configuration
# ==========================
CSV_FILE = "./data/mining/demographics/ros_packages_url.csv"
OUTPUT_DIR = "./analysis/output/demographics"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================
# Load CSV
# ==========================
df = pd.read_csv(CSV_FILE)

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Convert numeric columns
numeric_columns = ["Dependencies", "Other Packages Used"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Convert Last Commit to datetime
df["Last Commit"] = pd.to_datetime(df["Last Commit"], errors="coerce")

# ==========================
# Basic Statistics
# ==========================
print("========== BASIC STATISTICS ==========")
print(f"Total packages: {len(df)}")
print(f"Average dependencies: {df['Dependencies'].mean():.2f}")
print(f"Average other packages used: {df['Other Packages Used'].mean():.2f}")
print(f"Median dependencies: {df['Dependencies'].median()}")
print(f"Maximum dependencies: {df['Dependencies'].max()}")
print(f"Minimum dependencies: {df['Dependencies'].min()}")

# ==========================
# Top Organizations
# ==========================
top_orgs = df["Org"].value_counts().head(10)

print("\n========== TOP ORGANIZATIONS ==========")
print(top_orgs)

plt.figure(figsize=(10, 6))
top_orgs.sort_values().plot(kind="barh")
plt.title("Top 10 Organizations by Number of Packages")
plt.xlabel("Number of Packages")
plt.ylabel("Organization")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_organizations.pdf")
plt.close()

# ==========================
# Top Maintainers
# ==========================
maintainers = []

for value in df["Maintainers"].dropna():
    split_names = [name.strip() for name in str(value).split(",")]
    maintainers.extend(split_names)

top_maintainers = pd.Series(Counter(maintainers)).sort_values(ascending=False).head(10)

print("\n========== TOP MAINTAINERS ==========")
print(top_maintainers)

plt.figure(figsize=(10, 6))
top_maintainers.sort_values().plot(kind="barh")
plt.title("Top 10 Maintainers")
plt.xlabel("Number of Packages Maintained")
plt.ylabel("Maintainer")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_maintainers.png")
plt.close()

# ==========================
# Dependency Distribution
# ==========================
plt.figure(figsize=(10, 6))
plt.hist(df["Dependencies"], bins=20)
plt.title("Distribution of Package Dependencies")
plt.xlabel("Number of Dependencies")
plt.ylabel("Number of Packages")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/dependencies_distribution.pdf")
plt.close()

# ==========================
# Other Packages Used Distribution
# ==========================
plt.figure(figsize=(10, 6))
plt.hist(df["Other Packages Used"], bins=20)
plt.title("Distribution of Other Packages Used")
plt.xlabel("Other Packages Used")
plt.ylabel("Number of Packages")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/other_packages_distribution.png")
plt.close()

# ==========================
# Scatter Plot: Dependencies vs Other Packages Used
# ==========================
plt.figure(figsize=(8, 6))
plt.scatter(df["Dependencies"], df["Other Packages Used"], alpha=0.7)
plt.title("Dependencies vs Other Packages Used")
plt.xlabel("Dependencies")
plt.ylabel("Other Packages Used")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/dependencies_vs_other_packages.png")
plt.close()

# ==========================
# Package Activity by Last Commit Year
# ==========================
df["Commit Year"] = df["Last Commit"].dt.year

commit_years = df["Commit Year"].value_counts().sort_index()

print("\n========== PACKAGE ACTIVITY BY YEAR ==========")
print(commit_years)

plt.figure(figsize=(10, 6))
commit_years.plot(kind="bar")
plt.title("Package Last Commit Year Distribution")
plt.xlabel("Year")
plt.ylabel("Number of Packages")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/commit_year_distribution.png")
plt.close()

# ==========================
# Recently Updated Packages
# ==========================
recent_threshold = pd.Timestamp("2025-01-01")
recent_packages = df[df["Last Commit"] >= recent_threshold]

print("\n========== RECENTLY UPDATED PACKAGES ==========")
print(recent_packages[["Package", "Org", "Last Commit"]].head(20))

recent_packages.to_csv(f"{OUTPUT_DIR}/recent_packages.csv", index=False)

# ==========================
# Top Packages by Dependencies
# ==========================
top_dependencies = df.sort_values(by="Dependencies", ascending=False).head(20)

print("\n========== TOP PACKAGES BY DEPENDENCIES ==========")
print(top_dependencies[["Package", "Dependencies"]])

plt.figure(figsize=(12, 8))
plt.barh(top_dependencies["Package"], top_dependencies["Dependencies"])
plt.title("Top 20 Packages by Number of Dependencies")
plt.xlabel("Dependencies")
plt.ylabel("Package")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/top_packages_dependencies.png")
plt.close()

# ==========================
# Bubble Chart with Prediction Line
# ==========================
import numpy as np
from adjustText import adjust_text


repo_stats = []

for repo, group in df.groupby("Repository"):
    package_count = len(group)

    maintainers = set()
    for value in group["Maintainers"].dropna():
        names = [name.strip() for name in str(value).split(",")]
        maintainers.update(names)

    maintainer_count = len(maintainers)

    repo_stats.append({
        "Repository": repo,
        "Package Count": package_count,
        "Maintainer Count": maintainer_count
    })

repo_stats_df = pd.DataFrame(repo_stats)

# Keep top repositories by package count
repo_stats_df = repo_stats_df.sort_values(
    by="Package Count",
    ascending=False
).head(30)

x = repo_stats_df["Package Count"]
y = repo_stats_df["Maintainer Count"]

# Linear regression line
coefficients = np.polyfit(x, y, 1)
poly = np.poly1d(coefficients)

x_line = np.linspace(x.min(), x.max(), 100)
y_line = poly(x_line)

plt.figure(figsize=(12, 8))

# Bubble chart
plt.scatter(
    x,
    y,
    s=x * 100,
    alpha=0.6
)

# Prediction line
plt.plot(
    x_line,
    y_line,
    linewidth=2,
    label="Trend Line"
)

# Add repository labels
# Store text objects
texts = []

for _, row in repo_stats_df.iterrows():
    texts.append(
        plt.text(
            row["Package Count"],
            row["Maintainer Count"],
            row["Repository"],
            fontsize=12
        )
    )

# Automatically adjust labels to avoid overlap
adjust_text(
    texts,
    arrowprops=dict(arrowstyle="-", lw=0.5)
)

plt.xlabel("Number of Packages in Repository", fontsize=16)
plt.ylabel("Number of Unique Maintainers", fontsize=16)
plt.legend(fontsize=12)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/packages_vs_maintainers_bubble_trend.pdf")
plt.close()

# ==========================
# Correlation Analysis
# ==========================
correlation = df["Dependencies"].corr(df["Other Packages Used"])

print("\n========== CORRELATION ==========")
print(f"Correlation between Dependencies and Other Packages Used: {correlation:.3f}")

# ==========================
# Save Summary Report
# ==========================
with open(f"{OUTPUT_DIR}/summary_report.txt", "w") as f:
    f.write("ROS Package Dataset Analysis\n")
    f.write("============================\n\n")
    f.write(f"Total packages: {len(df)}\n")
    f.write(f"Average dependencies: {df['Dependencies'].mean():.2f}\n")
    f.write(f"Average other packages used: {df['Other Packages Used'].mean():.2f}\n")
    f.write(f"Median dependencies: {df['Dependencies'].median()}\n")
    f.write(f"Maximum dependencies: {df['Dependencies'].max()}\n")
    f.write(f"Minimum dependencies: {df['Dependencies'].min()}\n")
    f.write(f"Correlation between Dependencies and Other Packages Used: {correlation:.3f}\n")

print("\nAnalysis completed successfully.")
print(f"Results saved in: {OUTPUT_DIR}/")