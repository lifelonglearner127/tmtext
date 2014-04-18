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
import sys


def parse_arguments(argv=None):
    if argv is None:
        argv = sys.argv

    from optparse import OptionParser
    parser = OptionParser(
        "usage: %prog [options] output-file data-file [data-file ...]",
        version="%prog v0.1")
    parser.add_option('-f', '--filter', help="filter on <property>=<value>")

    options, args = parser.parse_args(argv[1:])

    if len(args) > 2:
        parser.error("Need more arguments.")

    output_fn = args[0]
    data_fns = args[1:]
    return options, output_fn, data_fns


def main(argv=None):
    """main([argv]):int

    Optionaly recieves the argument vector. If it is not provided,
    sys.argv is used.
    Returns the return status code.
    """
    options, output_fn, data_fns = parse_arguments(argv)

    if options.filter:
        prop, value = options.filter.split('=')

    data = collections.defaultdict(lambda: collections.defaultdict(list))
    for jl in chain(*map(open, data_fns)):
        rec = json.loads(jl)
        if not options.filter \
                or prop in rec and rec[prop].lower() == value.lower():
            data[rec['search_term']][rec.get('brand', '').lower()].append(rec)

    writer = csv.writer(open(output_fn, 'w'))
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
    sys.exit(main())
