#!/usr/bin/env python2
# vim:fileencoding=UTF-8

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import json


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Add extra fields to a product spider output.',
        version="%(prog)s 0.1")

    return parser.parse_args()


def main():
    _ = parse_arguments()

    for line in sys.stdin:
        product = json.loads(line)

        search_term = product['search_term'].lower()
        title = product['title'].lower()

        product['search_term_in_title_exactly'] = search_term in title

        product['search_term_in_title_partial'] = any(
            word in title for word in search_term.split())

        json.dump(product, sys.stdout)
        sys.stdout.write(b'\n')
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
