from core.log.log import Log


class PerfUtils(object):
    @staticmethod
    def is_value_in_range(actual, expected, tolerance=0.25):
        """
        Check if value is in range
        :param actual: Number value.
        :param expected: Number value.
        :param tolerance: Tolerance as percent.
        """
        Log.info("Actual value: " + str(actual))
        Log.info("Expected value: " + str(expected))
        return expected - (expected * tolerance) <= actual <= expected + (
            expected * tolerance)

    @staticmethod
    def get_average_time(operation, retry_count=3, *args, **kwargs):
        """
        Get average time of Run.command() operation.
        :param operation: lambda function that returns ProcessInfo object (for example Run.command("ls")).
        :param retry_count: Retry count.
        :param args:
        :param kwargs:
        :return: Average execution time in seconds.
        """
        total_time = 0
        for _ in range(0, retry_count):
            total_time = total_time + operation(*args, **kwargs).duration
        return total_time / retry_count
