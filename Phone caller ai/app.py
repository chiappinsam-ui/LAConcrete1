import subprocess

from flask import Flask, request

app = Flask(__name__)


@app.route("/execute", methods=["POST"])
def handle_request():
    data = request.json

    # Security check using your new key
    if not data or data.get("secret") != "1234":
        return "Unauthorized", 401

    if data.get("action") == "git_push":
        # Your exact Windows folder path
        repo_dir = r"C:\Users\hoopb\OneDrive\Desktop\Phone caller ai"
        subprocess.run(["git", "add", "."], cwd=repo_dir)
        subprocess.run(
            ["git", "commit", "-m", "Automated push from AI caller"],
            cwd=repo_dir,
        )
        subprocess.run(["git", "push"], cwd=repo_dir)
        return "Pushed to GitHub successfully!", 200

    return "Invalid action", 400


if __name__ == "__main__":
    app.run(port=5000)
