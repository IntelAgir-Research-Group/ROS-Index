import os
import time
import requests
import pandas as pd

# ==========================================================
# Configuration
# ==========================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

input_csv = "ros_repository_urls.csv"
output_commits_csv = "github_commits_and_dependencies.csv"

# Number of commits to retrieve per repository
COMMITS_PER_REPO = 100

# ==========================================================
# Helper Functions
# ==========================================================

def extract_owner_repo(repo_url):
    if pd.isna(repo_url):
        return None, None

    repo_url = str(repo_url).strip().rstrip("/")

    if "github.com/" not in repo_url:
        return None, None

    parts = repo_url.split("github.com/")[-1].split("/")

    if len(parts) < 2:
        return None, None

    owner = parts[0]
    repo = parts[1]

    # Remove .git if present
    repo = repo.replace(".git", "")

    return owner, repo


def get_default_branch(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("default_branch", "main")

    return "main"


def get_commits(owner, repo, per_page=100):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {
        "per_page": per_page
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to get commits for {owner}/{repo}: {response.status_code}")
        return []

    return response.json()


def get_file_content(owner, repo, path, branch):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text

    return None


def detect_dependencies(owner, repo):
    dependencies = []

    default_branch = get_default_branch(owner, repo)

    dependency_files = [
        "requirements.txt",
        "package.json",
        "pom.xml",
        "build.gradle",
        "Cargo.toml",
        "go.mod",
        "composer.json",
        "Gemfile",
        "environment.yml",
        "setup.py",
        "pyproject.toml",
        "package.xml",
        "CMakeLists.txt"
    ]

    for dep_file in dependency_files:
        content = get_file_content(owner, repo, dep_file, default_branch)

        if content:
            dependencies.append(f"{dep_file}: {content[:5000]}")

    return "\n\n".join(dependencies)

def get_commit_stats(owner, repo, sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None, None, None

    data = response.json()
    stats = data.get("stats", {})

    additions = stats.get("additions")
    deletions = stats.get("deletions")
    total_changes = stats.get("total")

    return additions, deletions, total_changes


# ==========================================================
# Main Script
# ==========================================================

df = pd.read_csv(input_csv)

rows = []

for index, row in df.iterrows():
    repo_url = row.get("URL", None)

    owner, repo = extract_owner_repo(repo_url)

    if not owner or not repo:
        continue

    print(f"[{index + 1}/{len(df)}] Processing {owner}/{repo}")

    try:
        commits = get_commits(owner, repo, COMMITS_PER_REPO)
        dependencies = detect_dependencies(owner, repo)

        for commit in commits:
            commit_data = commit.get("commit", {})

            commit_date = None

            if commit_data.get("author"):
                commit_date = commit_data["author"].get("date")

            full_message = commit_data.get("message", "")
            title = full_message.split("\n")[0] if full_message else ""
            message = "\n".join(full_message.split("\n")[1:]).strip()

            author_name = None

            if commit.get("author"):
                author_name = commit["author"].get("login")
            elif commit_data.get("author"):
                author_name = commit_data["author"].get("name")

            sha = commit.get("sha")
            additions, deletions, total_changes = get_commit_stats(owner, repo, sha)

            rows.append({
                "repository": f"{owner}/{repo}",
                "commit_sha": commit.get("sha"),
                "commit_date": commit_date,
                "commit_title": title,
                "commit_message": message,
                "author": author_name,
                "additions": additions,
                "deletions": deletions,
                "total_changes": total_changes,
                "dependencies": dependencies
            })

        time.sleep(0.2)

    except Exception as e:
        print(f"Error processing {owner}/{repo}: {e}")

output_df = pd.DataFrame(rows)
output_df.to_csv(output_commits_csv, index=False)

print(f"Saved results to {output_commits_csv}")