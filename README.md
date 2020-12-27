# GitProf

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/gitprof?color=brightgreen)](https://pypi.org/project/gitprof)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gitprof?color=blue)](https://pypi.org/project/gitprof)

## Introduction

GitProf ("Git Profiles") is a tool which simplifies working with multiple Git accounts/services.

GitProf helps you with:

- Using different Git services (e.g. GitHub and GitLab).
- Using multiple accounts on GitHub (e.g. personal and work accounts).

It solves the problems which you may experience when using multiple accounts/services:

- You can't clone a repository easily because your default SSH key is for a different account.
- Once you clone the repository, local Git config values such as `user.email` need to be set correctly.

GitProf doesn't change your Git workflow; after using `gitprof clone` or `gitprof profile apply` on a repository, you don't need to interact with `gitprof` again for that repository. 

## Installation

Requirements:

- Python 3.7 or higher, with the `pip` package manager (which is usually installed by default).
- Windows, Linux or macOS.

When installed with `pip`, the `gitprof` executable is automatically added to the `PATH` and behaves as a standalone program.

To install GitProf with `pip`, run the command:

```bash
pip install gitprof
```

Now you can run `gitprof version` to check that it is installed and available on the `PATH`.

## Quick Start

GitProf stores *profiles* which contain the information required to configure repositories for different accounts. When you run a command which uses a profile, you will be prompted to choose an existing profile or create a new one.

### Cloning a new repository

To clone a repository, just use `gitprof clone` instead of `git clone`. For example:

```bash
>> gitprof clone git@gitlab.com/some-profile/some-repo.git

### Choose a profile to clone with ###
[0] github                         (GitHub)
[2] gitlab                         (GitLab)
[3] <CREATE NEW PROFILE>
Enter a number from the list to choose an option [default=0]: 1

Cloning 'git@gitlab.com/some-profile/some-repo.git' with profile: gitlab

Setting local Git config values for 'some-repo'...
Setting your Git name to 'MyUsername'...
Setting your Git email to 'MyGitEmail'...
Setting your Git SSH command to 'ssh -i ~/.ssh/my_ssh_key'...
Finished setting up your Git repository.
```

### Applying a profile to an existing repository

If you have an existing repository whose config values you wish to change, you can `cd` into the repository and use `gitprof profile apply`. For example:

```bash
>> cd some-repo
>> gitprof profile apply

### Choose a profile to apply ###
[0] github                         (GitHub)
[2] gitlab                         (GitLab)
[3] <CREATE NEW PROFILE>
Enter a number from the list to choose an option [default=0]: 1

Setting local Git config values for 'some-repo'...
Setting your Git name to 'MyUsername'...
Setting your Git email to 'MyGitEmail'...
Setting your Git SSH command to 'ssh -i ~/.ssh/my_ssh_key'...
```

> **Tip**: GitProf includes help info, even for subcommands. For example, you can use `gitprof profile --help` to see parameters for the `profile` subcommand.

## Developer Notes

### Packaging the project

```bash
rm -r dist/
python -m pip install -r requirements-dev.txt -r requirements.txt
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
```
