import argparse, shutil, os, subprocess
from urllib.parse import urlparse
from compress import caller_path, output_path, output_folder_name

description = "Download an entire git repository"
usage = "main.py PATH"

# Arguments
parser = argparse.ArgumentParser(usage=usage, description=description)
parser.add_argument("path")
parser.add_argument("-f", "--force", action="store_true", help="bypass any confirmation prompt")
parser.add_argument("-v", "--verbose", action="store_true", help="more logs in terminal")
parser.add_argument("-nc", "--no-compress", action="store_true", help="skip compression")
args = parser.parse_args()

repo_name: str = args.path.split("/")[-1].split(".")[0] if args.path else ""
repo_path = os.path.abspath(os.path.join(output_path, repo_name))

def shell(cmd: str, output: bool = True) -> str or None:
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE if output else subprocess.DEVNULL, stderr=subprocess.STDOUT)
        process.wait()
        if output:
            return process.communicate()[0].decode("utf-8").split("\n")
    except:
        return None

def log(msg: str, force: bool = False) -> None:
    if args.verbose or force:
        print(msg)

def clean():
    for root, dirs, files in os.walk(output_path):
        if len(dirs) == 0 and len(files) == 0:
            shutil.rmtree(root)

def parse_input() -> str:
    # Make sure path exists and is valid
    parsed = urlparse(args.path)
    if args.path and bool(parsed.scheme and parsed.netloc and parsed.path): # There probably is a better way of doing this
        return args.path
    else:
        print("The specified url is invalid, please use another one")
        exit(1)

def require_confirmation(prompt: str) -> None:
    if not args.force:
        valid_responses = [ "y", "ye", "yes" ]
        answer = input(f"{prompt} (y/n): ")
        if answer.lower() not in valid_responses:
            print("Exiting...")
            clean()
            exit(1)

def initialize() -> None:
    if not os.path.exists(output_path): # No output folder
        os.makedirs(output_path)
    elif os.path.exists(repo_path): # Repository already exists
        require_confirmation(f"""The folder "{repo_name}" already exists, delete it?""")
        shutil.rmtree(repo_path)
        os.makedirs(repo_path)

def clone_repo(path: str) -> None:
    os.chdir(output_path)
    try:
        output = shell(f"git clone {path} {repo_name}")
        if output[1] == "remote: Not Found":
            raise Exception("Repository does not exist")
    except:
        print("Repository does not exist or is invalid")
        clean()
        exit(1)

def checkout_branches():
    os.chdir(repo_path)
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
            log(f"Successfullt checked out {branch}")
        
        log("Successfully checked out all branches")
    except:
        print("Failed to check out all repos, please try running the script again")
        exit(1)

    
def main():
    path = parse_input()
    initialize()
    clone_repo(path)
    checkout_branches()

if __name__ == "__main__":
    main()