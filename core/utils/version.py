"""
Version utils
"""


class Version(object):
    @staticmethod
    def get(version):
        """
        Convert version string to float.
        :param version: Version string.
        :return: Version as float.
        """
        split = version.split('.')
        if len(split) > 1:
            return float(split[0] + '.' + split[1])
        else:
            return float(split[0])
