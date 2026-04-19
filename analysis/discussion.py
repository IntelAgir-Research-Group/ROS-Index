
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# Load discussion data
# --------------------------------------------------
df = pd.read_csv("../mining/data/discussion/discussion_dates.csv")

# Parse dates
df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)

# Remove invalid dates
df = df.dropna(subset=["date"])

# Extract year and month
df["year"] = df["date"].dt.year
df["year_month"] = df["date"].dt.to_period("M").astype(str)

# --------------------------------------------------
# Aggregated totals by discussion type
# --------------------------------------------------
type_counts = df["discussion_type"].value_counts()

plt.figure(figsize=(10, 6))
type_counts.plot(kind="bar")
plt.xlabel("Discussion Type")
plt.ylabel("Total Number of Discussions")
plt.title("Total Discussions by Type")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("discussion_totals_by_type.png", dpi=300)
plt.close()

# Save aggregated table
type_counts.to_csv("discussion_totals_by_type.csv", header=["count"])

# --------------------------------------------------
# Aggregated totals by year
# --------------------------------------------------
year_counts = df.groupby("year").size()

plt.figure(figsize=(12, 6))
year_counts.plot(kind="bar")
plt.xlabel("Year")
plt.ylabel("Total Number of Discussions")
plt.title("Total Discussions by Year")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("discussion_totals_by_year.png", dpi=300)
plt.close()

year_counts.to_csv("discussion_totals_by_year.csv", header=["count"])

# --------------------------------------------------
# Aggregated totals by month with trend line
# --------------------------------------------------
month_counts = df.groupby("year_month").size()

x = np.arange(len(month_counts))
y = month_counts.values

# Linear trend line
z = np.polyfit(x, y, 1)
p = np.poly1d(z)

plt.figure(figsize=(20, 6))
plt.plot(month_counts.index, y, label="Monthly Discussions")
plt.plot(
    month_counts.index,
    p(x),
    linestyle="--",
    linewidth=2,
    label="Trend Line"
)

plt.xlabel("Month")
plt.ylabel("Total Number of Discussions")
plt.title("Total Discussions by Month with Trend Line")
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.savefig("discussion_totals_by_month_with_trend.png", dpi=300)
plt.close()

month_counts.to_csv("discussion_totals_by_month.csv", header=["count"])

# --------------------------------------------------
# Discussions by year and type
# --------------------------------------------------
year_type_counts = (
    df.groupby(["year", "discussion_type"])
    .size()
    .unstack(fill_value=0)
)

year_type_counts.plot(kind="bar", figsize=(14, 7))
plt.xlabel("Year")
plt.ylabel("Number of Discussions")
plt.title("Discussion Frequency by Year and Type")
plt.xticks(rotation=45)
plt.legend(title="Discussion Type")
plt.tight_layout()
plt.savefig("discussion_frequency_by_year_and_type.png", dpi=300)
plt.close()

year_type_counts.to_csv("discussion_frequency_by_year_and_type.csv")

# --------------------------------------------------
# Discussions by month and type
# --------------------------------------------------
month_type_counts = (
    df.groupby(["year_month", "discussion_type"])
    .size()
    .unstack(fill_value=0)
)

plt.figure(figsize=(20, 8))

for discussion_type in month_type_counts.columns:
    y = month_type_counts[discussion_type].values
    x = np.arange(len(y))

    plt.plot(month_type_counts.index, y, label=discussion_type)

    # Trend line for each type
    if len(y) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        plt.plot(
            month_type_counts.index,
            p(x),
            linestyle="--",
            linewidth=2
        )

plt.xlabel("Month")
plt.ylabel("Number of Discussions")
plt.title("Discussion Frequency by Month and Type with Trend Lines")
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.savefig("discussion_frequency_by_month_and_type_with_trends.png", dpi=300)
plt.close()

month_type_counts.to_csv("discussion_frequency_by_month_and_type.csv")

# --------------------------------------------------
# Stacked area chart
# --------------------------------------------------
month_type_counts.plot(
    kind="area",
    stacked=True,
    figsize=(20, 8)
)
plt.xlabel("Month")
plt.ylabel("Number of Discussions")
plt.title("Monthly Discussion Frequency by Type (Stacked Area)")
plt.xticks(rotation=90)
plt.legend(title="Discussion Type")
plt.tight_layout()
plt.savefig("discussion_frequency_stacked_area.png", dpi=300)
plt.close()

# --------------------------------------------------
# One subplot per discussion type
# --------------------------------------------------
discussion_types = sorted(df["discussion_type"].unique())

fig, axes = plt.subplots(
    len(discussion_types),
    1,
    figsize=(20, 4 * len(discussion_types)),
    sharex=True
)

if len(discussion_types) == 1:
    axes = [axes]

for ax, discussion_type in zip(axes, discussion_types):
    subset = df[df["discussion_type"] == discussion_type]

    counts = (
        subset.groupby("year_month")
        .size()
    )

    x = np.arange(len(counts))
    y = counts.values

    ax.plot(counts.index, y, label=discussion_type)

    # Trend line
    if len(y) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        ax.plot(
            counts.index,
            p(x),
            linestyle="--",
            linewidth=2,
            label="Trend"
        )

    ax.set_title(f"Monthly Discussion Frequency - {discussion_type}")
    ax.set_ylabel("Discussions")
    ax.legend()
    ax.tick_params(axis="x", rotation=90)

plt.xlabel("Month")
plt.tight_layout()
plt.savefig("discussion_frequency_monthly_subplots.png", dpi=300)
plt.close()

# --------------------------------------------------
# Log-scale graph to make smaller sources visible
# --------------------------------------------------
month_type_counts.plot(kind="line", figsize=(20, 8))
plt.yscale("log")
plt.xlabel("Month")
plt.ylabel("Number of Discussions (log scale)")
plt.title("Discussion Frequency by Month and Type (Log Scale)")
plt.xticks(rotation=90)
plt.legend(title="Discussion Type")
plt.tight_layout()
plt.savefig("discussion_frequency_by_month_and_type_log.png", dpi=300)
plt.close()

# --------------------------------------------------
# Print summary
# --------------------------------------------------
print("Discussion type counts:")
print(type_counts)

print("\nDate range:")
print(df["date"].min(), "to", df["date"].max())

print("\nSaved graphs:")
print("- discussion_totals_by_type.png")
print("- discussion_totals_by_year.png")
print("- discussion_totals_by_month_with_trend.png")
print("- discussion_frequency_by_year_and_type.png")
print("- discussion_frequency_by_month_and_type_with_trends.png")
print("- discussion_frequency_stacked_area.png")
print("- discussion_frequency_monthly_subplots.png")
print("- discussion_frequency_by_month_and_type_log.png")