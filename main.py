import argparse
import os
import subprocess
from urllib.parse import urlparse
from urls import url_list

END = "\033[0m"
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m"
}

caller_path = os.getcwd()
output_folder_name = "archived-repos"
output_folder_path = os.path.abspath(os.path.join(caller_path, output_folder_name))

def colored_string(prefix: str, string: str, color: str = "green", output: bool = False) -> None:
    value = f"[ {COLORS[color]}{prefix}{END} ] {string}"
    if output:
        return value
    else:
        print(value)

def shell(cmd: str, output: bool = True) -> str or None:
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE if output else subprocess.DEVNULL, stderr=subprocess.STDOUT)
        process.wait()
        if output:
            return process.communicate()[0].decode("utf-8").split("\n")
    except:
        return None

def verify_url(url: str) -> bool:
    parsed = urlparse(url)
    return url and bool(parsed.scheme and parsed.netloc and parsed.path)

def require_confirmation(prompt: str) -> bool:
    valid_responses = [ "y", "ye", "yes" ]
    answer = input(prompt)
    return answer.lower() in valid_responses

def get_repo_name(url: str) -> str:
    return url.split("/")[-1].split(".")[0] if url else ""

def get_repo_path(url: str) -> str:
    return os.path.abspath(os.path.join(output_folder_path, get_repo_name(url)))

def initialize():
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

def clone_repo(repo_url: str, force: bool) -> None:
    os.chdir(output_folder_path)
    try:
        continue_cloning = True
        if os.path.exists(get_repo_path(repo_url)) and not force:
            continue_cloning = require_confirmation(colored_string("WARN", \
                f"""The folder "{get_repo_name(repo_url)}" already exists, do you want to overwrite? (y/n) """,\
                 "yellow", True))

        if continue_cloning:
            colored_string("INFO", f"Cloning {get_repo_name(repo_url)}...", "blue")
            output = shell(f"git clone {repo_url} {get_repo_name(repo_url)}")
            if output[1] == "remote: Not Found":
                raise Exception("Repository does not exist")
    except:
        colored_string("ERROR", "Repository does not exist or is invalid", "red")
        exit(1)

def checkout_branches(repo_url: str):
    os.chdir(get_repo_path(repo_url))
    try:
        branches = []
        output = shell("git fetch && git branch -a")
        # Find all branches in repo
        for branch in output:
            if "remotes/" in branch and not "HEAD ->" in branch:
                branches.append(branch.strip())

        # Check out all branches
        for branch in branches:
            try:
                branch_name = branch.split("/")[-1]
                shell(f"git checkout {branch} && git checkout -b {branch_name}")
                colored_string("SUCCESS", f"Successfully checked out {branch}")
            except:
                colored_string("ERROR", f"Failed to checkout branch {branch}", "red")
        
        colored_string("SUCCESS", f"""All branches are checked out in "{get_repo_name(repo_url)}".""")
    except:
        colored_string("ERROR", "Failed to check out all repos.", "red")
        exit(1)

    
def main():
    description = "Clone, checkout and save one or multiple git repositories at once with a single command."
    usage = "main.py "

    # Arguments
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("-f", "--force", action="store_true")
    args = parser.parse_args()

    initialize()

    urls = args.urls if args.urls else url_list

    if len(urls) == 0:
        colored_string("ERROR", "No urls provided.", "red")
        colored_string("INFO", "You can provide urls by arguments or adding to the list in 'urls.py'.", "blue")
        exit(1)

    for url in urls:
        if verify_url(url):
            clone_repo(url, args.force)
            checkout_branches(url)
        else:
            print("ERROR", f"""Url "{url}" is invalid.""", "red")

if __name__ == "__main__":
    main()
