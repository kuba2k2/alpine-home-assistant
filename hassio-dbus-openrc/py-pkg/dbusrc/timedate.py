#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

from datetime import datetime
from glob import glob
from time import time

from .interface import InterfaceMixin
from .utils import cmd, cmdret, cmdstr


class TimedateInterface(InterfaceMixin):
    """
    <node>
        <interface name="org.freedesktop.timedate1">
            <method name="SetTime">
                <arg type="x" name="usec_rtc" direction="in"/>
                <arg type="b" name="relative" direction="in"/>
                <arg type="b" name="interactive" direction="in"/>
            </method>
            <method name="SetNTP">
                <arg type="b" name="use_ntp" direction="in"/>
                <arg type="b" name="interactive" direction="in"/>
            </method>
            <property type="s" name="Timezone" access="read" />
            <property type="b" name="LocalRTC" access="read" />
            <property type="b" name="CanNTP" access="read" />
            <property type="b" name="NTP" access="read" />
            <property type="b" name="NTPSynchronized" access="read" />
            <property type="t" name="TimeUSec" access="read" />
            <property type="t" name="RTCTimeUSec" access="read" />
        </interface>
    </node>
    """

    def SetTime(self, usec_rtc: int, _relative: bool, _interactive: bool):
        date = datetime.fromtimestamp(usec_rtc / 1e6)
        cmd("date", "-s", date.strftime("%Y-%m-%d %H:%M:%S"))

    def SetNTP(self, use_ntp: bool, _interactive: bool):
        cmd("service", "chronyd", "start" if use_ntp else "stop")
        cmd("rc-update", "add" if use_ntp else "del", "chronyd")

    @property
    def Timezone(self) -> str:
        zones = glob("/etc/zoneinfo/./**/*")
        if zones:
            return zones[0].split("./")[1]
        return ""

    @property
    def LocalRTC(self) -> bool:
        return False

    @property
    def CanNTP(self) -> bool:
        return cmdret("service", "-e", "chronyd") == 0

    @property
    def NTP(self) -> bool:
        return "chronyd" in cmdstr("rc-update", "show", "boot", "default")

    @property
    def NTPSynchronized(self) -> bool:
        return "started" in cmdstr("service", "chronyd", "status")

    @property
    def TimeUSec(self) -> float:
        return float(cmdstr("date", "+%s.%N")) * 1e6

    @property
    def RTCTimeUSec(self) -> float:
        return time() * 1e6
