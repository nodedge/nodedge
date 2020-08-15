#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

# print(find_packages(include=['tage'], exclude=["examples*", "tests*"]))

KEYWORDS = [
    "nodedge",
    "editor",
    "graphical-programming",
    "simulation",
    "physical-modeling",
    "control-systems",
    "dynamic-systems",
    "python3",
    "qt5",
    "pyside2",
    "platform-indenpendent",
    "windows",
    "linux",
    "macos",
]

CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3.6",
]

PLATFORMS = ["Windows", "Linux", "Mac OS-X", "Unix"]

setup(
    name="nodedge",
    keywords=KEYWORDS,
    description="Graphical editor for physical modeling and simulation.",
    url="https://www.nodedge.io",
    version="0.2.2",
    license="MIT",
    author="Anthony De Bortoli",
    author_email="anthony.debortoli@nodedge.io",
    python_requires=">=3.6",
    classifiers=CLASSIFIERS,
    install_requires=requirements,
    long_description=readme + "\n\n" + history + "\n",
    long_description_content_type="text/x-rst",
    platforms=PLATFORMS,
    packages=find_packages(include="nodedge*", exclude=["tests"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    zip_safe=False,
    entry_points={"console_scripts": ["nodedge = nodedge.__main__:main"]},
)
