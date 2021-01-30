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

import chdir
from setuptools import setup, find_packages

chdir.here(__file__)
import gitprof

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    dependencies = re.findall(r"^\s*(.+?)\s*$", f.read(), flags=re.MULTILINE)

setup(
    name="gitprof",
    version=gitprof.__version__,
    packages=find_packages(),
    python_requires="~=3.7",
    install_requires=dependencies,
    description="CLI tool which simplifies Git usage with multiple online accounts/services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CabbageDevelopment/gitprof",
    author="Sam McCormack",
    author_email="cabbagedevelopment@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="git profiles github gitlab bitbucket cli tool accounts services",
    project_urls={"Source": "https://github.com/CabbageDevelopment/gitprof"},
    entry_points={"console_scripts": ["gitprof=gitprof:init"]},
)
