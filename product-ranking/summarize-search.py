#!/usr/bin/env python2
# vim:fileencoding=UTF-8
# TODO Add first page size per site.

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

from itertools import chain
import csv
import collections
import json


def parse_arguments(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Summarize search data.',
                                     version="%(prog)s 0.1")
    #"usage: %prog [options] output-file data-file [data-file ...]",
    parser.add_argument('-f', '--filter', help="filter on <property>=<value>")
    parser.add_argument('output', help="the CSV output file.")
    parser.add_argument('inputs', nargs='+', help="the JSON line input files.")

    return parser.parse_args(argv)


def main(argv=None):
    """main([argv]):int

    Optionaly recieves the argument vector. If it is not provided,
    sys.argv is used.
    Returns the return status code.
    """
    args = parse_arguments(argv)

    if args.filter:
        prop, value = args.filter.split('=')

    data = collections.defaultdict(lambda: collections.defaultdict(list))
    for jl in chain(*map(open, args.inputs)):
        rec = json.loads(jl)
        if not args.filter \
                or prop in rec and rec[prop].lower() == value.lower():
            data[rec['search_term']][rec.get('brand', '').lower()].append(rec)

    writer = csv.writer(open(args.output, 'w'))
    writer.writerow(['site', 'search term', 'brand', 'total results',
                     'rankings', 'on first page'])
    for st, brands in data.items():
        for brand, recs in brands.items():
            rankings = sorted(r['ranking'] for r in recs)
            on_first_pag = sum(1 for r in rankings if r <= 16)
            writer.writerow(['walmart.com', st, brand.capitalize(),
                             recs[0]['total_matches'], rankings,
                             "%d/16" % on_first_pag])

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
