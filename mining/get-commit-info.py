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

# input_csv = "ros_repository_github.csv"
input_csv = "./data/demographics/ros_repository_github_top10.csv"
# output_csv = "github_repository_activity.csv"
commits_output_csv = "./data/popularity/github_commits.csv"
issues_output_csv = "./data/popularity/github_issues.csv"
prs_output_csv = "./data/popularity/github_pull_requests.csv"

COMMITS_PER_REPO = 100
ISSUES_PER_REPO = 100
PRS_PER_REPO = 100

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
    repo = parts[1].replace(".git", "")

    return owner, repo


# def safe_request(url, params=None):
#     try:
#         response = requests.get(url, headers=headers, params=params)

#         if response.status_code == 403:
#             remaining = response.headers.get("X-RateLimit-Remaining")
#             reset_time = response.headers.get("X-RateLimit-Reset")

#             print(f"Rate limit reached. Remaining: {remaining}, Reset: {reset_time}")
#             return None

#         if response.status_code != 200:
#             print(f"Request failed: {url} -> {response.status_code}")
#             return None

#         return response

#     except Exception as e:
#         print(f"Request error for {url}: {e}")
#         return None

# def safe_request(url, params=None, timeout=30):
#     try:
#         response = requests.get(
#             url,
#             headers=headers,
#             params=params,
#             timeout=timeout
#         )

#         if response.status_code == 403:
#             remaining = response.headers.get("X-RateLimit-Remaining")
#             reset_time = response.headers.get("X-RateLimit-Reset")

#             print(f"Rate limit reached. Remaining: {remaining}, Reset: {reset_time}")
#             return None

#         if response.status_code != 200:
#             print(f"Request failed: {url} -> {response.status_code}")
#             return None

#         return response

#     except requests.exceptions.Timeout:
#         print(f"Timeout while requesting: {url}")
#         return None

#     except requests.exceptions.ConnectionError:
#         print(f"Connection error while requesting: {url}")
#         return None

#     except requests.exceptions.RequestException as e:
#         print(f"Request error for {url}: {e}")
#         return None
from datetime import datetime
import time
import requests


def safe_request(url, params=None, timeout=20):
    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )

            # Success
            if response.status_code == 200:
                return response

            # Rate limit reached
            if response.status_code in [403, 429]:
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset_time = response.headers.get("X-RateLimit-Reset")

                print(f"Rate limit reached. Remaining: {remaining}, Reset: {reset_time}")

                if reset_time:
                    reset_timestamp = int(reset_time)
                    current_timestamp = int(time.time())

                    sleep_seconds = max(reset_timestamp - current_timestamp + 5, 5)

                    reset_datetime = datetime.utcfromtimestamp(reset_timestamp)

                    print(f"Sleeping for {sleep_seconds} seconds until {reset_datetime} UTC...")
                    time.sleep(sleep_seconds)
                    continue

                else:
                    print("Sleeping for 60 seconds...")
                    time.sleep(60)
                    continue

            # Other errors
            print(f"Request failed: {url} -> {response.status_code}")
            return None

        except requests.exceptions.Timeout:
            print(f"Timeout while requesting: {url}")
            return None

        except requests.exceptions.ConnectionError:
            print(f"Connection error while requesting: {url}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            return None


def get_default_branch(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = safe_request(url)

    if response:
        return response.json().get("default_branch", "main")

    return "main"


def get_repo_tree(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}"
    params = {"recursive": 1}

    response = safe_request(url, params=params)

    if response:
        return response.json().get("tree", [])

    return []


# def get_file_content(owner, repo, path, branch):
#     url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

#     try:
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             return response.text
#     except Exception:
#         pass

#     return None

def get_file_content(owner, repo, path, branch, timeout=30):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout
        )

        if response.status_code == 200:
            return response.text

    except requests.exceptions.Timeout:
        print(f"Timeout downloading file: {url}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file {url}: {e}")

    return None


# def detect_dependencies(owner, repo):
#     dependency_files = [
#         "requirements.txt",
#         "package.json",
#         "pom.xml",
#         "build.gradle",
#         "Cargo.toml",
#         "go.mod",
#         "composer.json",
#         "Gemfile",
#         "environment.yml",
#         "setup.py",
#         "pyproject.toml",
#         "package.xml",
#         "CMakeLists.txt"
#     ]

#     default_branch = get_default_branch(owner, repo)
#     tree = get_repo_tree(owner, repo, default_branch)

#     dependencies = []

#     for item in tree:
#         path = item.get("path", "")

#         if any(path.endswith(dep_file) for dep_file in dependency_files):
#             #content = get_file_content(owner, repo, path, default_branch)
#             content = get_file_content(owner, repo, path, default_branch, timeout=10)

#             if content:
#                 shortened_content = content[:5000].replace("\n", " ")
#                 dependencies.append(f"{path}: {shortened_content}")

#     return "\n\n".join(dependencies)


def get_commits(owner, repo):
    commits = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {
            "per_page": per_page,
            "page": page
        }

        response = safe_request(url, params=params)

        if not response:
            break

        batch = response.json()

        if not batch:
            break

        commits.extend(batch)

        print(f"Collected {len(commits)} commits from {owner}/{repo}")

        # If fewer than per_page items were returned, it was the last page
        if len(batch) < per_page:
            break

        page += 1

    return commits


def get_commit_stats(owner, repo, sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    response = safe_request(url)

    if not response:
        return None, None, None

    data = response.json()
    stats = data.get("stats", {})

    additions = stats.get("additions")
    deletions = stats.get("deletions")
    total_changes = stats.get("total")

    return additions, deletions, total_changes


def get_issues(owner, repo, state="all"):
    issues = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page
        }

        response = safe_request(url, params=params)

        if not response:
            break

        batch = response.json()

        if not batch:
            break

        # Remove pull requests from issues endpoint
        batch = [item for item in batch if "pull_request" not in item]

        issues.extend(batch)

        print(f"Collected {len(issues)} issues from {owner}/{repo}")

        if len(batch) < per_page:
            break

        page += 1

    return issues


def get_pull_requests(owner, repo, state="all"):
    prs = []
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page
        }

        response = safe_request(url, params=params)

        if not response:
            break

        batch = response.json()

        if not batch:
            break

        prs.extend(batch)

        print(f"Collected {len(prs)} pull requests from {owner}/{repo}")

        if len(batch) < per_page:
            break

        page += 1

    return prs


