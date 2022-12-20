#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

import json
import re
from subprocess import PIPE, Popen
from time import time
from urllib.parse import quote_plus

DESCRIPTIONS: dict[str, str] = {}
DMESG: list[tuple[float, str]] = []


def cmd(*args: str) -> list[str]:
    print("Running:", *args)
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    p.wait()
    if p.returncode != 0:
        print("Non-zero return code:", p.returncode)
        raise RuntimeError(p.stderr.read())
    return [line.decode() for line in p.stdout.read().splitlines() if line.strip()]


def cmdstr(*args: str) -> str:
    return "\n".join(cmd(*args))


def cmdjson(*args: str) -> dict:
    return json.loads("\n".join(cmd(*args)))


def cmdret(*args: str) -> int:
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    p.wait()
    return p.returncode


def getprop(file: str, key: str) -> str:
    with open(file) as f:
        data = f.read()
    match = re.search(key + r"\s*=\s*\"?(.+)\"?", data)
    if not match:
        return ""
    return match.group(1).rstrip('"')


def slugify(s: str) -> str:
    return quote_plus(s.replace("-", "_2d")).replace("%", "_")


def get_description(unit: str) -> str:
    if unit in DESCRIPTIONS:
        return DESCRIPTIONS[unit]
    DESCRIPTIONS[unit] = getprop(f"/etc/init.d/{unit}", "description")
    return DESCRIPTIONS[unit]


def dmesg(search: str) -> float:
    if not DMESG:
        with open("/var/log/dmesg", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        for line in lines:
            parts = line[1:].split("] ", maxsplit=2)
            sec = float(parts[0].strip())
            msg = parts[1].strip()
            DMESG.append((sec, msg))
    for sec, line in DMESG:
        if search in line:
            return sec
    return 0


def kstart() -> float:
    with open("/proc/uptime") as f:
        uptime = f.read().split(" ")[0]
        uptime = float(uptime)
    now = time()
    return now - uptime
