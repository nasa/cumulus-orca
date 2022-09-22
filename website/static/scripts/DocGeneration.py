import os
import pydoc
import subprocess


class TaskInfo:
    Name: str
    Primary_File: str

    def __init__(self, name, primary_file):
        self.Name = name
        self.Primary_File = primary_file


os.chdir('..')
repo_dir = os.getcwd()
tasks = [
    TaskInfo("copy_files_to_archive", "copy_files_to_archive.py"),
    TaskInfo("copy_to_archive", "handler.py"),
    TaskInfo("db_deploy", "db_deploy.py"),
    TaskInfo("extract_filepaths_for_granule", "extract_filepaths_for_granule.py"),
    TaskInfo("request_files", "request_files.py"),
    TaskInfo("request_status", "request_status.py")
]

for task in tasks:
    os.chdir(f"{repo_dir}\\tasks\\{task.Name}")
    print(f"Running for {task.Name}\\{task.Primary_File}")
    # subprocess.Popen?
    filename = os.path.splitext(task.Primary_File)[0]

    # pydoc.
    docs = subprocess.Popen(['venv/Scripts/python.exe', '-c', f"python -m pydoc {filename}"])
    docs.wait()
    # docs = subprocess.run(['venv/Scripts/python', '-c', f"python -m pydoc {filename}"])
    docs = docs.stdout
    print(docs)
    # os.system('venv\\Scripts\\activate')
    # docs = os.system(f"python -m pydoc {filename}")
    print(docs)

    # os.system('deactivate')
    # Remove the last 6 lines that contain the local file path and whitespace.
    docs = docs[:docs.count() - 6]
    with open(f"{repo_dir}\\website\\docs\\developer\\code\\lambda_docs\\{task.Name}.md") as doc_file:
        doc_file.write(docs)
