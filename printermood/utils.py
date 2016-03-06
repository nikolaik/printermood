from datetime import timedelta
import signal


class TimeoutException(Exception):
    pass


def top_emotion(emotions):
    if type(emotions) != dict or len(emotions) == 0:
        return None

    return sorted(emotions.items(), key=lambda x: x[1], reverse=True)[0]


class timeout(object):
    """A context manager designed to abort an action after given amount of
    time. It takes the same arguments as datetime.timedelta class. Here's a
    functional example:

    >>> start_time = time.time()
    >>> with timeout(seconds=3):
    >>>     time.sleep(5)
    >>> end_time = time.time()
    >>> assert (end_time - start_time) < 4
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
