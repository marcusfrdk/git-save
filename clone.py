import os, argparse, shutil, subprocess, zipfile, glob
from urllib.parse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument("src")
parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

def log(msg: str, force: bool = False) -> None:
    if args.verbose or force:
        print(msg)

def main():
    # Manage folder and cloning
    folder_name = args.src.split("/")[-1]
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    process = subprocess.Popen(f"git clone {args.src} {folder_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait()
    os.chdir(folder_name)
    os.system("git fetch")
    cmd = subprocess.Popen("git branch -a", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log("Successfully cloned repository")

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
            log(f"Successfully checked out {branch_name}")
        except Exception:
            log(f"Failed to checkout {branch_name}")

    # Compress
    if args.compress:
        try:
            os.chdir("..")
            zipped_folder_name = f"{folder_name}.zip"
            if os.path.exists(zipped_folder_name):
                os.remove(zipped_folder_name)
            shutil.make_archive(folder_name, "zip")
            # shutil.rmtree(folder_name) # Is this something one would want?
            log(f"Successfully compressed {folder_name}")
        except:
            # log(getattr(e, "message", repr(e)))
            log("Failed to compress folder")

if __name__ == "__main__":
    if(args.src and bool(urlparse(args.src).scheme)):
        main()
    else:
        print("Please a valid url to a git repo you want to clone")
        exit(1)