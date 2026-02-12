## in order to generate file paths , and read and write the content we generated in it  , we need tools
import pathlib
import subprocess                         # it is used to run the python scripts , execute shell commands , call other programs
from typing import Tuple

from langchain_core.tools import tool

# building a path pointing to a subfolder named  "Generated_projects_code" , inside the current working directory where your scripts run
PROJECT_ROOT = pathlib.Path.cwd() / "Generated_projects_code"



# this function helps in safely building a full file path inside the Generated_projects_code folder and blocks it , if path tries to escape outside the folder by raising the value error
def safe_path_for_project(path:str)-> pathlib.Path:
    p = (PROJECT_ROOT / path).resolve()                     # .resolve() converts the path into absolute normalized path

    if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p.parents and PROJECT_ROOT.resolve() != p:
        raise ValueError("attempt to write outside the project root ")
    return p

@tool
def write_file(path:str,content:str)->str:
    """write a content to a file at the specified path within the project root """
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w" , encoding='utf-8') as f:                    # for safer behaviour you can use "x" in place of "w"-'write' , x avoides overwriting
        f.write(content)
    return f"WROTE {p}"

@tool
def read_file(path:str)->str:
    """reads the content from a file at the specified path in the project root """
    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p ,'r' , encoding='utf-8') as f:
        return f.read()

@tool
def get_current_directory() -> str:
    """ Return the current working directory """
    return str(PROJECT_ROOT)

@tool
def list_files(directory: str = ".") ->str:               # "." means the current folder
    """ Return a list of all files in a specified directory within the project root """
    p = safe_path_for_project(directory)
    if not  p.is_dir():
        return f" Error : {p} is not a directory"
    files = []
    for f in p.glob("**/*"):
        if f.is_file():
            files.append(str(f.relative_to(PROJECT_ROOT)))
    return "\n".join(files) if files  else "file not found"

@tool
def run_cmd(cmd: str , cwd:str=None , timeout:int = 30 )->Tuple[int,str,str]:
    """Runs the shell command in the  specified directory and returns the result."""

    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT

    resp=subprocess.run(cmd, shell=True, cwd=str(cwd_dir),capture_output=True,text=True, timeout=timeout)
    return resp.returncode , resp.stdout , resp.stderr


# this function creates you project folder if it is does not exist and then return the path as a text
def init_project_root():
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)






