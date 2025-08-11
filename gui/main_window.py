import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from datetime import datetime

from ai.generator import generate_with_ai
from file_manager.github_utils import check_github_cli, run_command, get_username
from file_manager.creator import create_files

os.environ["PATH"] += r";C:\Program Files\GitHub CLI"

class SingleClickRepoCreator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 One-Click AI GitHub Repo Creator")
        self.root.geometry("800x600")
        self.root.configure(bg='#0D1117')
        
        self.bg = '#0D1117'
        self.surface = '#21262D'  
        self.primary = '#238636'
        self.text = '#F0F6FC'
        self.secondary = '#8B949E'
        
        self.setup_ui()
        
    def setup_ui(self):
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill='both', expand=True, padx=30, pady=30)
        
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
        
        self.log("🔍 Checking GitHub CLI authentication...")
        check_github_cli(self.log)
        
    def log(self, message):
        self.log_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert('end', f"[{timestamp}] {message}\n")
        self.log_area.see('end')
        self.log_area.config(state='disabled')
        self.root.update_idletasks()
        
    def create_magic(self):
        idea = self.idea_entry.get('1.0', 'end-1c').strip()
        if not idea or idea == 'A Python web scraper for extracting product data from e-commerce sites...':
            messagebox.showwarning("Input Needed", "Please describe your repository idea!")
            return
            
        self.magic_button.config(text="🔄 CREATING MAGIC...", state='disabled', bg='#6F42C1')
        
        def magic_process():
            original_cwd = os.getcwd()
            try:
                self.log("📁 Please select where to create your repository...")
                self.root.update()
                
                folder = filedialog.askdirectory(title="Select folder for your new repository")
                if not folder:
                    self.log("❌ No folder selected. Cancelling.")
                    return
                    
                self.log(f"✅ Selected: {folder}")
                
                self.log("🧠 Generating repository with AI...")
                ai_data = generate_with_ai(idea, self.log)
                if not ai_data:
                    return
                    
                repo_name = ai_data.get('repo_name', 'AIRepo')
                repo_name = ''.join(c if c.isalnum() or c in '-_' else '-' for c in repo_name)
                repo_name = repo_name.strip('-_')
                if not repo_name:
                    repo_name = 'AIRepo'
                    
                repo_path = os.path.join(folder, repo_name)
                
                self.log(f"📂 Creating repository: {repo_name}")
                os.makedirs(repo_path, exist_ok=True)
                
                create_files(repo_path, ai_data, self.log)
                
                self.log("🔧 Setting up Git...")
                
                success, _, stderr = run_command(["git", "init"], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git init failed: {stderr}")
                    return
                
                success, _, _ = run_command(["git", "config", "user.name"], cwd=repo_path)
                if not success:
                    self.log("🔧 Setting up Git user config...")
                    run_command(["git", "config", "user.name", "AI Repo Creator"], cwd=repo_path)
                    run_command(["git", "config", "user.email", "ai@example.com"], cwd=repo_path)
                
                success, _, stderr = run_command(["git", "add", "."], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git add failed: {stderr}")
                    return
                
                success, stdout, _ = run_command(["git", "status", "--porcelain"], cwd=repo_path)
                if not success or not stdout.strip():
                    self.log("❌ No files to commit!")
                    return
                
                commit_msg = "✨ Initial commit - Created with AI"
                success, _, stderr = run_command(["git", "commit", "-m", commit_msg], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git commit failed: {stderr}")
                    return
                
                self.log("✅ Git repository initialized and committed!")
                
                self.log("🚀 Creating GitHub repository...")
                desc = ai_data.get('description', 'AI-generated repository')
                
                success, _, stderr = run_command([
                    "gh", "repo", "create", repo_name,
                    "--public", "--description", desc,
                    "--source=.", "--remote=origin", "--push"
                ], cwd=repo_path)
                
                if not success:
                    self.log(f"❌ GitHub creation failed: {stderr}")
                    if "already exists" in stderr:
                        self.log("💡 Repository name already exists. Try with a different name.")
                    return
                
                username = get_username()
                repo_url = f"https://github.com/{username}/{repo_name}"
                
                self.log("🎉 SUCCESS! Repository created!")
                self.log(f"🌐 GitHub: {repo_url}")
                self.log(f"📍 Local: {repo_path}")
                
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
                os.chdir(original_cwd)
                self.magic_button.config(text="✨ CREATE MY REPOSITORY ✨", 
                                       state='normal', bg=self.primary)
        
        threading.Thread(target=magic_process, daemon=True).start()
        
    def run(self):
        self.root.mainloop()
