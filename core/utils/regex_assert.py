"""
Smart assert method for regex.
"""
import re


class RegexAssert(object):
    @staticmethod
    def regex_assert(actual, expected, error_message=""):
        """
        Assert using regex.
        :param actual: string containing actual result.
        :param expected: string containing expected result.
        :param error_message: string containing error message.
        Useful tool for testing creating and testing regex https://regex101.com/ . Just select Flavor python.
        """
        result = re.search(expected, actual, re.IGNORECASE | re.MULTILINE)

        if error_message != "":
            assert result, error_message
        else:
            error_message = "Expected Result: '" + expected + "' not found! Actual Data: " + actual
            assert result, error_message
