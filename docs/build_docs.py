import os

os.system("sphinx-apidoc -e -T -f -o source/rst/ -t source/_templates/ ../nodedge")
os.system("make clean")
os.system("make html")
