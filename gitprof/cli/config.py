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
import sys

import click

from gitprof import files
from gitprof.cli import root


@root.group("config", help="Work with the config file")
def config():
    pass


@config.command("edit", help="Edit the config file.")
@click.argument("editor", required=False)
def edit_config(editor: str):
    if not os.path.exists(files.config_file):
        print(f"Config file does not exist.")
        sys.exit(0)

    if editor:
        return os.system(fr'"{editor}" {files.config_file}')

    os.system(f'start "" "{files.config_file}"')


@config.command("rm", help="Delete the config file")
def delete_config():
    try:
        os.remove(files.config_file)
    except FileNotFoundError:
        click.echo(f"Config file does not exist.")
