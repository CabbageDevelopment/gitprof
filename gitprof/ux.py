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
import re
import sys
import time
from typing import List, Callable

import click


class SelectedOption:
    def __init__(self, value, is_fallback):
        self.fallback = is_fallback
        self.value = value

    def is_fallback(self) -> bool:
        return self.fallback

    def __str__(self):
        return ("[fallback option] " if self.fallback else "") + self.value

    @staticmethod
    def fallback(value) -> "SelectedOption":
        return SelectedOption(is_fallback=True, value=value)

    @staticmethod
    def create(value):
        return SelectedOption(value=value, is_fallback=False)


def get_simple_input(
    question: str,
    default: str = "",
    attempts=3,
    add_colon=True,
    optional=False,
    validator: Callable = lambda i: True,
    validation_failure_msg="Input failed validation. Please try again.",
    newlines_before=0,
    newlines_after=1,
    show_default=True,
) -> str:
    if default and show_default:
        question += f" [default='{default}']"
    if not question.endswith(":") and add_colon:
        question += ":"
    if not question.endswith(" "):
        question += " "

    if optional:
        question = "[optional] ".upper() + question

    question = newlines_before * "\n" + question

    for i in range(attempts):
        out = input(question).strip()

        if out:
            if not validator(out):
                click.echo(validation_failure_msg)
                continue
            else:
                break
        elif default:
            out = default
            break

        if optional:
            break

        click.echo("Bad input. Please try again.")
    else:
        click.echo("Failed to get valid input. Exiting.")
        sys.exit(1)

    print(newlines_after * "\n", end="")
    return out


def get_input_from_list(
    title: str,
    options: List[str],
    fallback: str = None,
    fallback_index: int = 0,
    fallback_enter_manually=False,
    default_item: str = None,
    default_index=-1,
    attempts: int = 3,
    newlines_before=1,
    newlines_after=1,
    fallback_uppercase=True,
    validator: Callable = lambda i: True,
    validation_failure_msg="Input failed validation. Please try again.",
) -> SelectedOption:
    if fallback or fallback_enter_manually:
        if fallback_enter_manually:
            fallback = "enter value manually"

        if fallback_uppercase:
            fallback = fallback.upper()

        if not re.match(r"^\s*<[^<^>]*>\s*$", fallback):
            fallback = re.sub(r"^\s*(.*)\s*$", r"<\1>", fallback)

        if fallback_index < 0:
            options.append(fallback)
        else:
            options.insert(fallback_index, fallback)

    if default_index == -1:
        default_index = fallback_index if fallback_index >= 0 else 0

    out = (
        "\n" * newlines_before
        + f"### {title} ###\n"
        + "\n".join(f"[{index}] {item}" for index, item in enumerate(options))
    )
    print(out)
    value = None

    for i in range(attempts):
        chosen = input(
            f"Enter a number from the list to "
            f"choose an option [default={default_index}]: "
        )

        try:
            if not chosen:
                chosen = default_index

            chosen = int(chosen)
            if fallback_enter_manually and (
                chosen == fallback_index
                or (fallback_index < 0 and chosen == len(options) - 1)
            ):
                value = input(
                    "You chose to enter a value manually. Enter your value: "
                ).strip()

            if isinstance(chosen, int) and 0 <= chosen < len(options):
                break
            elif not validator(chosen):
                print(validation_failure_msg)
            elif not fallback_enter_manually:
                print("Not a valid index. Please try again.")
            else:
                break
        except:
            print("Not an integer. Please try again.")
    else:
        click.echo("Failed to get valid input. Exiting.")
        sys.exit(1)

    print(newlines_after * "\n", end="")

    if not value:
        value = options[chosen]

    if chosen == fallback_index or (fallback_index < 0 and chosen == len(options) - 1):
        return SelectedOption.fallback(fallback)

    return SelectedOption.create(value)


def print_header(text: str, hashes=15, newlines: int = 2, newlines_before=0):
    hashes = "#" * hashes
    print(newlines_before * "\n" + f"{hashes} {text} {hashes}", end=newlines * "\n")


def sleep(seconds: int):
    time.sleep(seconds)
