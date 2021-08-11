import argparse, shutil, os, subprocess
from urllib.parse import urlparse

caller_path = os.getcwd()
output_folder_name = "archived-repos"
output_folder_path = os.path.abspath(os.path.join(caller_path, output_folder_name))

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
    answer = input(f"{prompt} (y/n): ")
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
            continue_cloning = require_confirmation(f"""The folder "{get_repo_name(repo_url)}" already exists, do you want to overwrite?""")

        if continue_cloning:
            print(f"Cloning {get_repo_name(repo_url)}...")
            output = shell(f"git clone {repo_url} {get_repo_name(repo_url)}")
            if output[1] == "remote: Not Found":
                raise Exception("Repository does not exist")
    except:
        print("Repository does not exist or is invalid")
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
            branch_name = branch.split("/")[-1]
            shell(f"git checkout {branch} && git checkout -b {branch_name}")
            print(f"Successfullt checked out {branch}")
        
        print(f"""Successfully checked out all branches in "{get_repo_name(repo_url)}".""")
    except:
        print("Failed to check out all repos, please try running the script again")
        exit(1)

    
def main():
    description = "Download an entire git repository"
    usage = "main.py "

    # Arguments
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("-f", "--force", action="store_true")
    args = parser.parse_args()

    initialize()

    for url in args.urls:
        if verify_url(url):
            clone_repo(url, args.force)
            checkout_branches(url)

if __name__ == "__main__":
    main()