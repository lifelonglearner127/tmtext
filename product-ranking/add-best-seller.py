#!/usr/bin/env python2
# vim:fileencoding=UTF-8

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import json


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Merge spider outputs to populate best seller ranking as an'
                    ' additional field.',
        version="%(prog)s 0.1")
    parser.add_argument('ranking', help="a JSONLines file.")
    parser.add_argument('best_seller_ranking',
                        help="a JSONLines file ranked by best seller.")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Load best seller ranked products.
    best_seller_rankings = {}
    with open(args.best_seller_ranking) as best_seller_f:
        for line in best_seller_f:
            product = json.loads(line)
            url = product['url']
            ranking = product['ranking']
            if url in best_seller_rankings \
                    and ranking != best_seller_rankings[url]:
                print("Found product with more than one best sellers ranking."
                      " '%s' has %d and %d. Using lowest."
                      % (url, best_seller_rankings[url], ranking),
                      file=sys.stderr)
                ranking = min(best_seller_rankings[url], ranking)
            best_seller_rankings[url] = ranking

    # Update first data set with best seller's ranking.
    with open(args.ranking) as ranking_f:
        for line in ranking_f:
            product = json.loads(line)
            product['best_seller_ranking'] = best_seller_rankings.get(
                product['url'])

            json.dump(product, sys.stdout, sort_keys=True)
            sys.stdout.write(b'\n')

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
