"""
A wrapper around java.
"""
from core.utils.run import run
from core.utils.version import Version


class Java(object):
    @staticmethod
    def version():
        """
        Java version.
        :rtype: float
        """
        result = run('java -version')
        return Version.get(result.output.split('"')[1])
