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
from gitprof import ssh
from gitprof import ux
from gitprof.cli import root
from gitprof.files import Config, Profile
from gitprof.vcs import services


def do_clone(
    ssh_command: str, repo: str, profile: Profile, dest: str, add_to_known_hosts=False
):
    if add_to_known_hosts:
        ssh_command = f"{ssh_command} -o StrictHostKeyChecking=no"

    cmd = (
        f"powershell -c "
        f'"git -c core.sshCommand="""{ssh_command}""" clone {repo}" "{dest}"'
    )

    pipes = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    stdout, stderr = pipes.communicate()

    if pipes.returncode != 0:
        ux.print_header("CLONE FAILED", newlines_before=2)

        stdout, stderr = (
            i.decode("utf-8").replace("\r", "").strip() for i in (stdout, stderr)
        )
        stdcombined = stdout + stderr

        print(stdout)
        print(stderr)

        def advice():
            ux.print_header("ADVICE", newlines_before=2)

        not_in_known_hosts = re.findall(
            r"Host key verification failed",
            stdcombined,
            re.MULTILINE,
        )

        if re.match("Identity file (.*) not accessible", stdcombined):
            advice()
            print("Your SSH key seems to be missing.")
        elif "Permission denied" in stdcombined:
            advice()

            pub = ssh.get_public_key(profile.ssh_key)
            print(f"\nYour SSH public key is:\n\n{pub}")

            ux.sleep(1)

            url = services.get_ssh_url_for(profile.service)
            if url:
                print(
                    f"You may need to add the SSH key to "
                    f"your account on '{profile.service}'."
                )
                yes = (
                    ux.get_simple_input(
                        question="Would you like to open the settings page for this [Y/n]",
                        default="Y",
                        show_default=False,
                    ).lower()
                    == "y"
                )

                if yes:
                    import webbrowser

                    webbrowser.open_new_tab(url)

            sys.exit(1)
        elif not_in_known_hosts:
            print(stdcombined)

            if (
                ux.get_simple_input(
                    question="The remote server is not in 'known_hosts'. "
                    "Would you like to add it? [Y/n]",
                    default="y",
                    show_default=False,
                    newlines_before=2,
                ).lower()
                == "y"
            ):
                print(f"Cloning with '-o StrictHostKeyChecking=no' in SSH command...")
                do_clone(ssh_command, repo, profile, dest, add_to_known_hosts=True)
            else:
                print(f"Sorry, cannot clone when the host key is not accepted.")
                sys.exit(1)
        else:
            sys.exit(1)


@root.command("clone", help="Clone a Git repository")
@click.argument("repo")
@click.option("-p", "--profile", help="Which profile to clone the repo with")
def clone(repo: str, profile: str):
    profile = command_utils.create_profile_interactive(profile)

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

    do_clone(ssh_command, repo, profile, dest)
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
