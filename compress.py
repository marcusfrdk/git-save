import os, shutil

caller_path = os.getcwd()
output_folder_name = "archived-repos"
output_path = os.path.abspath(os.path.join(caller_path, output_folder_name))

if __name__ == "__main__":
    try:
        os.chdir(caller_path)
        if os.path.exists(f"{output_path}.zip"):
            shutil.rmtree(output_path)
        shutil.make_archive(output_folder_name, "zip")
        shutil.rmtree(output_path)
    except:
        print("Failed to compress folder")