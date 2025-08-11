import subprocess
import threading

def run_command(cmd, cwd=None, capture_output=True):
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, 
                              text=True, check=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)

def check_github_cli(log_callback):
    def check():
        try:
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
            subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
            log_callback("✅ GitHub CLI ready!")
        except:
            log_callback("❌ GitHub CLI not ready. Please run 'gh auth login'")
    threading.Thread(target=check, daemon=True).start()

def get_username():
    success, stdout, _ = run_command(["gh", "api", "user", "--jq", ".login"])
    if success:
        return stdout.strip()
    return "user"
