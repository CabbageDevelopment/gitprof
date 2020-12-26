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
from typing import List

from github import Github, GitAuthor, GitCommit
from github.Repository import Repository

g = Github()


def get_name_and_email(username: str):
    user = g.get_user(username)
    repos: List[Repository] = user.get_repos()

    name, email = None, None

    for r in repos:
        commits = r.get_commits(author=user)
        size = commits.totalCount

        if size <= 0:
            continue

        last_commit: GitCommit = commits[size - 1].commit
        author: GitAuthor = last_commit.author

        name = author.name
        email = author.email

        if name and email:
            break

    return name, email
