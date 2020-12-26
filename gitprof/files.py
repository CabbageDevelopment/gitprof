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
import json
import os
import sys
import traceback
from dataclasses import dataclass
from json import JSONEncoder
from os.path import join
from typing import List, Any, Dict, Optional

config_dir = os.path.expanduser(r"~\AppData\Local\gitprof")
os.makedirs(config_dir, exist_ok=True)

config_file = join(config_dir, "config.json")


class ProfileEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        out = o.__dict__

        return out

    def decode(self, item: Dict) -> "Profile":
        _dict = json.loads(item)
        out = []

        profiles = _dict.get("profiles")
        for p in profiles:
            try:
                out.append(
                    Profile(
                        p["name"],
                        p["ssh_key"],
                        git_name=p.get("git_name"),
                        git_email=p.get("git_email"),
                        service=p.get("service"),
                    )
                )
            except:
                print(f"Warning: bad profile.")

        return out


@dataclass
class Profile:
    name: str
    ssh_key: str
    git_name: str
    git_email: str
    service: str

    def __init__(
        self, name=None, ssh_key=None, git_name=None, git_email=None, service=None
    ):
        self.name = name
        self.ssh_key = ssh_key
        self.git_name = git_name
        self.git_email = git_email
        self.service = service

    def __str__(self):
        out = []
        for key, value in self.__dict__.items():
            if key == "name":
                continue

            out.append(f"{key}='{value}'")

        lines = ",\n".join(f"\t{i}" for i in out)
        return f"\n{self.name} {{\n{lines}\n}}"


@dataclass
class Config:
    profiles: List[Profile] = None

    def __init__(self):
        self.load()

    def load(self):
        if not os.path.exists(config_file):
            return

        with open(config_file, "r") as loaded:
            text = loaded.read()

        try:
            loaded = json.loads(text, cls=ProfileEncoder)
        except:
            traceback.print_exc()
            return

        self.profiles = loaded

    def reload(self):
        self.load()

    def save(self) -> None:
        fields = self.get_fields()
        with open(config_file, "w") as f:
            json.dump(fields, f, indent=4, cls=ProfileEncoder)

    def get_fields(self):
        return self.__dict__

    def add_profile(self, profile: Profile):
        if not self.profiles:
            self.profiles = []

        if profile.name in map(lambda i: i.name, self.profiles):
            print(
                f"Cannot create profile '{profile.name}'; a profile with that name already exists."
            )
            return sys.exit(0)

        self.profiles.append(profile)

    def __str__(self):
        out = ""

        for p in self.profiles:
            out += f"{p}\n"

        return out

    def set_profile(self, profile: Profile) -> None:
        for index, p in enumerate(self.profiles):
            if p.name == profile.name:
                self.profiles[index] = p

    def get_profile(self, name: str) -> Optional[Profile]:
        for p in self.profiles or []:
            if p.name == name:
                return p

    def delete_profile(self, profile_name: str) -> None:
        self.profiles = list(filter(lambda p: p.name != profile_name, self.profiles))

    def get_profiles(self) -> List[Profile]:
        return self.profiles or []

    def get_profile_names(self) -> List[Profile]:
        return list(map(lambda i: i.name, self.get_profiles()))
