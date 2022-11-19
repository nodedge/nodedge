#!/usr/bin/env python

"""The setup script."""

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]


# print(find_packages(include=['tage'], exclude=["examples*", "tests*"]))


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


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
    "pyside6",
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

PROJECT_URLS = {
    "Website": "https://nodedge.io",
    "Documentation": "https://nodedge.readthedocs.io/en/latest/",
    "Source": "https://github.com/nodedge/nodedge",
    "Tracker": "https://github.com/nodedge/nodedge/issues",
    "Donate": "https://github.com/sponsors/nodedge",
}

setup(
    name="nodedge",
    keywords=KEYWORDS,
    description="Graphical editor for physical modeling and simulation.",
    url="https://www.nodedge.io",
    version="0.3.0",
    license="MIT",
    author="Anthony De Bortoli",
    author_email="anthony.debortoli@nodedge.io",
    python_requires=">=3.7",
    classifiers=CLASSIFIERS,
    install_requires=requirements,
    long_description=readme + "\n\n" + history + "\n",
    long_description_content_type="text/x-rst",
    platforms=PLATFORMS,
    packages=find_packages(include="nodedge*", exclude=["tests"]),
    include_package_data=True,
    package_data={"": ["*.qss"]},
    exclude_package_data={"": ["*/icons/*", "*.pyc"]},
    setup_requires=setup_requirements,
    test_suite="tests",
    cmdclass={"test": PyTest},
    tests_require=test_requirements,
    zip_safe=False,
    entry_points={"console_scripts": ["nodedge = nodedge.__main__:main"]},
    project_urls=PROJECT_URLS,
)
