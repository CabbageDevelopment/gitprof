#  MIT License
#
#  Copyright (c) 2020 Sam McCormack
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import os
import re
import subprocess
import sys

import click

from gitprof import command_utils
from gitprof import os_utils
from gitprof import ssh
from gitprof import ux
from gitprof.cli import root
from gitprof.files import Config, Profile
from gitprof.vcs import services


def _create_clone_command(ssh_command, repo, dest) -> str:
    if os_utils.is_windows():
        return (
            f"powershell -c "
            + f'"git -c core.sshCommand="""{ssh_command}""" clone {repo}" "{dest}"'
        )

    return f'git -c core.sshCommand="{ssh_command}" clone "{repo}" "{dest}"'


def do_clone(
    ssh_command: str,
    repo: str,
    dest: str,
    add_to_known_hosts=False,
) -> None:
    if add_to_known_hosts:
        ssh_command = f"{ssh_command} -o StrictHostKeyChecking=no"

    cmd = _create_clone_command(ssh_command, repo, dest)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True,
    )

    print()

    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)

    process.wait()
    if process.returncode != 0:
        print(
            f"\nError: clone failed. Please view the error message above for details."
        )
        sys.exit(1)


@root.command("clone", help="Clone a Git repository")
@click.argument("repo")
@click.option("-p", "--profile", help="Which profile to clone the repo with")
def clone(repo: str, profile: str):
    profile = command_utils.choose_profile_interactive(
        profile, title="Choose a profile to clone with"
    )

    click.echo(f"Cloning '{repo}' with profile: {profile}")
    profile: Profile = Config().get_profile(name=profile)

    if not profile:
        click.echo(
            f"Profile '{profile}' appears to be missing. Have you created it?",
            err=True,
        )
        exit(1)

    ssh_key = profile.ssh_key
    if not ssh_key:
        click.echo(f"Can't find SSH key for profile '{profile}'")
        sys.exit(0)

    if not (profile.git_name and profile.git_email):
        click.echo(
            f"Warning: your Git name and/or email address are missing for this profile. You need to set them.",
            err=True,
        )
        exit(1)

    ssh_key = ssh.fully_normalise_path(ssh_key)
    if not os.path.exists(ssh_key):
        print(f"Error: can't find your SSH key at '{ssh_key}'.")
        sys.exit(1)

    dest = re.findall(r".*/(.*?)\.git", repo)[0]
    ssh_command = ssh.get_ssh_command(ssh_key)

    do_clone(ssh_command, repo, dest)
    cwd = os.getcwd()

    try:
        os.chdir(dest)
    except FileNotFoundError:
        print(
            f"Could not find your cloned repository. Please 'cd' into it and then use 'gitprof profile apply'."
        )

    command_utils.set_git_configs(profile)

    print(f"Finished setting up your Git repository.")
    os.chdir(cwd)
