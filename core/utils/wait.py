import time


class Wait(object):
    @staticmethod
    def until(condition, timeout=100, period=1, *args, **kwargs):
        """
        Wait until condition is satisfied.
        :rtype: bool
        :returns: True if condition is satisfied before timeout, otherwise False.
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            if condition(*args, **kwargs):
                return True
            time.sleep(period)
        return False
