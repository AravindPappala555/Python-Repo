from flask import Flask, render_template, request
from github import Github
import os
import github  # Added import for the `github` exception handling

app = Flask(__name__)

# Function to detect the language based on code syntax
def detect_language(code):
    if "import" in code or "def " in code:
        return "python"
    elif "#include" in code or "std::" in code:
        return "cpp"
    elif "public class" in code or "System.out.println" in code:
        return "java"
    elif "CREATE TABLE" in code or "SELECT" in code:
        return "sql"
    elif "function" in code or "console.log" in code:
        return "nodejs"
    elif "db." in code:
        return "mongodb"
    elif "module" in code or "endmodule" in code:
        return "verilog"
    elif "void main()" in code or "print()" in code and "dart" in code:
        return "dart"
    return "unknown"

# Function to determine the correct file extension based on the language
def get_file_extension(language):
    extensions = {
        "python": "py",
        "cpp": "cpp",
        "java": "java",
        "sql": "sql",
        "nodejs": "js",
        "mongodb": "js",
        "verilog": "v",
        "dart": "dart"
    }
    return extensions.get(language, "txt")

# Function to upload code to GitHub
def upload_to_github(username, token, language, code):
    g = Github(token)
    user = g.get_user()

    # Choose the repo based on the language
    repo_name = f"{language.capitalize()}-Repo"

    try:
        repo = user.get_repo(repo_name)
    except github.GithubException:
        # If the repo doesn't exist, create it
        repo = user.create_repo(repo_name)

    # Determine the filename with the correct extension
    extension = get_file_extension(language)

    try:
        # Get the list of files if the repo is not empty
        existing_files = repo.get_contents("")
        # Create a unique filename based on existing files in the repo
        count = sum(1 for file in existing_files if file.name.endswith(f".{extension}"))
    except github.GithubException as e:
        # Handle the case where the repo is empty (404 error)
        if e.status == 404:
            count = 0  # Start with code1 if the repo is empty
        else:
            raise e

    filename = f"code{count + 1}.{extension}"

    # Upload the file to GitHub
    repo.create_file(filename, "uploading code", code)

    return f"Code successfully uploaded to {repo_name} as {filename}!"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        token = request.form["token"]
        code = request.form["code"]

        # Detect the language of the code
        language = detect_language(code)

        # Upload code to GitHub
        try:
            result = upload_to_github(username, token, language, code)
        except Exception as e:
            result = f"Error: {str(e)}"

        return render_template("index.html", result=result)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
