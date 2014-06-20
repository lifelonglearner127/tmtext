import fcntl
import logging
import os
import select


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
