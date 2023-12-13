import os
import shutil


def build_docs() -> None:
    """
    Build Nodedge documentation using sphinx

    :return: None
    """
    shutil.rmtree("source/apidoc")
    os.mkdir("source/apidoc")
    os.system(
        "sphinx-apidoc -e -T -f " "-o source/apidoc/ -t source/_templates/ ../nodedge"
    )
    os.system("make clean")
    os.system("make html")
    os.system(
        "pip-licenses --with-description --with-authors "
        "--with-urls  -f rst --output-file=source/licenses.rst"
    )


if __name__ == "__main__":
    build_docs()
