#!/usr/bin/env python3
"""
Script to automatically generate entries in CHANGELOG.md from Git commits.
Based on conventional commits to categorize changes.
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def get_current_version() -> str:
    """Reads the current version of the project from pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
        else:
            return "0.0.0"  # Default version if not found


def get_latest_tag() -> Optional[str]:
    """Gets the most recent tag from the Git repository."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.SubprocessError:
        return None


def get_commits_since_tag(tag: Optional[str]) -> List[str]:
    """Gets all commits since the specified tag."""
    cmd = ["git", "log", "--pretty=format:%s|%h|%an|%ad", "--date=short"]
    if tag:
        cmd.append(f"{tag}..HEAD")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def categorize_commits(commits: List[str]) -> Dict[str, List[str]]:
    """Categorizes commits following the conventional commits pattern."""
    categories = {
        "feat": {"title": "Added", "items": []},
        "fix": {"title": "Fixed", "items": []},
        "docs": {"title": "Documentation", "items": []},
        "style": {"title": "Style", "items": []},
        "refactor": {"title": "Refactoring", "items": []},
        "perf": {"title": "Performance", "items": []},
        "test": {"title": "Tests", "items": []},
        "build": {"title": "Build", "items": []},
        "ci": {"title": "CI", "items": []},
        "chore": {"title": "Maintenance", "items": []},
        "revert": {"title": "Reverted", "items": []},
        "security": {"title": "Security", "items": []},
        "other": {"title": "Others", "items": []},
    }

    for commit in commits:
        if not commit:
            continue

        parts = commit.split("|")
        if len(parts) < 2:
            continue

        message, hash_id = parts[0], parts[1]

        # Ignores merge commits
        if message.startswith("Merge"):
            continue

        # Extracts commit type (feat, fix, etc.)
        match = re.match(r"^(\w+)(\(.*\))?!?:", message)

        if match:
            commit_type = match.group(1)
            scope = match.group(2) if match.group(2) else ""

            # Removes parentheses from scope if it exists
            if scope:
                scope = scope[1:-1]  # Removes ( and )
                formatted_message = f"{message[match.end():].strip()} [{scope}]"
            else:
                formatted_message = message[match.end() :].strip()

            # Adds link to the commit
            entry = f"{formatted_message} ([{hash_id[:7]}](https://github.com/fsant0s/neuron/commit/{hash_id}))"

            if commit_type in categories:
                categories[commit_type]["items"].append(entry)
            else:
                categories["other"]["items"].append(entry)
        else:
            # Commits that don't follow the pattern
            entry = (
                f"{message} ([{hash_id[:7]}](https://github.com/fsant0s/neuron/commit/{hash_id}))"
            )
            categories["other"]["items"].append(entry)

    return categories


def generate_changelog_entry(version: str, categories: Dict[str, Dict]) -> str:
    """Generates the changelog entry for the specified version."""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [f"## [{version}] - {today}\n"]

    for category, data in categories.items():
        if data["items"]:
            lines.append(f"### {data['title']}")
            for item in data["items"]:
                lines.append(f"- {item}")
            lines.append("")  # Blank line

    return "\n".join(lines)


def update_changelog(new_entry: str) -> None:
    """Updates the CHANGELOG.md file with the new entry."""
    changelog_path = "CHANGELOG.md"

    if not os.path.exists(changelog_path):
        # Creates a new CHANGELOG file if it doesn't exist
        with open(changelog_path, "w") as f:
            f.write("# Changelog\n\n")
            f.write(
                "All notable changes to the NEURON project will be documented in this file.\n\n"
            )
            f.write(
                "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
            )
            f.write("and this project adheres to [Semantic Versioning](https://semver.org/).\n\n")
            f.write(new_entry)
        return

    with open(changelog_path, "r") as f:
        content = f.read()

    # Finds where to insert the new entry (after the header)
    unreleased_match = re.search(r"## \[Unreleased\]", content)
    if not unreleased_match:
        unreleased_match = re.search(r"## \[Não lançado\]", content)
    first_version_match = re.search(r"## \[\d+\.\d+\.\d+\]", content)

    if unreleased_match:
        # Inserts after the "Unreleased" section
        unreleased_section_end = content.find("\n\n", unreleased_match.end())
        if unreleased_section_end == -1:
            # If the end of the section is not found, use the beginning of the next version
            if first_version_match:
                insertion_point = first_version_match.start()
            else:
                insertion_point = len(content)
        else:
            insertion_point = unreleased_section_end + 2

        new_content = content[:insertion_point] + new_entry + "\n" + content[insertion_point:]
    elif first_version_match:
        # Inserts before the first version
        new_content = (
            content[: first_version_match.start()]
            + new_entry
            + "\n"
            + content[first_version_match.start() :]
        )
    else:
        # Adds to the end
        new_content = content + "\n" + new_entry

    with open(changelog_path, "w") as f:
        f.write(new_content)


def main() -> None:
    """Main function."""
    version = get_current_version()
    latest_tag = get_latest_tag()

    print(f"Generating changelog for version {version}...")
    if latest_tag:
        print(f"Commits since tag {latest_tag}")
    else:
        print("Analyzing all commits (no tag found)")

    commits = get_commits_since_tag(latest_tag)

    if not commits or (len(commits) == 1 and not commits[0]):
        print("No commits found to include in the changelog.")
        return

    categories = categorize_commits(commits)

    # Counts the total number of entries
    total_entries = sum(len(data["items"]) for data in categories.values())

    if total_entries == 0:
        print("No entries to add to the changelog.")
        return

    print(f"Found {total_entries} entries for the changelog.")

    changelog_entry = generate_changelog_entry(version, categories)
    update_changelog(changelog_entry)

    print(f"Changelog successfully updated for version {version}!")


if __name__ == "__main__":
    main()
