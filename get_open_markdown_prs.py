import argparse
from datetime import datetime
import pytz
from github import Github

# Argument parsing
parser = argparse.ArgumentParser(description='Scan GitHub repositories for PRs.')
parser.add_argument('-s', '--since', required=True, help='Date to filter PRs (format: YYYY-MM-DD)')
parser.add_argument('-o', '--output', required=True, help='Output file path (with .tsv extension)')
parser.add_argument('-l', '--label', action='store_true', help='Filter PRs by "Ready for Review" label')
args = parser.parse_args()

# Convert string to timezone-aware datetime
since_date = datetime.strptime(args.since, '%Y-%m-%d')
since_date = pytz.utc.localize(since_date)

# List of GitHub repositories in the format 'username/repo'
repositories = ['username/repo1', 'username/repo2']

# Initialize PyGithub
g = Github()

# Function to get PRs with .md file changes since a given date
def get_md_prs(repo_name, since, label_filter=False):
    repo = g.get_repo(repo_name)
    prs = repo.get_pulls(state='open')
    md_prs = []

    for pr in prs:
        if pr.created_at < since:
            continue

        if label_filter and not any(label.name.lower() == "ready for review" for label in pr.get_labels()):
            continue

        files = pr.get_files()
        for file in files:
            if file.filename.endswith('.md'):
                pr_date = pr.created_at.strftime('%Y-%m-%d')
                md_prs.append(f"{repo_name}\t{file.filename}\t{pr.title}\t{pr.number}\t{pr.title}\t{pr_date}")
                break

    return md_prs

# Write to output file
with open(args.output, 'w') as file:
    file.write("Repo\tPath\tPR Title\tPR Number\tPR Title\tPR Date\n")
    for repo in repositories:
        md_prs = get_md_prs(repo, since_date, args.label)
        if md_prs:
            for pr_info in md_prs:
                file.write(pr_info + '\n')
        else:
            file.write(f"No PRs with .md file changes found in {repo} since {args.since}.\n")
