from datetime import timedelta
import signal


class TimeoutException(Exception):
    pass


def top_emotion(emotions):
    if type(emotions) != dict or len(emotions) == 0:
        return None

    return sorted(emotions.items(), key=lambda x: x[1], reverse=True)[0]


def are_rectangles_overlapping(rect1, rect2):
    """Returns `True` if two rectangles are overlapping.

    >>> rectangle1 = (0, 0, 10, 10)
    >>> rectangle2 = (0, 10, 20, 20)
    >>> rectangle3 = (11, 11, 20, 20)
    >>> assert are_rectangles_overlapping(rectangle1, rectangle2)
    >>> assert are_rectangles_overlapping(rectangle2, rectangle3)
    >>> assert not are_rectangles_overlapping(rectangle1, rectangle3)
    """
    try:
        f1_x1, f1_x2 = rect1[0], rect1[0] + rect1[2]
        f1_y1, f1_y2 = rect1[1], rect1[1] + rect1[3]

        f2_x1, f2_x2 = rect2[0], rect2[0] + rect2[2]
        f2_y1, f2_y2 = rect2[1], rect2[1] + rect2[3]
    except (TypeError, IndexError):
        msg = "Both parameters must be list-like elements with >=4 elements."
        raise AttributeError(msg)

    op_x1 = f1_x1 <= f2_x1 <= f1_x2
    op_x2 = f2_x1 <= f1_x1 <= f2_x2
    op_x = op_x1 or op_x2

    op_y1 = f2_y1 <= f1_y1 <= f2_y2
    op_y2 = f1_y1 <= f2_y1 <= f1_y2
    op_y = op_y1 or op_y2

    return op_x and op_y


class timeout(object):
    """A context manager designed to abort an action after given amount of
    time. It takes the same arguments as datetime.timedelta class. Here's a
    functional example:

    >>> import time
    >>> start_time = time.time()
    >>> with timeout(seconds=1): \
            time.sleep(3)
    >>> end_time = time.time()
    >>> assert (end_time - start_time) < 2
    """
    def __init__(self, raise_exception=False, **kwargs):
        self.old_handler = None
        self.raise_exception = raise_exception
        self.seconds = timedelta(**kwargs).seconds

    def __enter__(self):
        self.old_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, self.new_handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.old_handler)

        is_timeout = exc_type and exc_type != TimeoutException
        if not self.raise_exception and is_timeout:
            return False
        return True

    @staticmethod
    def new_handler(signo, frame):
        raise TimeoutException()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
