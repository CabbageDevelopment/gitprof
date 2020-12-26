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
from typing import List, Optional

from gitprof.files import Config


def get_services() -> List[str]:
    default = ["GitHub", "GitLab", "Bitbucket", "Self-hosted"]
    others = list(
        filter(
            lambda i: (i and i != "None"),
            map(lambda i: i.service, Config().get_profiles()),
        )
    )

    out = default + others
    seen = set()

    return [i for i in out if not (i in seen or seen.add(i))]


def get_ssh_url_for(service: str) -> Optional[str]:
    if service.lower() == "github":
        return "https://github.com/settings/keys"
    elif service.lower() == "gitlab":
        return "https://gitlab.com/-/profile/keys"
    elif service.lower() == "bitbucket":
        return "https://bitbucket.org/account/settings/ssh-keys/"

    return None
