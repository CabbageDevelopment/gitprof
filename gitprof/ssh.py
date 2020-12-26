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
from typing import List

ssh_dir = os.path.expanduser("~/.ssh")


def create_ssh_key(name: str) -> str:
    print(
        f"Creating an SSH key following SSH best practices:\n"
        f"https://security.stackexchange.com/questions/143442/what-are-ssh-keygen-best-practices\n"
    )

    if not os.path.isabs(name):
        name = os.path.join(ssh_dir, name)

    command = f'ssh-keygen -t ed25519 -a 100 -f "{name}"'
    os.system(command)

    return fully_normalise_path(name)


def get_ssh_command(ssh_key: str) -> str:
    return f"ssh -i {fully_normalise_path(ssh_key)}"


def get_public_key(name: str) -> str:
    if not re.match(r"^.*\.pub$", name):
        name += ".pub"

    with open(name, "r") as f:
        pub = f.read()

    return pub


def fully_normalise_path(path: str) -> str:
    return os.path.normcase(os.path.normpath(os.path.abspath(path))).replace("\\", "/")


def get_ssh_key_path(key: str) -> str:
    if os.path.exists(key):
        return fully_normalise_path(key)

    return fully_normalise_path(os.path.join(ssh_dir, key))


def get_key_options() -> List[str]:
    files = os.listdir(ssh_dir)

    keys = [f for f in files if len([i for i in files if f in i]) == 2]
    return keys
