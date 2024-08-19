#!/usr/bin/env python

import subprocess

def get_version():
    try:
        tag = subprocess.check_output(['git', 'describe', '--tags']).strip().decode('utf-8')
        if '-' in tag:
            tag, commits, _ = tag.split('-')
            version = f"{tag}.{commits}"
        else:
            version = tag
    except subprocess.CalledProcessError:
        version = "0.1"

    branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    if branch != 'main':
        version += "-dev"

    return version

if __name__ == "__main__":
    print(get_version())
