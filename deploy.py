import os

os.environ["NUMEXPR_MAX_THREADS"] = "16"

app_name = "nodedge"
path = r"nodedge/__main__.py"
resources_src = r"resources"
examples_src = r"examples"
version_file_path = r"file_version_info.txt"
nodedge_logo = r"resources/Icon.ico"

command = (
    f"pyinstaller "
    f'--name="{app_name}" '
    f"{path} "
    f'--add-data="{resources_src}{os.pathsep}{resources_src}" '
    f'--add-data="{examples_src}{os.pathsep}{examples_src}" '
    f'--version-file="{version_file_path}" '
    f"--onefile "
    f"--windowed "
    f"--noconfirm "
    f"--icon {nodedge_logo} "
    f"--log-level DEBUG"
)

os.system(command)
