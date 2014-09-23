import fcntl
import logging
import os
import select
import pickle
import zlib
import base64
import datetime


FINISH = 'finished'
UNAVAILABLE = 'unavailable'
RUNNING = 'running'
PENDING = 'pending'


class RequestsLinePumper:
    """Writes lines from a requests' request into a file like object.

    This is not an asynchronous Pumper but will block only for small chunks.
    """

    def __init__(self, req, dest_fd):
        """
        :param req: Requests' request object.
        :param dest_fd: FD to write to.
        """
        self._req = req
        self._req_lines_iter = req.iter_lines()
        self._dest_fd = dest_fd

        self._data_left = True

        #fcntl.fcntl(dest_fd, fcntl.F_SETFL, os.O_NONBLOCK)

        self._log = logging.getLogger(__file__ + '.' + type(self).__name__)

    def pump(self):
        """Read a line from the request and writes it to the destination.

        :returns: If there's possibly more data left.
        """
        if not self._data_left:
            return False

        _, write_ready, _ = select.select([], [self._dest_fd], [], 0)
        if not write_ready:
            return True

        for line in self._req_lines_iter:
            if line:  # Filter Keep-Alives.
                # FIXME: This may block.
                os.write(self._dest_fd, line)
                self._log.info("Pumped %s bytes.", len(line))
                return True

        self._data_left = False
        return False


def pump(input_fd, output_fd, max_buffer_size=1024):
    """Pumps data from a pipe into another.

    This class implements a generator that will take whatever data is available
    from the input pipe and write as much as possible into the output pipe
    without blocking.
    When there is no data flow, the generator will yield.
    When the input is exhausted, the generator will finish.

    :param input_fd: File descriptor to read from.
    :param output_fd: File descriptor to write to.
    :param max_buffer_size: How much data to keep in memory for writing. Also,
                            no more than this amount of data will be read and
                            written in one iteration.
    :type max_buffer_size: int
    """
    # Set FDs to non-blocking.
    fcntl.fcntl(input_fd, fcntl.F_SETFL, os.O_NONBLOCK)
    fcntl.fcntl(output_fd, fcntl.F_SETFL, os.O_NONBLOCK)

    data = b""
    while True:
        read_ready, write_ready, _ = select.select(
            [input_fd], [output_fd], [], 0)

        read, written = 0, 0

        data_size = len(data)
        if read_ready and data_size < max_buffer_size:
            data += os.read(input_fd, max_buffer_size - data_size)
            read = len(data) - data_size

        if data and write_ready:
            written = os.write(output_fd, data)
            data = data[written:]

        yield read, written


def encode_ids(ids):
    return base64.urlsafe_b64encode(
        zlib.compress(
            pickle.dumps(ids, pickle.HIGHEST_PROTOCOL),
            zlib.Z_BEST_COMPRESSION))


def decode_ids(s):
    return pickle.loads(zlib.decompress(base64.urlsafe_b64decode(
        # Pyramid will automatically decode it as Unicode but it's ASCII.
        s.encode('ascii'))))


def get_request_status(req, jobids_status):
    """Return the status of a REST command or spider request

    Parameters:
      . req: dictionary structure representing a REST request. 
        The structure is the one returned by db.get_request and
        db.get_last_requests
      . jobids_status: Dictionary containing the status of each
        request as it is returned by 
        scrapyd.ScrapydInterface.scrapyd_interf.get_jobs
    """
    final_status = FINISH
    for jobid in req['jobids']:
        # Set the final status
        if not jobid in jobids_status:
            final_status = UNAVAILABLE
        else:
            current_status = jobids_status[jobid]['status']
            if current_status == RUNNING:
                if final_status != UNAVAILABLE:
                    final_status = RUNNING
            elif current_status == PENDING:
                if final_status not in (UNAVAILABLE, RUNNING):
                    final_status = PENDING
            elif current_status == FINISH:
                pass    # Default option
    
    return final_status


def string2datetime(string, format='%Y-%m-%d %H:%M:%S.%f'):
    """Convert a string to datetime.datetime"""

    try:
        date = datetime.datetime.strptime(string, format)
    except ValueError:
        date = None

    return date


def string_from_local2utc(string, format='%Y-%m-%d %H:%M:%S.%f'):
    """Convert a string with localtime to UTC"""
    try:
        offset = datetime.datetime.utcnow() - datetime.datetime.now()
        local_datetime = datetime.datetime.strptime(string, format)
        result_utc_datetime = local_datetime + offset 
        ret = result_utc_datetime.strftime(format)
    except ValueError:
        ret = None

    return ret


def dict_filter(source, items):
    '''Given a source dictionary, returns a new one with a subset of the original

    items is a list of list than conteins the info of the new dictionary 
    structure to be returned.  For example:
    source = {"queues": {
                        "product_ranking": {"running": 0, 
                                            "finished": 0, 
                                            "pending": 0
                                            }
                        }, 
              "scrapyd_projects": ["product_ranking"], 
              "scrapyd_alive": true,
            }
    items = [ ['name1', 'queues'], 
              ['name2', 'queues.product_ranking],
              ['name3', 'queues.product_ranking.running]
            ]

    The returned dictionary should be:
    {"name2": {"running": 0, 
               "finished": 0, 
               "pending": 0}, 
     "name3": 0, 
     "name1": { "product_ranking": {"running": 0, 
                                    "finished": 0, 
                                    "pending": 0}
              }
    }
    '''

    ret = {}

    for item in items:
        if len(item) <> 2:
            continue
        [name, props] = item
        try:
            ret[name] = reduce((lambda x, y: x.get(y)), props.split('.'), source)
        except:
            continue

    return ret

# vim: set expandtab ts=4 sw=4:
