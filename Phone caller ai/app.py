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

        try:
            # We combine the commands so we can see the full output of the chain
            result = subprocess.run(
                ["git", "add", "."],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Automated push from AI caller"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            push_result = subprocess.run(
                ["git", "push"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )

            # Print success to the Flask terminal
            print("Git Push Output:", push_result.stdout)
            return "Pushed to GitHub successfully!", 200

        except subprocess.CalledProcessError as e:
            # If Git fails, this catches the error and prints it to your terminal
            print(f"GIT FAILED! Error code: {e.returncode}")
            print(f"Error output: {e.stderr}")
            print(f"Standard output: {e.stdout}")
            return f"Git failed: {e.stderr}", 500

    return "Invalid action", 400


if __name__ == "__main__":
    app.run(port=5000)
