import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from google import generativeai as genai

# Add GitHub CLI path to current environment if not already available
os.environ["PATH"] += r";C:\Program Files\GitHub CLI"

# --- YOUR API KEY (keep as-is) ---
genai.configure(api_key="AIzaSyAq6sB4h1pFHX4IL0IeRCtA7RE6_40gjXY")  # ✅ your real key goes here

def get_ai_generated_repo_data(user_input):
    """Generate repository metadata using Gemini AI"""
    prompt = f"""
    Create a public GitHub repo for this idea: {{{user_input}}}

    Return only a clean JSON object with these keys:
    - "repo_name": repository name (no spaces, use hyphens)
    - "description": brief description
    - "license": license type (mit/apache-2.0/gpl-3.0/none)
    - "language": main programming language
    - "readme": full README.md content
    - "gitignore": .gitignore content
    - "requirements": requirements.txt content (if applicable)
    - "license_text": full license text content
    - "contributing": CONTRIBUTING.md content

    ⚠️ DO NOT return code files like main.py or app.py.
    ⚠️ NO markdown code blocks, NO explanation — ONLY a valid JSON.
    """

    print("⏳ Contacting Gemini 2.5 flash Lite...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        print("✅ Gemini responded.")
        
        # Clean response if wrapped in code blocks
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").split("\n", 1)[-1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
        
        return json.loads(raw_text)
    except Exception as e:
        print("❌ Gemini API error:", e)
        return None

def create_local_files(data, repo_dir):
    """Create local files from AI-generated data"""
    # File mapping for proper extensions
    FILE_MAPPING = {
        "readme": "README.md",
        "gitignore": ".gitignore", 
        "requirements": "requirements.txt",
        "license_text": "LICENSE",
        "contributing": "CONTRIBUTING.md"
    }
    
    SKIP_KEYS = {"repo_name", "description", "license", "language"}
    
    created_files = []
    for key, content in data.items():
        if key in SKIP_KEYS or not content:
            continue
            
        filename = FILE_MAPPING.get(key.lower(), f"{key}.txt")
        filepath = os.path.join(repo_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(filename)
            print(f"📄 Created: {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    return created_files

def setup_git_and_github(repo_dir, data):
    """Initialize git and create GitHub repository"""
    repo_name = data.get("repo_name", "UntitledRepo")
    description = data.get("description", "AI-generated repository")
    
    try:
        # Change to repository directory
        os.chdir(repo_dir)
        print(f"📂 Working in: {repo_dir}")
        
        # Initialize git repository
        print("🔧 Initializing Git repository...")
        subprocess.run(["git", "init"], check=True, capture_output=True)
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        
        # Initial commit
        subprocess.run(["git", "commit", "-m", "Initial commit - AI generated"], check=True, capture_output=True)
        print("✅ Git repository initialized and files committed.")
        
        # Create GitHub repository
        print("🚀 Creating GitHub repository...")
        github_cmd = [
            "gh", "repo", "create", repo_name,
            "--public",  # Default to public as per AI generation
            "--description", description,
            "--source=.", "--remote=origin", "--push"
        ]
        
        result = subprocess.run(github_cmd, check=True, capture_output=True, text=True)
        print(f"✅ GitHub repository '{repo_name}' created and pushed successfully!")
        print(f"🌐 Repository URL: https://github.com/{get_github_username()}/{repo_name}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"❌ Git/GitHub operation failed: {error_msg}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_github_username():
    """Get current GitHub username"""
    try:
        result = subprocess.run(["gh", "api", "user", "--jq", ".login"], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return "your-username"  # fallback

def validate_github_cli():
    """Check if GitHub CLI is installed and authenticated"""
    try:
        # Check if gh is available
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        
        # Check if authenticated
        result = subprocess.run(["gh", "auth", "status"], check=True, capture_output=True, text=True)
        print("✅ GitHub CLI is authenticated and ready.")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI is not authenticated. Please run 'gh auth login' first.")
        return False
    except FileNotFoundError:
        print("❌ GitHub CLI is not installed. Please install it from https://cli.github.com/")
        return False

def main():
    """Main function that orchestrates the entire process"""
    print("🤖 AI-Powered GitHub Repository Creator")
    print("=" * 50)
    
    # Validate prerequisites
    if not validate_github_cli():
        input("Press Enter to exit...")
        return
    
    # Step 1: Get user input
    user_input = input("📌 Describe your repository idea:\n").strip()
    if not user_input:
        print("❌ Empty input. Exiting.")
        return
    
    # Step 2: Generate AI data
    print("\n🧠 Generating repository structure with AI...")
    ai_data = get_ai_generated_repo_data(user_input)
    if not ai_data:
        print("❌ Failed to generate AI data. Exiting.")
        return
    
    print("✅ AI generation completed.")
    print(f"📛 Generated repo name: {ai_data.get('repo_name', 'Unknown')}")
    print(f"📝 Description: {ai_data.get('description', 'No description')}")
    
    # Step 3: Folder selection
    print("\n📁 Select folder to create the repository...")
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        base_folder = filedialog.askdirectory(title="Select folder to create GitHub repo in")
        root.destroy()
        
        if not base_folder:
            print("❌ No folder selected. Exiting.")
            return
    except Exception as e:
        print(f"❌ Folder selection failed: {e}")
        return
    
    # Step 4: Create repository directory
    repo_name = ai_data.get("repo_name", "UntitledRepo")
    repo_dir = os.path.join(base_folder, repo_name)
    
    try:
        os.makedirs(repo_dir, exist_ok=True)
        print(f"📂 Repository directory created: {repo_dir}")
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return
    
    # Step 5: Create local files
    print("\n📄 Creating repository files...")
    created_files = create_local_files(ai_data, repo_dir)
    
    if not created_files:
        print("❌ No files were created. Exiting.")
        return
    
    # Step 6: Setup Git and GitHub
    print("\n🔧 Setting up Git and creating GitHub repository...")
    success = setup_git_and_github(repo_dir, ai_data)
    
    # Step 7: Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Your AI-generated repository is ready!")
        print(f"📍 Local path: {repo_dir}")
        print(f"🌐 GitHub repo: https://github.com/{get_github_username()}/{repo_name}")
        print(f"📄 Created files: {', '.join(created_files)}")
    else:
        print("⚠️  Repository files created locally, but GitHub upload failed.")
        print(f"📍 Local path: {repo_dir}")
        print("💡 You can manually push to GitHub later using: git push origin main")
    
    print("\n✨ Thank you for using AI Repository Creator!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()