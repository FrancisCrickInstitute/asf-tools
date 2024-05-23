#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.md", encoding="UTF-8") as f:
    readme = f.read()

with open("requirements.txt", encoding="UTF-8") as f:
    required = f.read().splitlines()


def get_version(rel_path):
    """Extract version information from source code."""
    with open(rel_path, "r") as file:
        for line in file:
            if line.startswith("__version__"):
                # Remove quotation marks
                delims = "\"'"
                return line.split("=")[1].strip().strip(delims)
    return "0.0.0"  # Default if version not found


setup(
    name="asf-tools",
    version=get_version("asf_tools/__init__.py"),
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[],
    author="",
    author_email="",
    url="",
    license="",
    entry_points={"console_scripts": ["asf_tools=asf_tools.__main__:run_asf_tools"]},
    python_requires=">=3.11",
    install_requires=required,
    packages=find_packages(exclude="docs"),
    include_package_data=True,
    zip_safe=False,
)
