import os, argparse, shutil, subprocess
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

parser = argparse.ArgumentParser()
parser.add_argument("src")
args = parser.parse_args()

def isValidUrl(src:str) -> bool:
    validate_url = URLValidator()
    try:
        validate_url(src)
        return True 
    except ValidationError:
        return False

def main():
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.system(f"git clone {args.src} output")
    os.chdir("output")
    os.system("git fetch")
    cmd = subprocess.Popen("git branch -a", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    branches = []
    raw = cmd.communicate()[0].decode("utf-8").split("\n")

    # Get all branches in repo
    for branch in raw:
        if "remotes/" in branch and not "HEAD ->" in branch:
            branches.append(branch)

    # Checkout all repos
    for branch in branches:
        try:
            branch_name = branch.split("/")[-1]
            subprocess.Popen(f"git checkout {branch} && git checkout -b {branch_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"Successfully checked out {branch_name}")
        except:
            print(f"Failed to checkout {branch_name}")

if __name__ == "__main__":
    if(args.src and isValidUrl(args.src)):
        main()
    else:
        print("Please a valid url to a git repo you want to clone")
        exit(1)