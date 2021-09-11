"""
Clone, checkout and save one or multiple git repositories at once with a single command.
"""

import argparse
import os
import subprocess
import sys
from urllib.parse import urlparse
from urls import url_list

END = "\033[0m"
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m"
}

CALLER_PATH = os.getcwd()
OUTPUT_FOLDER_NAME = "archived-repos"
OUTPUT_FOLDER_PATH = os.path.abspath(os.path.join(CALLER_PATH, OUTPUT_FOLDER_NAME))

def colored_string(prefix: str, string: str, color: str = "green", stdout: bool = True) -> None:
    """ Print or return a string with a colored prefix """
    value = f"[ {COLORS[color]}{prefix}{END} ] {string}"
    if stdout:
        print(value)
    return value

def shell(cmd: str, output: bool = True) -> str or None:
    """ Run a system shell command """
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE if output\
            else subprocess.DEVNULL, stderr=subprocess.STDOUT)
        process.wait()
        if output:
            return process.communicate()[0].decode("utf-8").split("\n")
    except:
        return None

def verify_url(url: str) -> bool:
    """ Check if url is valid """
    parsed = urlparse(url)
    return url and bool(parsed.scheme and parsed.netloc and parsed.path)

def require_confirmation(prompt: str) -> bool:
    """ Require a confirmation from the user before continuing """
    valid_responses = [ "y", "ye", "yes" ]
    answer = input(prompt)
    return answer.lower() in valid_responses

def get_repo_name(url: str) -> str:
    """ Parse a url to get the repository's name """
    return url.split("/")[-1].split(".")[0] if url else ""

def get_repo_path(url: str) -> str:
    """ Parse a url to get the path of the url """
    return os.path.abspath(os.path.join(OUTPUT_FOLDER_PATH, get_repo_name(url)))

def initialize():
    """ Create the necessary folders and checks before running script """
    if not os.path.exists(OUTPUT_FOLDER_PATH):
        os.makedirs(OUTPUT_FOLDER_PATH)

def clone_repo(repo_url: str, force: bool) -> None:
    """ Clone a repository """
    os.chdir(OUTPUT_FOLDER_PATH)
    continue_cloning = True
    if os.path.exists(get_repo_path(repo_url)) and not force:
        continue_cloning = require_confirmation(colored_string("WARN", \
            f"The folder '{get_repo_name(repo_url)}'' already exists, do" +
            "you want to overwrite it? (y/n)", "yellow", False))

    if not continue_cloning:
        colored_string("INFO", "Exiting...", "blue")
        sys.exit(0)
    else:
        colored_string("INFO", f"Cloning {get_repo_name(repo_url)}...", "blue")
        output = shell(f"git clone {repo_url} {get_repo_name(repo_url)}")
        if output[1] == "remote: Not Found":
            colored_string("ERROR", "Repository does not exist or is invalid", "red")

def checkout_branches(repo_url: str):
    """ Loop through all branches in repository and save them locally """
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
        colored_string("SUCCESS", \
            f"""All branches are checked out in "{get_repo_name(repo_url)}".""")
    except:
        colored_string("ERROR", "Failed to check out all repos.", "red")
        sys.exit(1)

def main():
    """ Main scripts function, runs all checks and functions that make this script """
    description = "Clone, checkout and save one or multiple git repositories at \
        once with a single command."
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
        colored_string("INFO", "You can provide urls by arguments or adding to \
            the list in 'urls.py'.", "blue")
        sys.exit(1)

    for url in urls:
        if verify_url(url):
            clone_repo(url, args.force)
            checkout_branches(url)
        else:
            print("ERROR", f"""Url "{url}" is invalid.""", "red")

if __name__ == "__main__":
    main()
