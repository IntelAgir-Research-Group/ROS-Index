import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Create output directory if it does not exist
output_dir = "output/popularity"
os.makedirs(output_dir, exist_ok=True)

# Load the CSV file
df = pd.read_csv("../mining/demographics/ros_packages_with_github_metrics.csv")

# Column names
stars_column = "GitHub Stars"
forks_column = "GitHub Forks"
watchers_column = "GitHub Watchers"
repo_column = "URL"

# Keep only required columns and remove invalid rows
df = df[[repo_column, stars_column, forks_column, watchers_column]].dropna()
df = df[
    (df[stars_column] > 0) &
    (df[forks_column] > 0) &
    (df[watchers_column] > 0)
]

# Scale watcher values for bubble size
bubble_sizes = df[watchers_column] * 8

# Create figure
plt.figure(figsize=(12, 7))

# Bubble chart
plt.scatter(
    df[stars_column],
    df[forks_column],
    s=bubble_sizes,
    alpha=0.5
)

# Set axes to logarithmic scale
plt.xscale("log")
plt.yscale("log")

# Highlight important repositories
highlight_keywords = [
    "mavlink",
    "librealsense",
    "navigation2",
    "usb_cam",
    "velodyne",
    "plotjuggler",
    "realsense-ros"
]

for _, row in df.iterrows():
    repo_url = str(row[repo_column]).lower()

    if any(keyword in repo_url for keyword in highlight_keywords):
        repo_name = repo_url.rstrip("/").split("/")[-1]

        plt.annotate(
            repo_name,
            (row[stars_column], row[forks_column]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=12
        )

# Labels and title
plt.xlabel("GitHub Stars (log scale)", fontsize=14)
plt.ylabel("GitHub Forks (log scale)", fontsize=14)
#plt.title("ROS 2 Project Popularity and Community Engagement")
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Optional legend for bubble size
example_sizes = [10, 50, 100, 200]
for size in example_sizes:
    plt.scatter([], [], s=size * 8, alpha=0.5, label=f"{size} watchers")

plt.legend(title="Bubble Size", loc="lower right")

# Grid for readability
plt.grid(True, which="both", linestyle="--", alpha=0.5)

# Improve layout
plt.tight_layout()

# Save figure
plt.savefig(f"{output_dir}/github_stars_forks_watchers_bubble_chart.pdf", dpi=300)

# Show plot
plt.show()