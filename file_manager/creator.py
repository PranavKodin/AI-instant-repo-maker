import os

def create_files(repo_path, data, log_callback=None):
    files = {
        'readme': 'README.md',
        'gitignore': '.gitignore', 
        'license_text': 'LICENSE',
        'requirements': 'requirements.txt'
    }
    
    for key, filename in files.items():
        content = data.get(key, '')
        if content and content.strip():
            try:
                with open(os.path.join(repo_path, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
                if log_callback:
                    log_callback(f"✅ Created: {filename}")
            except Exception as e:
                if log_callback:
                    log_callback(f"❌ Failed to create {filename}: {str(e)}")
