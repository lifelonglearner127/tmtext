from __future__ import division
import os
import math

from pyspecs import given, when, then, the, finish

from web_runner.util import pump


with given.a_pump_and_two_pipes:
    DATA = "Hello world!"
    BUFFER_SIZE = 2

    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    os.write(w1, DATA)

    pumper = pump(r1, w2, max_buffer_size=BUFFER_SIZE)

    with when.its_iterated_once:
        read, written = next(pumper)

        with then.it_should_report_bytes_read:
            the(read).should.equal(BUFFER_SIZE)

        with then.it_should_report_bytes_written:
            the(written).should.equal(BUFFER_SIZE)

        with then.it_should_have_copied_one_block_of_data:
            transmitted = os.read(r2, BUFFER_SIZE)
            the(transmitted).should.equal(DATA[:BUFFER_SIZE])

    with when.its_iterated_until_done:
        transmitted = DATA[:BUFFER_SIZE]  # What was already copied.
        for _ in range(int(math.ceil(len(DATA) / BUFFER_SIZE)) - 1):
            _, written = next(pumper)
            transmitted += os.read(r2, written)

        with then.it_should_have_copied_all_data:
            the(transmitted).should.equal(DATA)


if __name__ == '__main__':
    finish()
