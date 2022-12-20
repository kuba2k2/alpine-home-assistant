#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

from .interface import InterfaceMixin
from .utils import cmd, cmdstr, getprop


class HostnameInterface(InterfaceMixin):
    """
    <node>
        <interface name="org.freedesktop.hostname1">
            <method name="SetHostname">
                <arg type="s" name="hostname" direction="in"/>
                <arg type="b" name="interactive" direction="in"/>
            </method>
            <property type="s" name="Hostname" access="read" />
            <property type="s" name="StaticHostname" access="read" />
            <property type="s" name="PrettyHostname" access="read" />
            <property type="s" name="DefaultHostname" access="read" />
            <property type="s" name="IconName" access="read" />
            <property type="s" name="Chassis" access="read" />
            <property type="s" name="Deployment" access="read" />
            <property type="s" name="Location" access="read" />
            <property type="s" name="KernelName" access="read" />
            <property type="s" name="KernelRelease" access="read" />
            <property type="s" name="KernelVersion" access="read" />
            <property type="s" name="OperatingSystemPrettyName" access="read" />
            <property type="s" name="OperatingSystemCPEName" access="read" />
            <property type="s" name="HomeURL" access="read" />
        </interface>
    </node>
    """

    def SetHostname(self, hostname: str, _interactive: bool):
        cmd("hostname", hostname)

    @property
    def Hostname(self) -> str:
        return cmdstr("hostname")

    @property
    def StaticHostname(self) -> str:
        with open("/etc/hostname") as f:
            hostname = f.read().strip()
        return hostname

    @property
    def PrettyHostname(self) -> str:
        return ""

    @property
    def DefaultHostname(self) -> str:
        return "alpine"

    @property
    def IconName(self) -> str:
        return "computer-server"

    @property
    def Chassis(self) -> str:
        return "server"

    @property
    def Deployment(self) -> str:
        return ""

    @property
    def Location(self) -> str:
        return ""

    @property
    def KernelName(self) -> str:
        return cmdstr("uname", "-s")

    @property
    def KernelRelease(self) -> str:
        return cmdstr("uname", "-r")

    @property
    def KernelVersion(self) -> str:
        return cmdstr("uname", "-v")

    @property
    def OperatingSystemPrettyName(self) -> str:
        return getprop("/etc/os-release", "PRETTY_NAME")

    @property
    def OperatingSystemCPEName(self) -> str:
        return ""

    @property
    def HomeURL(self) -> str:
        return "https://alpinelinux.org/"
