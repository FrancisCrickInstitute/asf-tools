#!/usr/bin/env python

from setuptools import find_packages, setup

version = "0.1dev"

with open("README.md", encoding="UTF-8") as f:
    readme = f.read()

with open("requirements.txt", encoding="UTF-8") as f:
    required = f.read().splitlines()

setup(
    name="asf-tools",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[],
    author="",
    author_email="",
    url="",
    license="",
    entry_points={"console_scripts": ["asf_tools=asf_tools.__main__:run_asf_tools"]},
    python_requires=">=3.10",
    install_requires=required,
    packages=find_packages(exclude="docs"),
    include_package_data=True,
    zip_safe=False,
)
