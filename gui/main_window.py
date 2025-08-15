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
        self.root.geometry("900x700")
        self.root.configure(bg='#0A0E1A')
        self.root.resizable(True, True)
        
        # Enhanced color scheme
        self.bg = '#0A0E1A'           # Deeper dark blue
        self.surface = '#1A1F2E'      # Dark surface with blue tint
        self.card = '#252B3D'         # Card background
        self.primary = '#00D4FF'      # Cyan accent
        self.secondary = '#7C3AED'    # Purple accent
        self.success = '#10B981'      # Green success
        self.text = '#F8FAFC'         # White text
        self.text_secondary = '#94A3B8'  # Light gray
        self.accent = '#F59E0B'       # Amber accent
        self.border = '#334155'       # Border color
        
        # Configure custom styles
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Setup custom ttk styles for modern look"""
        style = ttk.Style()
        
        # Configure button style
        style.configure('Modern.TButton',
                       background=self.primary,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 15))
        
        style.map('Modern.TButton',
                 background=[('active', '#00B8E6'), ('pressed', '#0099CC')])
        
    def create_gradient_frame(self, parent, color1, color2, width, height):
        """Create a gradient effect frame (simulated with alternating colors)"""
        frame = tk.Frame(parent, bg=color1, width=width, height=height)
        return frame
        
    def create_modern_entry(self, parent, placeholder="", height=1, **kwargs):
        """Create a modern styled entry with border effects"""
        container = tk.Frame(parent, bg=self.card, highlightbackground=self.border, 
                       highlightthickness=1, relief='flat')
    
        if height > 1:
        # Don't hardcode wrap='word', let it come from kwargs if provided
            entry = tk.Text(container, height=height, **kwargs)
        else:
            entry = tk.Entry(container, **kwargs)
        
        entry.pack(padx=2, pady=2, fill='both', expand=True)
        return container, entry
        
    def setup_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.bg)
        main_container.pack(fill='both', expand=True)
        
        # Header section with gradient effect
        header_frame = tk.Frame(main_container, bg=self.surface, height=120)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Add subtle border line at top
        top_accent = tk.Frame(header_frame, bg=self.primary, height=3)
        top_accent.pack(fill='x')
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.surface)
        header_content.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Title with enhanced styling
        title_frame = tk.Frame(header_content, bg=self.surface)
        title_frame.pack()
        
        title = tk.Label(title_frame, 
                        text="🤖 AI REPOSITORY CREATOR", 
                        font=('Segoe UI', 28, 'bold'),
                        bg=self.surface, fg=self.primary)
        title.pack()
        
        # Add version/status indicator
        version_label = tk.Label(title_frame,
                               text="v2.0 • Production Ready",
                               font=('Segoe UI', 10),
                               bg=self.surface, fg=self.accent)
        version_label.pack(pady=(5, 0))
        
        subtitle = tk.Label(header_content,
                           text="Transform ideas into complete GitHub repositories with AI intelligence",
                           font=('Segoe UI', 14),
                           bg=self.surface, fg=self.text_secondary)
        subtitle.pack(pady=(10, 0))
        
        # Main content area
        main = tk.Frame(main_container, bg=self.bg)
        main.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Input section with modern card design
        input_card = tk.Frame(main, bg=self.card, relief='flat', bd=0)
        input_card.pack(fill='x', pady=(0, 25))
        
        # Add subtle top border to card
        card_accent = tk.Frame(input_card, bg=self.secondary, height=2)
        card_accent.pack(fill='x')
        
        input_content = tk.Frame(input_card, bg=self.card)
        input_content.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Input label with icon
        label_frame = tk.Frame(input_content, bg=self.card)
        label_frame.pack(fill='x', pady=(0, 15))
        
        input_label = tk.Label(label_frame,
                              text="💡 Repository Concept",
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.card, fg=self.text,
                              anchor='w')
        input_label.pack(side='left')
        
        # Status indicator
        self.input_status = tk.Label(label_frame,
                                   text="● Ready",
                                   font=('Segoe UI', 12),
                                   bg=self.card, fg=self.success)
        self.input_status.pack(side='right')
        
        help_text = tk.Label(input_content,
                           text="Describe your project idea in detail. Be specific about functionality, tech stack, and goals.",
                           font=('Segoe UI', 11),
                           bg=self.card, fg=self.text_secondary,
                           anchor='w')
        help_text.pack(fill='x', pady=(0, 10))
        
        # Modern text input with border effect
        text_container, self.idea_entry = self.create_modern_entry(
            input_content,
            height=5,
            font=('Segoe UI', 12),
            bg='#1E293B',
            fg=self.text,
            insertbackground=self.primary,
            relief='flat',
            bd=0,
            padx=15,
            pady=12,
            selectbackground=self.secondary,
            wrap='word'
        )
        text_container.pack(fill='x', pady=(0, 10))
        
        self.idea_entry.insert('1.0', 'A Python web scraper for extracting product data from e-commerce sites...')
        
        # Bind events for input validation feedback
        self.idea_entry.bind('<KeyRelease>', self.on_text_change)
        self.idea_entry.bind('<FocusIn>', lambda e: self.update_input_status("● Editing", self.accent))
        self.idea_entry.bind('<FocusOut>', lambda e: self.update_input_status("● Ready", self.success))
        
        # Enhanced magic button with hover effects
        button_frame = tk.Frame(main, bg=self.bg)
        button_frame.pack(pady=20)
        
        # Button container for shadow effect
        button_container = tk.Frame(button_frame, bg=self.bg, highlightthickness=0)
        button_container.pack()
        
        self.magic_button = tk.Button(button_container,
                                     text="⚡ CREATE REPOSITORY",
                                     font=('Segoe UI', 18, 'bold'),
                                     bg=self.primary,
                                     fg='white',
                                     relief='flat',
                                     bd=0,
                                     padx=50,
                                     pady=18,
                                     cursor='hand2',
                                     command=self.create_magic)
        self.magic_button.pack()
        
        # Add button hover effects
        self.magic_button.bind('<Enter>', self.on_button_enter)
        self.magic_button.bind('<Leave>', self.on_button_leave)
        
        # Status section with enhanced design
        status_card = tk.Frame(main, bg=self.card, relief='flat')
        status_card.pack(fill='both', expand=True, pady=(15, 0))
        
        # Status header with accent
        status_header = tk.Frame(status_card, bg=self.secondary, height=3)
        status_header.pack(fill='x')
        
        status_content = tk.Frame(status_card, bg=self.card)
        status_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Status header with controls
        header_row = tk.Frame(status_content, bg=self.card)
        header_row.pack(fill='x', pady=(0, 10))
        
        status_label = tk.Label(header_row,
                               text="📊 System Status & Logs",
                               font=('Segoe UI', 14, 'bold'),
                               bg=self.card, fg=self.text)
        status_label.pack(side='left')
        
        # Add clear button
        clear_btn = tk.Button(header_row,
                            text="Clear",
                            font=('Segoe UI', 10),
                            bg=self.surface,
                            fg=self.text_secondary,
                            relief='flat',
                            bd=0,
                            padx=15,
                            pady=5,
                            cursor='hand2',
                            command=self.clear_logs)
        clear_btn.pack(side='right')
        
        # Enhanced log area with custom scrollbar
        log_frame = tk.Frame(status_content, bg=self.card)
        log_frame.pack(fill='both', expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame,
                                                 height=12,
                                                 font=('JetBrains Mono', 10),
                                                 bg='#0F172A',
                                                 fg=self.text,
                                                 insertbackground=self.primary,
                                                 relief='flat',
                                                 bd=0,
                                                 padx=15,
                                                 pady=12,
                                                 state='disabled',
                                                 selectbackground=self.secondary,
                                                 wrap='word')
        self.log_area.pack(fill='both', expand=True)
        
        # Configure text tags for colored output
        self.log_area.tag_configure("success", foreground=self.success)
        self.log_area.tag_configure("error", foreground="#EF4444")
        self.log_area.tag_configure("warning", foreground=self.accent)
        self.log_area.tag_configure("info", foreground=self.primary)
        self.log_area.tag_configure("timestamp", foreground=self.text_secondary)
        
        # Footer with system info
        footer = tk.Frame(main_container, bg=self.surface, height=40)
        footer.pack(fill='x')
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.surface)
        footer_content.pack(expand=True, fill='both', padx=30, pady=10)
        
        sys_info = tk.Label(footer_content,
                          text="GitHub CLI Integration • Gemini AI • Git Version Control",
                          font=('Segoe UI', 10),
                          bg=self.surface, fg=self.text_secondary)
        sys_info.pack(side='left')
        
        self.connection_status = tk.Label(footer_content,
                                        text="🔍 Checking connections...",
                                        font=('Segoe UI', 10),
                                        bg=self.surface, fg=self.text_secondary)
        self.connection_status.pack(side='right')
        
        # Initial system check
        self.log("🔍 Initializing system components...", "info")
        self.check_systems()
        
    def on_text_change(self, event):
        """Handle text input changes"""
        content = self.idea_entry.get('1.0', 'end-1c').strip()
        if len(content) > 20:
            self.update_input_status("● Valid", self.success)
        else:
            self.update_input_status("● Too short", "#EF4444")
            
    def update_input_status(self, text, color):
        """Update input status indicator"""
        self.input_status.config(text=text, fg=color)
        
    def on_button_enter(self, event):
        """Button hover enter effect"""
        self.magic_button.config(bg='#00B8E6', relief='raised', bd=2)
        
    def on_button_leave(self, event):
        """Button hover leave effect"""
        self.magic_button.config(bg=self.primary, relief='flat', bd=0)
        
    def clear_logs(self):
        """Clear the log area"""
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        
    def check_systems(self):
        """Enhanced system checks with better status updates"""
        def check():
            try:
                check_github_cli(self.log)
                self.connection_status.config(text="✅ All systems ready", fg=self.success)
            except Exception as e:
                self.connection_status.config(text="⚠️ System issues detected", fg=self.accent)
                
        threading.Thread(target=check, daemon=True).start()
        
    def log(self, message, tag="info"):
        """Enhanced logging with colored output and better formatting"""
        self.log_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert timestamp
        self.log_area.insert('end', f"[{timestamp}] ", "timestamp")
        
        # Insert message with appropriate tag
        if "✅" in message or "SUCCESS" in message:
            tag = "success"
        elif "❌" in message or "failed" in message or "Error" in message:
            tag = "error"
        elif "⚠️" in message or "Warning" in message:
            tag = "warning"
        elif "🔍" in message or "🧠" in message or "🚀" in message:
            tag = "info"
            
        self.log_area.insert('end', f"{message}\n", tag)
        self.log_area.see('end')
        self.log_area.config(state='disabled')
        self.root.update_idletasks()
        
    def create_magic(self):
        idea = self.idea_entry.get('1.0', 'end-1c').strip()
        if not idea or idea == 'A Python web scraper for extracting product data from e-commerce sites...':
            messagebox.showwarning("Input Required", "Please describe your repository idea!")
            return
            
        # Enhanced button state for processing
        self.magic_button.config(
            text="🔄 PROCESSING...", 
            state='disabled', 
            bg=self.secondary,
            cursor='wait'
        )
        
        # Update status
        self.connection_status.config(text="🚀 Creating repository...", fg=self.primary)
        
        def magic_process():
            original_cwd = os.getcwd()
            try:
                self.log("📁 Please select destination folder for your repository...", "info")
                self.root.update()
                
                folder = filedialog.askdirectory(title="Select folder for your new repository")
                if not folder:
                    self.log("❌ Operation cancelled - No folder selected", "error")
                    return
                    
                self.log(f"✅ Destination selected: {folder}", "success")
                
                self.log("🧠 Generating repository structure with AI...", "info")
                ai_data = generate_with_ai(idea, self.log)
                if not ai_data:
                    return
                    
                repo_name = ai_data.get('repo_name', 'AIRepo')
                repo_name = ''.join(c if c.isalnum() or c in '-_' else '-' for c in repo_name)
                repo_name = repo_name.strip('-_')
                if not repo_name:
                    repo_name = 'AIRepo'
                    
                repo_path = os.path.join(folder, repo_name)
                
                self.log(f"📂 Creating repository structure: {repo_name}", "info")
                os.makedirs(repo_path, exist_ok=True)
                
                create_files(repo_path, ai_data, self.log)
                
                self.log("🔧 Initializing Git repository...", "info")
                
                success, _, stderr = run_command(["git", "init"], cwd=repo_path)
                if not success:
                    self.log(f"❌ Git initialization failed: {stderr}", "error")
                    return
                
                success, _, _ = run_command(["git", "config", "user.name"], cwd=repo_path)
                if not success:
                    self.log("🔧 Configuring Git user settings...", "info")
                    run_command(["git", "config", "user.name", "AI Repo Creator"], cwd=repo_path)
                    run_command(["git", "config", "user.email", "ai@example.com"], cwd=repo_path)
                
                success, _, stderr = run_command(["git", "add", "."], cwd=repo_path)
                if not success:
                    self.log(f"❌ Failed to stage files: {stderr}", "error")
                    return
                
                success, stdout, _ = run_command(["git", "status", "--porcelain"], cwd=repo_path)
                if not success or not stdout.strip():
                    self.log("❌ No files available for commit", "error")
                    return
                
                commit_msg = "✨ Initial commit - repo created with AI"  #before changing this please star this repository thank you
                success, _, stderr = run_command(["git", "commit", "-m", commit_msg], cwd=repo_path)
                if not success:
                    self.log(f"❌ Commit failed: {stderr}", "error")
                    return
                
                self.log("✅ Git repository initialized and committed successfully", "success")
                
                self.log("🚀 Publishing to GitHub...", "info")
                desc = ai_data.get('description', 'AI-generated repository')
                
                success, _, stderr = run_command([
                    "gh", "repo", "create", repo_name,
                    "--public", "--description", desc,
                    "--source=.", "--remote=origin", "--push"
                ], cwd=repo_path)
                
                if not success:
                    self.log(f"❌ GitHub publication failed: {stderr}", "error")
                    if "already exists" in stderr:
                        self.log("💡 Repository name conflict - Please try with a different name", "warning")
                    return
                
                username = get_username()
                repo_url = f"https://github.com/{username}/{repo_name}"
                
                self.log("🎉 REPOSITORY CREATED SUCCESSFULLY!", "success")
                self.log(f"🌐 GitHub URL: {repo_url}", "info")
                self.log(f"📍 Local path: {repo_path}", "info")
                
                # Update status
                self.connection_status.config(text="🎉 Repository created!", fg=self.success)
                
                result = messagebox.askyesno("🎉 SUCCESS!", 
                                           f"Repository '{repo_name}' has been created successfully!\n\n"
                                           f"🌐 GitHub: {repo_url}\n"
                                           f"📍 Local: {repo_path}\n\n"
                                           "Would you like to open it in your browser?",
                                           icon='question')
                if result:
                    import webbrowser
                    webbrowser.open(repo_url)
                    
            except Exception as e:
                self.log(f"❌ Unexpected system error: {str(e)}", "error")
                messagebox.showerror("System Error", f"An unexpected error occurred:\n\n{str(e)}")
            finally:
                os.chdir(original_cwd)
                self.magic_button.config(
                    text="⚡ CREATE REPOSITORY", 
                    state='normal', 
                    bg=self.primary,
                    cursor='hand2'
                )
                self.connection_status.config(text="✅ Ready for next operation", fg=self.success)
        
        threading.Thread(target=magic_process, daemon=True).start()
        
    def run(self):
        self.root.mainloop()
