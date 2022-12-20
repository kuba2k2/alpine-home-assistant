#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

from .interface import InterfaceMixin
from .utils import cmd, get_description, dmesg, kstart, slugify


class SystemdInterface(InterfaceMixin):
    """
    <node>
        <interface name="org.freedesktop.systemd1.Manager">
            <method name="StartUnit">
                <arg type="s" name="name" direction="in" />
                <arg type="s" name="mode" direction="in" />
                <arg type="s" name="response" direction="out" />
            </method>
            <method name="StopUnit">
                <arg type="s" name="name" direction="in" />
                <arg type="s" name="mode" direction="in" />
                <arg type="s" name="response" direction="out" />
            </method>
            <method name="ReloadUnit">
                <arg type="s" name="name" direction="in" />
                <arg type="s" name="mode" direction="in" />
                <arg type="s" name="response" direction="out" />
            </method>
            <method name="RestartUnit">
                <arg type="s" name="name" direction="in" />
                <arg type="s" name="mode" direction="in" />
                <arg type="s" name="response" direction="out" />
            </method>
            <method name="ListUnits">
                <arg type="a(ssssssouso)" name="response" direction="out" />
            </method>
            <method name="Reboot">
                <annotation name="org.freedesktop.systemd1.Privileged" value="true"/>
            </method>
            <method name="PowerOff">
                <annotation name="org.freedesktop.systemd1.Privileged" value="true"/>
            </method>
            <method name="Halt">
                <annotation name="org.freedesktop.systemd1.Privileged" value="true"/>
            </method>
            <property type="t" name="FirmwareTimestamp" access="read" />
            <property type="t" name="FirmwareTimestampMonotonic" access="read" />
            <property type="t" name="LoaderTimestamp" access="read" />
            <property type="t" name="LoaderTimestampMonotonic" access="read" />
            <property type="t" name="KernelTimestamp" access="read" />
            <property type="t" name="KernelTimestampMonotonic" access="read" />
            <property type="t" name="InitRDTimestamp" access="read" />
            <property type="t" name="InitRDTimestampMonotonic" access="read" />
            <property type="t" name="UserspaceTimestamp" access="read" />
            <property type="t" name="UserspaceTimestampMonotonic" access="read" />
            <property type="t" name="FinishTimestamp" access="read" />
            <property type="t" name="FinishTimestampMonotonic" access="read" />
        </interface>
    </node>
    """

    def StartUnit(self, name: str, _mode: str):
        cmd("service", name, "start")

    def StopUnit(self, name: str, _mode: str):
        cmd("service", name, "stop")

    def ReloadUnit(self, name: str, _mode: str):
        cmd("service", name, "restart")

    def RestartUnit(self, name: str, _mode: str):
        cmd("service", name, "restart")

    def ListUnits(self) -> list[tuple]:
        status = cmd("rc-status", "-s")
        out = []
        for line in status:
            parts = list(filter(None, line.split(" ")))
            name = parts[0]
            description = get_description(name)
            started = "started" in parts
            starting = "starting" in parts
            stopped = "stopped" in parts
            stopping = "stopping" in parts
            unit = (
                name,
                description or "",
                "loaded",
                "active"
                if started
                else "activating"
                if starting
                else "inactive"
                if stopped
                else "deactivating"
                if stopping
                else "failed",
                "running" if started else "dead",
                "",
                "/org/freedesktop/systemd1/unit/" + slugify(name),
                0,
                "",
                "/",
            )
            out.append(unit)
        return out

    def Reboot(self):
        cmd("reboot")

    def PowerOff(self):
        cmd("poweroff")

    def Halt(self):
        cmd("halt")

    @property
    def FirmwareTimestampMonotonic(self) -> int:
        return 0

    @property
    def FirmwareTimestamp(self) -> int:
        return 0

    @property
    def LoaderTimestampMonotonic(self) -> int:
        return 0

    @property
    def LoaderTimestamp(self) -> int:
        return 0

    @property
    def KernelTimestampMonotonic(self) -> float:
        return dmesg("") * 1e6

    @property
    def KernelTimestamp(self) -> float:
        return kstart() * 1e6 + self.KernelTimestampMonotonic

    @property
    def InitRDTimestampMonotonic(self) -> float:
        return dmesg("Run /init as init process") * 1e6

    @property
    def InitRDTimestamp(self) -> float:
        return kstart() * 1e6 + self.InitRDTimestampMonotonic

    @property
    def UserspaceTimestampMonotonic(self) -> float:
        return dmesg("Alpine Init") * 1e6

    @property
    def UserspaceTimestamp(self) -> float:
        return kstart() * 1e6 + self.UserspaceTimestampMonotonic

    @property
    def FinishTimestampMonotonic(self) -> float:
        return dmesg("crng init done") * 1e6

    @property
    def FinishTimestamp(self) -> float:
        return kstart() * 1e6 + self.FinishTimestampMonotonic