# ==========================================================
# Main Script
# ==========================================================

df = pd.read_csv(input_csv)

# rows = []

commit_rows = []
issue_rows = []
pr_rows = []

for index, row in df.iterrows():
    repo_url = row.get("URL")

    owner, repo = extract_owner_repo(repo_url)

    if not owner or not repo:
        print(f"Skipping invalid URL: {repo_url}")
        continue

    print(f"[{index + 1}/{len(df)}] Processing {owner}/{repo}")

    try:
        # dependencies = detect_dependencies(owner, repo)

        commits = get_commits(owner, repo)
        issues = get_issues(owner, repo, state="all")
        pull_requests = get_pull_requests(owner, repo, state="all")

        # ==========================================================
        # Save Commits
        # ==========================================================

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

            # rows.append({
            #     "repository": f"{owner}/{repo}",
            #     "record_type": "commit",

            #     "commit_sha": sha,
            #     "commit_date": commit_date,
            #     "commit_title": title,
            #     "commit_message": message,
            #     "commit_author": author_name,
            #     "additions": additions,
            #     "deletions": deletions,
            #     "total_changes": total_changes,

            #     "issue_number": None,
            #     "issue_state": None,
            #     "issue_title": None,
            #     "issue_created_at": None,
            #     "issue_closed_at": None,
            #     "issue_author": None,
            #     "issue_comments": None,

            #     "pr_number": None,
            #     "pr_state": None,
            #     "pr_title": None,
            #     "pr_created_at": None,
            #     "pr_closed_at": None,
            #     "pr_merged_at": None,
            #     "pr_author": None,
            #     "pr_comments": None,

            #     # "dependencies": dependencies
            # })

            commit_rows.append({
                "repository": f"{owner}/{repo}",
                "commit_sha": sha,
                "commit_date": commit_date,
                "commit_title": title,
                "commit_message": message,
                "commit_author": author_name,
                "additions": additions,
                "deletions": deletions,
                "total_changes": total_changes
            })

        # ==========================================================
        # Save Issues
        # ==========================================================

        for issue in issues:

            issue_rows.append({
                "repository": f"{owner}/{repo}",
                "issue_number": issue.get("number"),
                "issue_state": issue.get("state"),
                "issue_title": issue.get("title"),
                "issue_created_at": issue.get("created_at"),
                "issue_closed_at": issue.get("closed_at"),
                "issue_author": issue.get("user", {}).get("login"),
                "issue_comments": issue.get("comments")
            })

        # ==========================================================
        # Save Pull Requests
        # ==========================================================

        for pr in pull_requests:
            pr_rows.append({
                "repository": f"{owner}/{repo}",
                "pr_number": pr.get("number"),
                "pr_state": pr.get("state"),
                "pr_title": pr.get("title"),
                "pr_created_at": pr.get("created_at"),
                "pr_closed_at": pr.get("closed_at"),
                "pr_merged_at": pr.get("merged_at"),
                "pr_author": pr.get("user", {}).get("login"),
                "pr_comments": pr.get("comments")
            })

        time.sleep(0.5)

    except Exception as e:
        print(f"Error processing {owner}/{repo}: {e}")

# ==========================================================
# Save Results
# ==========================================================

commit_columns = [
    "repository",
    "commit_sha",
    "commit_date",
    "commit_title",
    "commit_message",
    "commit_author",
    "additions",
    "deletions",
    "total_changes"
]

issue_columns = [
    "repository",
    "issue_number",
    "issue_state",
    "issue_title",
    "issue_created_at",
    "issue_closed_at",
    "issue_author",
    "issue_comments"
]

pr_columns = [
    "repository",
    "pr_number",
    "pr_state",
    "pr_title",
    "pr_created_at",
    "pr_closed_at",
    "pr_merged_at",
    "pr_author",
    "pr_comments"
]

commit_df = pd.DataFrame(commit_rows, columns=commit_columns)
issue_df = pd.DataFrame(issue_rows, columns=issue_columns)
pr_df = pd.DataFrame(pr_rows, columns=pr_columns)

commit_df.to_csv(commits_output_csv, index=False)
issue_df.to_csv(issues_output_csv, index=False)
pr_df.to_csv(prs_output_csv, index=False)

print(f"Saved commits to {commits_output_csv}")
print(f"Saved issues to {issues_output_csv}")
print(f"Saved pull requests to {prs_output_csv}")