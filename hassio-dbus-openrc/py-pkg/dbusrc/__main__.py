#!/usr/bin/python3

#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

from glob import glob
from os.path import basename

from gi.repository import GLib

from dbusrc.hostname import HostnameInterface
from dbusrc.interface import InterfaceMixin
from dbusrc.systemd import SystemdInterface
from dbusrc.timedate import TimedateInterface
from dbusrc.utils import get_description

if __name__ == "__main__":
    for unit in glob("/etc/init.d/*"):
        get_description(basename(unit))

    loop = GLib.MainLoop()

    root = InterfaceMixin(path=[])
    root.register(SystemdInterface, "/org/freedesktop/systemd1")
    root.register(HostnameInterface, "/org/freedesktop/hostname1")
    root.register(TimedateInterface, "/org/freedesktop/timedate1")

    loop.run()
