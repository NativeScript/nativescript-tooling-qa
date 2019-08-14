import unittest
from core.utils.regex_assert import RegexAssert


# noinspection PyMethodMayBeStatic
class RegexAssertTests(unittest.TestCase):

    def test_assert_with_regex(self):
        expected_number = "33"
        actual_data = "test " + expected_number + " test"
        expected_data = r"test \d+ test"
        case_actual_data = "TEST " + expected_number + " TEST"
        multi_line_actual_data = """
        test
        test
        test 33 test
        test
        test
        """
        RegexAssert.regex_assert(actual_data, expected_data)
        RegexAssert.regex_assert(actual_data, actual_data)
        RegexAssert.regex_assert(actual_data, expected_number)
        RegexAssert.regex_assert(actual_data, r"\d+")
        RegexAssert.regex_assert(case_actual_data, actual_data)
        RegexAssert.regex_assert(multi_line_actual_data, r"\d+")
        RegexAssert.regex_assert(multi_line_actual_data, actual_data)

    def test_assert_with_regex_fails_without_error_message(self):
        expected_number = "dd"
        actual_data = "test " + expected_number + " test"
        expected_data = r"test \d+ test"
        exception_message = "Expected Result: 'test \\d+ test' not found! Actual Data: test dd test"
        with self.assertRaises(AssertionError) as error:
            RegexAssert.regex_assert(actual_data, expected_data)
        assertion_error_message = "Default error message is wrong! Log: " + str(error.exception)
        assert exception_message == str(error.exception), assertion_error_message

    def test_assert_with_regex_fails_with_error_message(self):
        expected_number = "dd"
        actual_data = "test " + expected_number + " test"
        expected_data = r"test \d+ test"
        exception_message = "Error Message!"
        with self.assertRaises(AssertionError) as error:
            RegexAssert.regex_assert(actual_data, expected_data, exception_message)
        assertion_error_message = "Error message is wrong! Log: " + str(error.exception)
        assert exception_message == str(error.exception), assertion_error_message


if __name__ == '__main__':
    unittest.main()
