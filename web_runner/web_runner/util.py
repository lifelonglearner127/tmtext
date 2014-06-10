import fcntl
import os
import select


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
