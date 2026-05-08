import pandas as pd

# Load commit-level file
commits_csv = "../mining/data/popularity/github_commits-bottom10.csv"

df = pd.read_csv(commits_csv)

# Convert ai_detected to boolean
df["ai_detected"] = (
    df["ai_detected"]
    .astype(str)
    .str.lower()
    .map({
        "true": True,
        "false": False
    })
)

# Convert commit date
df["commit_date"] = pd.to_datetime(
    df["commit_date"],
    errors="coerce"
)

# Extract year
df["year"] = df["commit_date"].dt.year

# Remove rows with invalid year
df = df.dropna(subset=["year"])

df["year"] = df["year"].astype(int)

# ==========================================================
# Global Counts by Year
# ==========================================================

year_summary = (
    df.groupby("year")
    .agg(
        total_commits=("commit_sha", "count"),
        ai_commits=("ai_detected", "sum")
    )
    .reset_index()
)

year_summary["non_ai_commits"] = (
    year_summary["total_commits"] - year_summary["ai_commits"]
)

year_summary["ai_percentage"] = (
    year_summary["ai_commits"] / year_summary["total_commits"] * 100
).round(2)

print("==================================================")
print("GLOBAL AI DETECTION SUMMARY BY YEAR")
print("==================================================")
print(year_summary)

# ==========================================================
# Per Repository Counts by Year
# ==========================================================

repo_year_summary = (
    df.groupby(["repository", "year"])
    .agg(
        total_commits=("commit_sha", "count"),
        ai_commits=("ai_detected", "sum")
    )
    .reset_index()
)

repo_year_summary["non_ai_commits"] = (
    repo_year_summary["total_commits"] - repo_year_summary["ai_commits"]
)

repo_year_summary["ai_percentage"] = (
    repo_year_summary["ai_commits"] / repo_year_summary["total_commits"] * 100
).round(2)

repo_year_summary = repo_year_summary.sort_values(
    by=["year", "ai_commits"],
    ascending=[True, False]
)

print("\n==================================================")
print("PER-REPOSITORY AI DETECTION SUMMARY BY YEAR")
print("==================================================")
print(repo_year_summary)

# ==========================================================
# Save Results
# ==========================================================

year_output_csv = "../mining/data/popularity/github_ai_commit_counts_by_year.csv"
repo_year_output_csv = "../mining/data/popularity/github_ai_commit_counts_by_repo_year.csv"

year_summary.to_csv(year_output_csv, index=False)
repo_year_summary.to_csv(repo_year_output_csv, index=False)

print(f"\nSaved yearly summary to: {year_output_csv}")
print(f"Saved repository yearly summary to: {repo_year_output_csv}") 

# GRAPHS

import matplotlib.pyplot as plt

# Set year as index for easier plotting
plot_df = year_summary.set_index("year")

# Stacked bar plot
plot_df[["ai_commits", "non_ai_commits"]].plot(
    kind="bar",
    stacked=True
)

plt.title("AI vs Non-AI Commits per Year")
plt.xlabel("Year")
plt.ylabel("Number of Commits")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("../mining/data/popularity/ai_vs_non_ai_commits.png")
plt.show()

plt.figure()

plt.plot(
    year_summary["year"],
    year_summary["ai_percentage"],
    marker="o"
)

plt.title("AI Commit Percentage Over Time")
plt.xlabel("Year")
plt.ylabel("AI % of Commits")

plt.grid()

plt.tight_layout()
plt.savefig("../mining/data/popularity/ai_percentage_trend.png")
plt.show()

year_summary["ai_growth"] = year_summary["ai_commits"].pct_change() * 100
year_summary["non_ai_growth"] = year_summary["non_ai_commits"].pct_change() * 100

plt.figure()

plt.plot(year_summary["year"], year_summary["ai_growth"], label="AI Growth", marker="o")
plt.plot(year_summary["year"], year_summary["non_ai_growth"], label="Non-AI Growth", marker="o")

plt.legend()
plt.title("Growth Rate: AI vs Non-AI Commits")
plt.xlabel("Year")
plt.ylabel("Growth (%)")

plt.grid()

plt.tight_layout()
plt.savefig("../mining/data/popularity/growth_comparison.png")
plt.show()

latest_year = repo_year_summary["year"].max()

top_repos = (
    repo_year_summary[repo_year_summary["year"] == latest_year]
    .sort_values(by="ai_commits", ascending=False)
    .head(10)
)

plt.figure()

plt.barh(
    top_repos["repository"],
    top_repos["ai_commits"]
)

plt.title(f"Top 10 Repositories by AI Commits ({latest_year})")
plt.xlabel("AI Commits")
plt.ylabel("Repository")

plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig("../mining/data/popularity/top_repos_ai_commits.png")
plt.show()