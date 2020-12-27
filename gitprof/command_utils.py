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

from gitprof import ux
from gitprof import ssh
from gitprof.files import Profile, Config


def run_command(args: str):
    raw = subprocess.check_output(
        args,
        stdin=None,
        stderr=None,
        shell=True,
        universal_newlines=False,
    ).decode("utf-8")
    return "".join(raw).strip().replace("\r\n", "")


def set_git_configs(profile: Profile):
    print(f"\nSetting local Git config values for '{os.getcwd()}'...")
    ssh_command = ssh.get_ssh_command(profile.ssh_key)

    print(f"Setting your Git name to '{profile.git_name}'...")
    run_command(f'git config --local user.name "{profile.git_name}"')

    print(f"Setting your Git email to '{profile.git_email}'...")
    run_command(f'git config --local user.email "{profile.git_email}"')

    print(f"Setting your Git SSH command to '{ssh_command}'...")
    run_command(f'git config --local core.sshCommand "{ssh_command}"')


def choose_profile_interactive(profile: str, title: str) -> str:
    config = Config()

    while not profile:
        config.reload()

        if not profile:
            options = config.get_profiles()
            for index, profile in enumerate(options):
                options[index] = profile.name

                if profile.service:
                    whitespace = " " * (35 - len(profile.name))
                    options[index] = f"{options[index]}{whitespace}({profile.service})"

            chosen = ux.get_input_from_list(
                title=title,
                options=options,
                fallback="create new profile",
                fallback_index=-1,
            )

            matches = re.findall(r"^(.*?)\s*\(.*\)\s*$", chosen.value)
            if matches:
                chosen.value = matches[0]

            if not config.get_profiles() or chosen.is_fallback():
                name = ux.get_simple_input(
                    question="Enter a name for your new profile (e.g. 'github')",
                    validator=lambda n: len(n.split(" ")) == 1,
                )
                profile = name
                os.system(f"gitprof profile create {name}")
                continue

            profile = chosen.value

    return profile
