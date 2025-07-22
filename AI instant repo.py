import os
import subprocess
import tkinter as tk
from tkinter import filedialog

# Add GitHub CLI path to current environment if not already available
os.environ["PATH"] += r";C:\Program Files\GitHub CLI"

def create_github_repo():
    # GUI folder picker
    root = tk.Tk()
    root.withdraw()
    print("📁 Please select the folder where your new GitHub repo should be created...")
    base_dir = filedialog.askdirectory(title="Select folder to create GitHub repo in")

    if not base_dir:
        print("❌ No folder selected. Exiting.")
        return

    # Prompt for repo info
    repo_name = input("📝 Repository name: ").strip()
    description = input("🗒️  Description: ").strip()
    visibility = input("🔐 Visibility [private/public]: ").strip().lower()
    language = input("🧠 Main language [python/node/java/etc]: ").strip().lower()
    license_type = input("📄 Add license? [mit/none]: ").strip().lower()

    if visibility not in ['private', 'public']:
        print("❌ Invalid visibility. Choose 'private' or 'public'.")
        return

    # Create folder
    folder_name = repo_name.replace(" ", "-")
    full_path = os.path.join(base_dir, folder_name)
    try:
        os.makedirs(full_path, exist_ok=True)
        os.chdir(full_path)
        print(f"✅ Folder created at: {full_path}")
    except Exception as e:
        print(f"❌ Failed to create folder: {e}")
        return

    # Write README.md
    with open("README.md", "w") as f:
        f.write(f"# {repo_name}\n\n{description}\n\n## Features\n- Feature 1\n- Feature 2\n\n## Installation\n```bash\n# install steps\n```\n\n## Usage\n```bash\n# usage instructions\n```\n")

    # Write LICENSE (MIT only)
    if license_type == "mit":
        from datetime import datetime
        year = datetime.now().year
        license_content = f"""MIT License

Copyright (c) {year} Pranav

Permission is hereby granted, free of charge, to any person obtaining a copy...
(You can paste full MIT license if needed)
"""
        with open("LICENSE", "w") as f:
            f.write(license_content)

    # Write CONTRIBUTING.md
    with open("CONTRIBUTING.md", "w") as f:
        f.write("# Contributing\n\nThanks for contributing! Please follow the steps below:\n\n1. Fork the repo\n2. Create a feature branch\n3. Make changes\n4. Commit and push\n5. Open a pull request")

    # Download .gitignore using GitHub CLI
    try:
        ignore_content = subprocess.run(
            ["gh", "api", f"/gitignore/templates/{language}", "--jq", ".source"],
            capture_output=True,
            text=True
        ).stdout
        with open(".gitignore", "w") as f:
            f.write(ignore_content)
    except:
        with open(".gitignore", "w") as f:
            f.write("# Default\n*.pyc\n__pycache__/\n.env")

    # Git operations
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return

    # Create GitHub repo
    try:
        subprocess.run([
            "gh", "repo", "create", folder_name,
            "--" + visibility,
            "--description", description,
            "--source=.", "--remote=origin", "--push"
        ], check=True)
        print(f"🚀 Repository '{folder_name}' created and pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub repo creation failed: {e}")

if __name__ == "__main__":
    create_github_repo()
