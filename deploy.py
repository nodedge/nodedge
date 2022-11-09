import os

app_name = "nodedge"
path = r".\nodedge\__main__.py"
qss_src = r".\nodedge\qss"
qss_dest = r".\nodedge\qss"
resources_src = r".\nodedge\resources"
resources_dest = r".\nodedge\resources"
examples_src = r".\examples"
version_file_path = r".\file_version_info.txt"
nodedge_logo = r".\nodedge\resources\Icon.ico"

command = (
    f"pyinstaller "
    f'--name="{app_name}" '
    f"{path} "
    f'--add-data="{qss_src}{os.pathsep}{qss_dest}" '
    f'--add-data="{resources_src}{os.pathsep}{resources_dest}" '
    f'--add-data="{examples_src}{os.pathsep}{examples_src}" '
    f'--version-file="{version_file_path}" '
    f"--onefile "
    f"--windowed "
    f"--noconfirm "
    f"--icon {nodedge_logo}"
)

os.system(command)
