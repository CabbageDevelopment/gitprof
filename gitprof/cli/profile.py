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
import sys
import webbrowser
from typing import List

import click

from gitprof import command_utils
from gitprof import ssh
from gitprof import ux
from gitprof.cli import root
from gitprof.files import Config, Profile
from gitprof.ssh import get_key_options, get_ssh_key_path, create_ssh_key
from gitprof.vcs import github_utils, services


@root.group("profile", help="Add, delete or modify a profile")
def profile():
    pass


@profile.command("create", help="Add a new profile")
@click.argument("name")
@click.option("--username", help="Your username for the service (e.g. GitHub)")
def create_profile(name: str, username: str = None):
    ux.print_header(f"Creating profile: {name}")

    config = Config()
    if config.get_profile(name):
        click.echo(
            f"Profile '{name}' already exists. Please edit it instead of creating a new one.",
            err=True,
        )
        sys.exit(1)

    keys: List[str] = get_key_options()
    chosen = ux.get_input_from_list(
        title="Choose an SSH key",
        options=keys,
        fallback="CREATE NEW KEY",
    )

    new_ssh_key = False
    if chosen.is_fallback():
        ssh_key = ux.get_simple_input(
            question="Enter the name for your SSH key",
            validator=lambda p: len(p.split(" ")) == 1,
            default=name,
        )
        ssh_key = create_ssh_key(ssh_key)
        new_ssh_key = True
    else:
        ssh_key = chosen.value

    key_path = get_ssh_key_path(ssh_key)

    service = ux.get_input_from_list(
        title="Select the service this profile is for",
        options=services.get_services(),
        fallback_enter_manually=True,
    ).value

    profile: Profile = Profile(name, key_path, service=service)

    if not username and service.lower() == "github":
        username = ux.get_simple_input(
            f"What's your username for the service '{service}'?\n"
            f"This is used to automatically find your committer name and email",
            optional=True,
        )

    if username:
        print(f"Trying to find your Git committer name and email...")
        result = github_utils.get_name_and_email(username)

        if len(result) == 2:
            name, email = result

            profile.git_name = name
            profile.git_email = email

            click.echo(
                f"\nYour name and email were found and are set as the defaults for the next questions."
            )

    profile.git_name = ux.get_simple_input(
        "Enter your Git committer name", default=profile.git_name
    )
    profile.git_email = ux.get_simple_input(
        "Enter your Git committer email", default=profile.git_email
    )

    if new_ssh_key:
        print(f"Your new SSH public key is:\n{ssh.get_public_key(ssh_key)}")
        url = services.get_ssh_url_for(profile.service)

        if (
            url
            and ux.get_simple_input(
                question=f"Would you like to open the settings on '{profile.service}' to add your SSH key [Y/n]",
                default="Y",
                show_default=False,
            ).lower()
            == "y"
        ):
            webbrowser.open_new_tab(url)

    config.add_profile(profile)
    config.save()

    click.echo(f"Saved profile: {name}")


@profile.command("apply", help="Apply profile to current repository")
@click.option("-p", "--profile", help="The profile to apply")
def apply_profile(profile: str):
    profile = command_utils.create_profile_interactive(profile)

    profile: Profile = Config().get_profile(name=profile)
    command_utils.set_git_configs(profile)


@profile.command("rm", help="Delete one or more profiles")
@click.argument("names", nargs=-1)
def delete_profile(names: tuple):
    for n in names:
        do_delete(n)


def do_delete(name: str):
    click.echo(f"Deleting profile '{name}'...")
    config = Config()

    if config.get_profile(name):
        config.delete_profile(profile_name=name)
        config.save()
    else:
        print("Profile does not exist.")
        sys.exit(0)

    if not config.get_profile(name):
        print(f"Successfully deleted profile.")
    else:
        print("Error: failed to delete profile.")


@profile.command("ls", help="List your profiles")
@click.option("-q", "--quiet", is_flag=True, help="List profile names only")
def list_profiles(quiet: bool):
    profiles = Config().get_profiles()

    if not profiles:
        return click.echo("No profiles exist.")

    for p in profiles:
        if quiet:
            print(p.name)
        else:
            print(p)


@profile.command("edit", help="Edit an existing profile")
@click.argument("name")
@click.option("--git-name", help="Your committer name to use for this profile.")
@click.option("--git-email", help="Your committer email to use for this profile.")
def edit_profile(name: str, git_name: str, git_email: str):
    config = Config()
    profile: Profile = config.get_profile(name)

    if not profile:
        print(f"Profile '{name}' does not exist.")
        sys.exit(0)

    if git_name:
        profile.git_name = git_name
    if git_email:
        profile.git_email = git_email

    for field, value in profile.__dict__.items():
        value = ux.get_simple_input(
            question=f"Enter new value for '{field}'", default=value
        )
        setattr(profile, field, value)

    config.set_profile(profile)
    config.save()
