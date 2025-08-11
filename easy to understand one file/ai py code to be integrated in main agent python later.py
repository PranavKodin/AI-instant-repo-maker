import os
import json
import tkinter as tk
from tkinter import filedialog
from google import generativeai as genai

# --- YOUR API KEY (leave as-is) ---
genai.configure(api_key="AIzaSyAq6sB4h1pFHX4IL0IeRCtA7RE6_40gjXY")  # ✅ your real key goes here

# --- STEP 1: USER INPUT ---
user_input = input("📌 Enter your repo idea:\n").strip()
if not user_input:
    print("❌ Empty input. Exiting.")
    exit()

# --- STEP 2: PROMPT PREP ---
prompt = f"""
Create a public GitHub repo for this idea: {{{user_input}}}

Return only a clean JSON object like:
- "repo_name"
- "license"
- "readme"
- "gitignore"
- "requirements"
- "license_text"
- any other meta text files

⚠️ DO NOT return code files like main.py or app.py.
⚠️ NO markdown, NO code blocks, NO explanation — ONLY a valid JSON.
"""

# --- STEP 3: GEMINI CALL ---
print("⏳ Contacting Gemini 2.5 flash Lite...")
try:
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    print("✅ Gemini responded.")
except Exception as e:
    print("❌ Gemini API error:", e)
    exit()

# --- STEP 4: PARSE JSON RESPONSE ---
print("🧪 Parsing Gemini response...")
try:
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").split("\n", 1)[-1]
    data = json.loads(raw_text)
    print("✅ JSON parsed successfully.")
except json.JSONDecodeError as e:
    print("❌ Failed to decode JSON:", e)
    print("Raw response:\n", raw_text)
    exit()

# --- STEP 5: TKINTER FOLDER PICKER ---
print("📁 Please select a folder to create the repo.")
try:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # Force it to front
    folder = filedialog.askdirectory(title="Select folder for your GitHub repo")
    if not folder:
        print("⚠️ No folder selected. Exiting.")
        exit()
except Exception as e:
    print("❌ Folder picker failed:", e)
    exit()

# --- STEP 6: CREATE FILES ---
repo_name = data.get("repo_name", "UntitledRepo")
repo_dir = os.path.join(folder, repo_name)
os.makedirs(repo_dir, exist_ok=True)

SKIP_KEYS = {"repo_name", "license"}
EXTENSION_MAP = {
    "readme": "README.md",
    "gitignore": ".gitignore",
    "requirements": "requirements.txt",
    "license_text": "LICENSE"
}

for key, content in data.items():
    if key in SKIP_KEYS:
        continue
    filename = EXTENSION_MAP.get(key.lower(), f"{key}.txt")
    path = os.path.join(repo_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Created: {filename}")

# --- STEP 7: DONE ---
print("\n✅ Repo created at:", repo_dir)
print("📛 Repo Name:", repo_name)
print("🪪 License:", data.get("license", "Not specified"))
