import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
from datetime import datetime
from google import generativeai as genai

# Add GitHub CLI path
os.environ["PATH"] += r";C:\Program Files\GitHub CLI"

# Configure API
genai.configure(api_key="AIzaSyAq6sB4h1pFHX4IL0IeRCtA7RE6_40gjXY")

class SingleClickRepoCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 One-Click AI GitHub Repo Creator")
        self.root.geometry("800x600")
        self.root.configure(bg='#0D1117')
        
        # Colors
        self.bg = '#0D1117'
        self.surface = '#21262D'  
        self.primary = '#238636'
        self.text = '#F0F6FC'
        self.secondary = '#8B949E'
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title = tk.Label(main, 
                        text="🤖 ONE-CLICK AI REPO CREATOR", 
                        font=('Arial', 24, 'bold'),
                        bg=self.bg, fg=self.text)
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(main,
                           text="Describe your idea → Get a complete GitHub repository",
                           font=('Arial', 12),
                           bg=self.bg, fg=self.secondary)
        subtitle.pack(pady=(0, 30))
        
        # Input area
        input_frame = tk.Frame(main, bg=self.surface, relief='flat', bd=0)
        input_frame.pack(fill='x', pady=(0, 20))
        
        input_label = tk.Label(input_frame,
                              text="💡 Describe your repository idea:",
                              font=('Arial', 14, 'bold'),
                              bg=self.surface, fg=self.text)
        input_label.pack(anchor='w', padx=20, pady=(15, 5))
        
        self.idea_entry = tk.Text(input_frame,
                                 height=4,
                                 font=('Arial', 11),
                                 bg='#161B22',
                                 fg=self.text,
                                 insertbackground=self.text,
                                 relief='flat',
                                 bd=0,
                                 padx=15,
                                 pady=10)
        self.idea_entry.pack(fill='x', padx=20, pady=(0, 15))
        self.idea_entry.insert('1.0', 'A Python web scraper for extracting product data from e-commerce sites...')
        
        # THE BIG BUTTON
        self.magic_button = tk.Button(main,
                                     text="✨ CREATE MY REPOSITORY ✨",
                                     font=('Arial', 16, 'bold'),
                                     bg=self.primary,
                                     fg='white',
                                     relief='flat',
                                     bd=0,
                                     padx=40,
                                     pady=15,
                                     cursor='hand2',
                                     command=self.create_magic)
        self.magic_button.pack(pady=20)
        
        # Status area
        status_frame = tk.Frame(main, bg=self.surface, relief='flat')
        status_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        status_label = tk.Label(status_frame,
                               text="📋 Status & Logs:",
                               font=('Arial', 12, 'bold'),
                               bg=self.surface, fg=self.text)
        status_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        self.log_area = scrolledtext.ScrolledText(status_frame,
                                                 height=15,
                                                 font=('Consolas', 9),
                                                 bg='#0D1117',
                                                 fg=self.text,
                                                 insertbackground=self.text,
                                                 relief='flat',
                                                 bd=0,
                                                 padx=10,
                                                 pady=10,
                                                 state='disabled')
        self.log_area.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Initial check
        self.log("🔍 Checking GitHub CLI authentication...")
        self.check_github_cli()
        
    def log(self, message):
        """Add message to log"""
        self.log_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert('end', f"[{timestamp}] {message}\n")
        self.log_area.see('end')
        self.log_area.config(state='disabled')
        self.root.update_idletasks()
        
    def check_github_cli(self):
        """Check GitHub CLI in background"""
        def check():
            try:
                subprocess.run(["gh", "--version"], check=True, capture_output=True)
                subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
                self.log("✅ GitHub CLI ready!")
            except:
                self.log("❌ GitHub CLI not ready. Please run 'gh auth login'")
        
        threading.Thread(target=check, daemon=True).start()
        
    def run_command(self, cmd, cwd=None, capture_output=True):
        """Helper to run commands with better error handling"""
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, 
                                  text=True, check=True)
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except Exception as e:
            return False, "", str(e)
        
    def create_magic(self):
        """The magic single-click function"""
        idea = self.idea_entry.get('1.0', 'end-1c').strip()
        if not idea or idea == 'A Python web scraper for extracting product data from e-commerce sites...':
            messagebox.showwarning("Input Needed", "Please describe your repository idea!")
            return
            
        # Disable button
        self.magic_button.config(text="🔄 CREATING MAGIC...", state='disabled', bg='#6F42C1')
        
        def magic_process():
            original_cwd = os.getcwd()
            try:
                # Step 1: Get folder
                self.log("📁 Please select where to create your repository...")
                self.root.update()
                
                folder = filedialog.askdirectory(title="Select folder for your new repository")
                if not folder:
                    self.log("❌ No folder selected. Cancelling.")
                    return
                    
                self.log(f"✅ Selected: {folder}")
                
                # Step 2: AI Generation
                self.log("🧠 Generating repository with AI...")
                ai_data = self.generate_with_ai(idea)
                if not ai_data:
                    return
                    
                # Step 3: Create files
                repo_name = ai_data.get('repo_name', 'AIRepo')
                # Clean repo name - remove invalid characters
                repo_name = ''.join(c if c.isalnum() or c in '-_' else '-' for c in repo_name)
                repo_name = repo_name.strip('-_')
                if not repo_name:
                    repo_name = 'AIRepo'
                    
                repo_path = os.path.join(folder, repo_name)
                
                self.log(f"📂 Creating repository: {repo_name}")
                os.makedirs(repo_path, exist_ok=True)
                
                # Create all files
                self.create_files(repo_path, ai_data)
                
                # Step 4: Git setup with better error handling
                self.log("🔧 Setting up Git...")
                
                # Initialize git
                success, stdout, stderr = self.run_command(["git", "init"], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git init failed: {stderr}")
                    return
                
                # Configure git user if not set
                success, _, _ = self.run_command(["git", "config", "user.name"], cwd=repo_path)
                if not success:
                    self.log("🔧 Setting up Git user config...")
                    self.run_command(["git", "config", "user.name", "AI Repo Creator"], cwd=repo_path)
                    self.run_command(["git", "config", "user.email", "ai@example.com"], cwd=repo_path)
                
                # Add files
                success, stdout, stderr = self.run_command(["git", "add", "."], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git add failed: {stderr}")
                    return
                
                # Check if there are files to commit
                success, stdout, stderr = self.run_command(["git", "status", "--porcelain"], cwd=repo_path)
                if not success or not stdout.strip():
                    self.log("❌ No files to commit!")
                    return
                
                # Commit
                commit_msg = "✨ Initial commit - Created with AI"
                success, stdout, stderr = self.run_command(
                    ["git", "commit", "-m", commit_msg], cwd=repo_path
                )
                if not success:
                    self.log(f"❌ Git commit failed: {stderr}")
                    return
                
                self.log("✅ Git repository initialized and committed!")
                
                # Step 5: Create GitHub repository
                self.log("🚀 Creating GitHub repository...")
                desc = ai_data.get('description', 'AI-generated repository')
                
                success, stdout, stderr = self.run_command([
                    "gh", "repo", "create", repo_name,
                    "--public", "--description", desc,
                    "--source=.", "--remote=origin", "--push"
                ], cwd=repo_path)
                
                if not success:
                    self.log(f"❌ GitHub creation failed: {stderr}")
                    # Try to get more details
                    if "already exists" in stderr:
                        self.log("💡 Repository name already exists. Try with a different name.")
                    return
                
                # Success!
                username = self.get_username()
                repo_url = f"https://github.com/{username}/{repo_name}"
                
                self.log("🎉 SUCCESS! Repository created!")
                self.log(f"🌐 GitHub: {repo_url}")
                self.log(f"📍 Local: {repo_path}")
                
                # Show success popup
                result = messagebox.askyesno("🎉 SUCCESS!", 
                                           f"Repository '{repo_name}' created!\n\n"
                                           f"GitHub: {repo_url}\n"
                                           f"Local: {repo_path}\n\n"
                                           "Open in browser?")
                if result:
                    import webbrowser
                    webbrowser.open(repo_url)
                    
            except Exception as e:
                self.log(f"❌ Unexpected error: {str(e)}")
                messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")
            finally:
                # Restore original directory
                os.chdir(original_cwd)
                self.magic_button.config(text="✨ CREATE MY REPOSITORY ✨", 
                                       state='normal', bg=self.primary)
        
        threading.Thread(target=magic_process, daemon=True).start()
        
    def generate_with_ai(self, idea):
        """Generate repo data with AI"""
        try:
            prompt = f"""
            Create a GitHub repository for: {idea}
            
            Return ONLY valid JSON with:
            - "repo_name": name with hyphens, no spaces, alphanumeric only
            - "description": brief description  
            - "readme": complete README.md content
            - "gitignore": .gitignore content
            - "license_text": MIT license text
            - "requirements": requirements.txt if needed (can be empty string)
            
            NO code blocks, NO explanations, ONLY JSON.
            """
            
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            response = model.generate_content(prompt)
            raw = response.text.strip()
            
            # Clean response
            if raw.startswith("```"):
                lines = raw.split('\n')
                # Find the first line that doesn't start with ``` or contain 'json'
                start_idx = 0
                for i, line in enumerate(lines):
                    if not line.strip().startswith('```') and 'json' not in line.lower():
                        start_idx = i
                        break
                # Find the last line that doesn't start with ```
                end_idx = len(lines)
                for i in range(len(lines)-1, -1, -1):
                    if not lines[i].strip().startswith('```'):
                        end_idx = i + 1
                        break
                raw = '\n'.join(lines[start_idx:end_idx])
                    
            data = json.loads(raw)
            self.log("✅ AI generation completed!")
            return data
            
        except json.JSONDecodeError as e:
            self.log(f"❌ Invalid JSON from AI: {str(e)}")
            self.log(f"Raw response: {raw[:200]}...")
            return None
        except Exception as e:
            self.log(f"❌ AI generation failed: {str(e)}")
            return None
            
    def create_files(self, repo_path, data):
        """Create all repository files"""
        files = {
            'readme': 'README.md',
            'gitignore': '.gitignore', 
            'license_text': 'LICENSE',
            'requirements': 'requirements.txt'
        }
        
        for key, filename in files.items():
            content = data.get(key, '')
            if content and content.strip():  # Only create non-empty files
                try:
                    with open(os.path.join(repo_path, filename), 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.log(f"✅ Created: {filename}")
                except Exception as e:
                    self.log(f"❌ Failed to create {filename}: {str(e)}")
                
    def get_username(self):
        """Get GitHub username"""
        try:
            success, stdout, stderr = self.run_command(["gh", "api", "user", "--jq", ".login"])
            if success:
                return stdout.strip()
            else:
                self.log(f"Warning: Could not get username: {stderr}")
                return "user"
        except:
            return "user"
            
    def run(self):
        self.root.mainloop()

# Run the app
if __name__ == "__main__":
    app = SingleClickRepoCreator()
    app.run()