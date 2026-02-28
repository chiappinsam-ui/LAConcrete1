import subprocess
from flask import Flask, request, send_file
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# 1. Boot up the AI connection
client = genai.Client(api_key="AIzaSyDyknMlCojGvlF1gMToeOAakajY4-aGr-4")

# -> THIS IS THE NEW PART: Serving your UI directly! <-
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/execute', methods=['POST'])
def handle_request():
    data = request.json
    
    # Security check
    if not data or data.get('secret') != '1234':
        return "Unauthorized", 401

    user_command = data.get('command')
    
    # 2. If a command is sent, ask the AI how to handle it
    if user_command:
        print(f"\n--- PHONE COMMAND RECEIVED ---")
        print(f"Command: {user_command}")
        
        try:
            prompt = f"I am a Python automation script. The user just told me: '{user_command}'. What specific file edits or Git commands should I execute to fulfill this? Be incredibly concise."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            print(f"\n--- GEMINI'S BRAIN ---")
            print(response.text)
            print("----------------------\n")
            
        except Exception as e:
            print(f"Failed to wake up AI: {e}")
            return "AI Error", 500

    # 3. The physical Git push trigger
    if data.get('action') == 'git_push':
        repo_dir = r"C:\Users\hoopb\OneDrive\Desktop\Phone caller ai"
        try:
            subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True, text=True, check=True)
            subprocess.run(["git", "commit", "-m", "Automated push from AI caller"], cwd=repo_dir, capture_output=True, text=True, check=True)
            push_result = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, check=True)
            print("\nGit Push Output:", push_result.stdout)
            return "Pushed to GitHub successfully!", 200
            
        except subprocess.CalledProcessError as e:
            print(f"\n--- GIT FAILED ---\nError: {e.stderr}")
            return f"Git failed", 500

    return "Command processed!", 200

if __name__ == '__main__':
    app.run(port=5000)
