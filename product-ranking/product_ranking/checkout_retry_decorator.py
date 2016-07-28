import time
from functools import wraps
import traceback
import inspect
import logging
import socket

def retry_func(ExceptionToCheck, tries=15, delay=3):
    """Retry call for decorated function"""

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('RETRY_DECORATOR')

    def ext_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "Exception - {}, retrying method {} in {} seconds, retries left: {}...".format(
                        str(e), f.__name__, mdelay, mtries)
                    func_args = "Arguments: {}".format(inspect.getargspec(f))
                    trb = "################### TRACEBACK HERE ############## \n {} ################".format(
                        traceback.format_exc())
                    if logger:
                        logger.warning(msg)
                        logger.warning(func_args)
                        logger.warning(trb)
                    else:
                        print traceback.format_exc()
                        print msg
                        print func_args
                    time.sleep(mdelay)
                    mtries -= 1
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return ext_retry