"""
A wrapper around java.
"""
from core.utils.process import Run
from core.utils.version import Version


class Java(object):
    @staticmethod
    def version():
        result = Run.command('java -version')
        return Version.get(result.output.split('"')[1])
