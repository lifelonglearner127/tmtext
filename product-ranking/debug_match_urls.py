#
# Using this, you can compare output of 2 different versions of the same spider.
# It will compare the data for the same URLs, and print out differences.
#

from pprint import pprint
import json
import argparse

import colorama  # pip install colorama


def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--f1")  # input .JL file 1
    parser.add_argument("--f2")  # input .JL file 2
    parser.add_argument(
        "--strip_get_args", default=False, required=False)  # exclude GET args from URL?
    parser.add_argument(
        "--exclude_fields", default=False
    )  # do not compare these fields (separator: comma)
    parser.add_argument(
        "--skip_urls", default=None
    )  # skip URLs containing this substring
    return parser.parse_args()


def strip_get_args(url):
    return url.rsplit('/', 1)[0]


def unify_br(br):
    return br.replace("u'", '').replace("'", '').replace(' ', '')


def _parse_exclude_fields_from_arg(arg):
    return [f.strip() for f in arg.split(',')]


def _list_diff(l1, l2):
    result = []
    for _l in l1:
        if not _l in l2:
            result.append(_l)
    if _l in l2:
        if not _l in l1:
            result.append(_l)
    return list(set(result))


def _get_mismatching_fields(d1, d2, exclude_fields):
    result = []
    # check their length (missing fields?)
    keys1 = set([key for key in d1.keys() if not key in exclude_fields])
    keys2 = set([key for key in d2.keys() if not key in exclude_fields])
    if len(keys1) != len(keys2):
        return 'length: %s' % [
            f for f in list(keys1)+list(keys2)
            if f not in keys1 or f not in keys2
        ]
    if keys1 != keys2:
        return 'field_names: ' + str(_list_diff(keys1, keys2))
    # now compare values
    for k1, v1 in [(key,value) for key,value in d1.items()
                   if not key in exclude_fields]:
        v2 = d2[k1]
        if k1 == 'buyer_reviews':
            v1 = unify_br(str(v1))
            v2 = unify_br(str(v2))
        if v1 != v2:
            result.append({k1: [v1, v2]})
    return result


def print_human_friendly(
        results, exclude_fields, indent=4,
        heading_color=colorama.Fore.RED,
        basic_color=colorama.Fore.GREEN
):
    for element in results:
        if isinstance(element, dict):
            field, vals = element.items()[0]
            if field in exclude_fields:
                continue
        else:  # string error code?
            field = 'Fiels sets are different!'
            vals = [field, ''] if isinstance(results, (list, tuple))\
                else [results, '']
        print ' '*indent, heading_color, field, basic_color
        print ' '*indent*2, colorama.Fore.YELLOW, '1.', basic_color, vals[0]
        print ' '*indent*2, colorama.Fore.YELLOW, '2.', basic_color, vals[1]
        print


if __name__ == '__main__':
    total_urls = 0
    matched_urls = 0

    colorama.init()
    print colorama.Back.BLACK

    args = parse_cmd_args()
    fields2exclude = _parse_exclude_fields_from_arg(
        args.exclude_fields if args.exclude_fields else '')

    f1 = open(args.f1).readlines()
    f2 = open(args.f2).readlines()
    f1 = [json.loads(l.strip()) for l in f1 if l.strip()]
    f2 = [json.loads(l.strip()) for l in f2 if l.strip()]

    for i, json1 in enumerate(f1):
        if not 'url' in json1:
            continue
        url1 = json1['url']
        if args.strip_get_args:
            url1 = strip_get_args(url1)

        total_urls += 1

        if args.skip_urls:
            if args.skip_urls in url1:
                continue

        for json2 in f2:
            if not json2:
                continue
            if not 'url' in json2.keys():
                continue
            url2 = json2['url']
            if args.strip_get_args:
                url2 = strip_get_args(url2)
            if url1 == url2:
                matched_urls += 1
                mis_fields = _get_mismatching_fields(json1, json2,
                                                     fields2exclude)
                if mis_fields:
                    print 'LINE', i
                    print colorama.Fore.GREEN
                    print_human_friendly(mis_fields, fields2exclude)
                    print colorama.Fore.RESET

    print 'TOTAL URLS:', total_urls
    print 'MATCHED URLS:', matched_urls

    print colorama.Back.RESET