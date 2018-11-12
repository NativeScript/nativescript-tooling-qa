import time


class Wait(object):
    @staticmethod
    def until(condition, timeout=60, period=1, *args, **kwargs):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if condition(*args, **kwargs):
                return True
            time.sleep(period)
        return False
