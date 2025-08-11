import json
from google import generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("gemini_api_key"))

def generate_with_ai(idea, log_callback):
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
        
        if raw.startswith("```"):
            lines = raw.split('\n')
            start_idx = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('```') and 'json' not in line.lower():
                    start_idx = i
                    break
            end_idx = len(lines)
            for i in range(len(lines)-1, -1, -1):
                if not lines[i].strip().startswith('```'):
                    end_idx = i + 1
                    break
            raw = '\n'.join(lines[start_idx:end_idx])
                
        data = json.loads(raw)
        log_callback("✅ AI generation completed!")
        return data
        
    except json.JSONDecodeError as e:
        log_callback(f"❌ Invalid JSON from AI: {str(e)}")
        log_callback(f"Raw response: {raw[:200]}...")
        return None
    except Exception as e:
        log_callback(f"❌ AI generation failed: {str(e)}")
        return None
