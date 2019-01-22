# noinspection PyShadowingBuiltins
class EmulatorInfo(object):
    def __init__(self, avd=None, os_version=None, port=None, emu_id=None):
        self.avd = avd
        self.os_version = os_version
        self.port = port
        self.emu_id = emu_id
