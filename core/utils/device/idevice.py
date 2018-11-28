class IDevice(object):
    @staticmethod
    def __run_adb_command(command):
        pass

    @staticmethod
    def get_devices():
        return []

    @staticmethod
    def is_text_visible(id, text):
        return False

    @staticmethod
    def get_screen(id, file_path):
        return None
