"""
Version utils
"""


class Version(object):
    @staticmethod
    def get(version):
        """
        Convert version string to float.
        Will also trim version like this:
        - 13.2.2 will be trimmed to 13.2
        :param version: Version string.
        :return: Version as float.
        """
        split = version.split('.')
        if len(split) > 1:
            return float(split[0] + '.' + split[1])
        else:
            return float(split[0])
