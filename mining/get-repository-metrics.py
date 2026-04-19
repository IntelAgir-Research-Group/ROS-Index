# Python Script to Collect GitHub Repository Metrics from a CSV

import pandas as pd
import requests
import time

# Load CSV
input_csv = "ros_repository_github.csv"
output_csv = "ros_packages_with_github_metrics.csv"

# Optional: GitHub personal access token
# Create one at https://github.com/settings/tokens
# This helps avoid API rate limits
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {}
if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_TOKEN_HERE":
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

# Read CSV
df = pd.read_csv(input_csv)

# Prepare new columns
stars_list = []
watchers_list = []
forks_list = []
collaborators_list = []

for index, row in df.iterrows():
    repo_url = str(row.get("URL", "")).strip()

    print(f"Processing {index + 1}/{len(df)}: {repo_url}")

    if not repo_url or repo_url == "nan":
        stars_list.append(None)
        watchers_list.append(None)
        forks_list.append(None)
        # collaborators_list.append(None)
        continue

    try:
        # Remove trailing slash if present
        repo_url = repo_url.rstrip("/")

        # Extract owner and repository name
        # Example: https://github.com/ros2/rclcpp
        parts = repo_url.split("github.com/")[-1].split("/")

        if len(parts) < 2:
            stars_list.append(None)
            watchers_list.append(None)
            forks_list.append(None)
            #collaborators_list.append(None)
            continue

        owner = parts[0]
        repo = parts[1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve repository info: {response.status_code}")
            stars_list.append(None)
            watchers_list.append(None)
            forks_list.append(None)
            #collaborators_list.append(None)
            continue

        data = response.json()

        stars = data.get("stargazers_count")
        watchers = data.get("subscribers_count")
        forks = data.get("forks_count")

        # Collaborators endpoint
        # collab_url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"
        # collab_response = requests.get(collab_url, headers=headers)

        # if collab_response.status_code == 200:
        #     collaborators = len(collab_response.json())
        # elif collab_response.status_code == 404:
        #     collaborators = None
        # elif collab_response.status_code == 403:
        #     collaborators = None
        #     print("Collaborator information requires additional permissions.")
        # else:
        #     collaborators = None

        stars_list.append(stars)
        watchers_list.append(watchers)
        forks_list.append(forks)
        #collaborators_list.append(collaborators)

    except Exception as e:
        print(f"Error processing {repo_url}: {e}")
        stars_list.append(None)
        watchers_list.append(None)
        forks_list.append(None)
        #collaborators_list.append(None)

    # Avoid hitting GitHub rate limits
    time.sleep(0.5)

# Add new columns to dataframe
df["GitHub Stars"] = stars_list
df["GitHub Watchers"] = watchers_list
df["GitHub Forks"] = forks_list
# df["GitHub Collaborators"] = collaborators_list

# Save updated CSV
df.to_csv(output_csv, index=False)

print(f"Saved updated file to: {output_csv}")