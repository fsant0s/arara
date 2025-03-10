#!/usr/bin/env python3
"""
Script to increment the project version following the Semantic Versioning standard.
Updates the version in the pyproject.toml file and optionally generates a Git tag.
"""

import argparse
import re
import subprocess
import sys
from typing import Tuple, Optional


def get_current_version() -> str:
    """Reads the current version of the project from pyproject.toml."""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
            else:
                print("Error: Could not find the version in the pyproject.toml file.")
                sys.exit(1)
    except FileNotFoundError:
        print("Error: The pyproject.toml file was not found.")
        sys.exit(1)


def bump_version(current_version: str, part: str) -> str:
    """
    Increments a specific part of the version.
    
    Args:
        current_version: The current version in the format x.y.z
        part: The part to increment ('major', 'minor', or 'patch')
    
    Returns:
        The new version
    """
    # Checks if the current version is in the correct format
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$", current_version)
    if not match:
        print(f"Error: Invalid version format: {current_version}")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups()[:3])
    prerelease = match.group(4)
    build = match.group(5)
    
    # Increments the specified part
    if part == "major":
        major += 1
        minor = 0
        patch = 0
        prerelease = None
    elif part == "minor":
        minor += 1
        patch = 0
        prerelease = None
    elif part == "patch":
        patch += 1
        prerelease = None
    elif part.startswith("pre"):
        # Increments the pre-release version (alpha, beta, rc, etc)
        pre_type = part[4:]  # alpha, beta, rc
        if not prerelease or not prerelease.startswith(pre_type):
            prerelease = f"{pre_type}.1"
        else:
            pre_parts = prerelease.split(".")
            if len(pre_parts) >= 2 and pre_parts[-1].isdigit():
                pre_num = int(pre_parts[-1]) + 1
                prerelease = f"{pre_type}.{pre_num}"
            else:
                prerelease = f"{pre_type}.1"
    else:
        print(f"Error: Invalid version part: {part}")
        print("Valid values: major, minor, patch, prealpha, prebeta, prerc")
        sys.exit(1)
    
    # Builds the new version
    new_version = f"{major}.{minor}.{patch}"
    if prerelease:
        new_version += f"-{prerelease}"
    if build:
        new_version += f"+{build}"
    
    return new_version


def update_version_in_files(new_version: str) -> None:
    """Updates the version in the pyproject.toml file."""
    # Updates pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        
        updated_content = re.sub(
            r'(version\s*=\s*)"[^"]+"',
            f'\\1"{new_version}"',
            content
        )
        
        with open("pyproject.toml", "w") as f:
            f.write(updated_content)
        
        print(f"pyproject.toml file updated with version {new_version}")
    except Exception as e:
        print(f"Error updating the version in the pyproject.toml file: {e}")
        sys.exit(1)


def create_git_tag(version: str) -> None:
    """Creates a Git tag for the version."""
    tag_name = f"v{version}"
    try:
        # Adds the modified files
        subprocess.run(["git", "add", "pyproject.toml"], check=True)
        
        # Creates the commit
        commit_message = f"release: bump version to {tag_name}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Creates the tag
        subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Version {version}"], check=True)
        
        print(f"Git tag {tag_name} created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating the Git tag: {e}")
        sys.exit(1)


def main() -> None:
    """Main function of the script."""
    parser = argparse.ArgumentParser(description="Increments the project version following Semantic Versioning.")
    parser.add_argument("part", choices=["major", "minor", "patch", "prealpha", "prebeta", "prerc"], 
                      help="Part of the version to increment")
    parser.add_argument("--no-git", action="store_true", 
                      help="Do not create a Git tag for the new version")
    parser.add_argument("--no-changelog", action="store_true",
                      help="Do not generate a changelog entry")
    
    args = parser.parse_args()
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    new_version = bump_version(current_version, args.part)
    print(f"New version: {new_version}")
    
    update_version_in_files(new_version)
    
    if not args.no_changelog:
        try:
            print("Generating changelog entry...")
            subprocess.run(["python", "scripts/generate_changelog.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not generate changelog entry: {e}")
    
    if not args.no_git:
        create_git_tag(new_version)
        print(f"To push the tag to the remote repository, run: git push origin v{new_version}")
    
    print(f"Version successfully updated to {new_version}!")


if __name__ == "__main__":
    main() 