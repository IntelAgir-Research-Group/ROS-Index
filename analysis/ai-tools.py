import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load data
# =========================
df = pd.read_csv("../mining/data/popularity/github_commits-bottom10.csv")

# =========================
# Cleaning
# =========================
# Convert date
df["commit_date"] = pd.to_datetime(df["commit_date"], errors="coerce")

# Extract year
df["year"] = df["commit_date"].dt.year

# Normalize ai_detected
df["ai_detected"] = df["ai_detected"].astype(str).str.lower() == "true"

# Keep only commits with AI score
df["ai_score"] = pd.to_numeric(df["ai_score"], errors="coerce")

df_clean = df.dropna(subset=["year", "ai_score"])

# OPTIONAL: focus only on AI commits
df_ai = df_clean[df_clean["ai_detected"] == True].copy()


# =========================
# Distribution of AI reasons (PREFIX ONLY) per year
# =========================

df_reasons = df_ai.copy()

# Clean column
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].fillna("").astype(str)

# Normalize separators
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.replace(";", ",")
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.replace("|", ",")

# Split into list
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.split(",")

# Explode
df_reasons = df_reasons.explode("ai_reasons")

# Clean whitespace
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.strip()

# Remove empty values
df_reasons = df_reasons[df_reasons["ai_reasons"] != ""]

# =========================
# Extract prefix BEFORE ":"
# =========================
df_reasons["reason_category"] = df_reasons["ai_reasons"].str.split(":").str[0]

# Normalize (lowercase)
df_reasons["reason_category"] = df_reasons["reason_category"].str.lower().str.strip()

# =========================
# Count frequencies
# =========================
reason_counts = (
    df_reasons.groupby(["year", "reason_category"])
    .size()
    .reset_index(name="count")
)

# Pivot
reason_pivot = reason_counts.pivot(
    index="reason_category", columns="year", values="count"
).fillna(0)

# =========================
# Plot
# =========================
import matplotlib.pyplot as plt

plt.figure()

reason_pivot.plot(kind="bar")

plt.title("Distribution of AI Reason Categories per Year")
plt.xlabel("Reason Category")
plt.ylabel("Number of Commits")

plt.xticks(rotation=45, ha="right")
plt.legend(title="Year")

plt.tight_layout()
plt.savefig("ai_reason_categories_per_year.png")
plt.show()

# # =========================
# # 1. Boxplot (best overview)
# # =========================
# plt.figure()

# df_ai.boxplot(column="ai_score", by="year")

# plt.title("Distribution of AI Scores per Year")
# plt.suptitle("")
# plt.xlabel("Year")
# plt.ylabel("AI Score")

# plt.tight_layout()
# plt.savefig("ai_score_boxplot_per_year.png")
# plt.show()

# # =========================
# # 2. Violin plot (better shape)
# # =========================
# plt.figure()

# years = sorted(df_ai["year"].dropna().unique())

# data = [df_ai[df_ai["year"] == y]["ai_score"] for y in years]

# plt.violinplot(data, showmeans=True)

# plt.xticks(range(1, len(years) + 1), years)
# plt.title("AI Score Distribution per Year (Violin)")
# plt.xlabel("Year")
# plt.ylabel("AI Score")

# plt.tight_layout()
# plt.savefig("ai_score_violin_per_year.png")
# plt.show()

# # =========================
# # 3. Histogram per year
# # =========================
# for y in years:
#     subset = df_ai[df_ai["year"] == y]

#     plt.figure()
#     subset["ai_score"].plot(kind="hist", bins=15)

#     plt.title(f"AI Score Distribution - {y}")
#     plt.xlabel("AI Score")
#     plt.ylabel("Frequency")

#     plt.tight_layout()
#     plt.savefig(f"ai_score_hist_{y}.png")
#     plt.close()

# # =========================
# # 4. Mean trend (optional but useful)
# # =========================
# mean_scores = df_ai.groupby("year")["ai_score"].mean()

# plt.figure()
# mean_scores.plot(marker='o')

# plt.title("Average AI Score per Year")
# plt.xlabel("Year")
# plt.ylabel("Average AI Score")

# plt.tight_layout()
# plt.savefig("ai_score_mean_trend.png")
# plt.show()

# print("All plots generated successfully!")

# # =========================
# # Normalized frequency (percentage)
# # =========================
# freq_pct = freq.copy()

# freq_pct["percentage"] = freq_pct.groupby("year")["count"].transform(
#     lambda x: x / x.sum() * 100
# )

# freq_pct_pivot = freq_pct.pivot(
#     index="ai_score", columns="year", values="percentage"
# ).fillna(0)

# freq_pct_pivot.plot(kind="bar")

# plt.title("Percentage Distribution of AI Scores per Year")
# plt.xlabel("AI Score")
# plt.ylabel("Percentage (%)")

# plt.xticks(rotation=0)
# plt.legend(title="Year")
# plt.tight_layout()

# plt.savefig("ai_score_frequency_percentage.png")
# plt.show()

# =========================
# Distribution of AI reasons per year
# =========================

# Work on AI commits only
df_reasons = df_ai.copy()

# Clean and split reasons
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].fillna("").astype(str)

# Support multiple separators
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.replace(";", ",")
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.replace("|", ",")

# Split into lists
df_reasons["ai_reasons"] = df_reasons["ai_reasons"].str.split(",")

# Explode (one reason per row)
df_reasons = df_reasons.explode("ai_reasons")

# Clean text
df_reasons["ai_reasons"] = (
    df_reasons["ai_reasons"]
    .str.strip()
    .str.lower()
)

# Remove empty values
df_reasons = df_reasons[df_reasons["ai_reasons"] != ""]

# =========================
# Count frequencies
# =========================
reason_counts = (
    df_reasons.groupby(["year", "ai_reasons"])
    .size()
    .reset_index(name="count")
)

# Pivot for plotting
reason_pivot = reason_counts.pivot(
    index="ai_reasons", columns="year", values="count"
).fillna(0)

# =========================
# Plot (raw counts)
# =========================
plt.figure()

reason_pivot.plot(kind="bar")

plt.title("Distribution of AI Reasons per Year")
plt.xlabel("AI Reasons")
plt.ylabel("Number of Commits")

plt.xticks(rotation=45, ha="right")
plt.legend(title="Year")

plt.tight_layout()
plt.savefig("ai_reasons_distribution.png")
plt.show()


# =========================
# Overall AI score distribution
# =========================
plt.figure()

df_ai["ai_score"].plot(kind="box")

plt.title("Overall Distribution of AI Scores")
plt.ylabel("AI Score")

plt.tight_layout()
plt.savefig("ai_score_overall_boxplot.png")
plt.show()