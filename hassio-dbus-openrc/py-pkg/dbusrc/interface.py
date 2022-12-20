#  Copyright (c) Kuba Szczodrzyński 2022-8-22.

from pydbus.bus import Bus, SystemBus

from dbusrc.utils import slugify

bus: Bus = SystemBus()
objects: dict[str, object] = {}


class InterfaceMixin:
    bus_name: str = None
    path: list[str] = None

    def __init__(self, path: list[str], bus_name: str = None):
        self.bus_name = bus_name
        self.path = path

    def register(self, interface: type, path: str) -> str:
        path = list(filter(None, path.split("/")))
        # if not self.bus_name:
        path = self.path + path
        path_str = "/" + "/".join(slugify(el) for el in path)
        if path_str in objects:
            return path_str
        obj = interface(path)
        print("Registering", interface.__name__, "on", path_str)
        if not self.path:
            bus.publish(".".join(path))
        # else:
        bus.register_object(path_str, obj, interface.__doc__)
        objects[path_str] = obj
        return path_str
