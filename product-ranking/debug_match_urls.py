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


def _strip_get_args(url):
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


def _compare_dicts(d1, d2, exclude_fields):
    results = []
    if not d1 or not d2:
        return results
    if exclude_fields is None:
        exclude_fields = []

    if isinstance(d1, list) and isinstance(d2, list):
        len1 = len(d1)
        len2 = len(d2)
        if len1 != len2:
            return 'different length: %s and %s' % (len1, len2)
        t1 = d1[:]
        t2 = d2[:]
        l = len(t1)
        for i in xrange(l-1, -1, -1):
            v1 = t1[i]
            if v1 in t2:
                t2.remove(v1)
                t1.remove(v1)
        if t1 or t2:
            results.append('Not matching lists: %s ----- %s' % (t1, t2))

    if isinstance(d1, dict) and isinstance(d2, dict):
        e_f = set(exclude_fields)
        keys1 = set(d1.keys()) - e_f
        keys2 = set(d2.keys()) - e_f
        # check their length (missing fields?)
        if keys1 != keys2:
            return 'fields: %s, %s' % (list(keys1-keys2), list(keys2-keys1))
        for k in keys1:
            v1, v2 = d1[k], d2[k]
            if isinstance(v1, (list, dict)) and isinstance(v2, (list, dict)):
                res = _compare_dicts(v1, v2, exclude_fields)
                if res:
                    results.append({k: res})
            elif v1 != v2:
                results.append({k: [v1, v2]})
    return results


def _get_mismatching_fields(d1, d2, exclude_fields):
    result = []
    if d1.keys() is None or d2.keys() is None:
        return []
    if exclude_fields is None:
        exclude_fields = []
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
            field = 'Field sets are different!'
            vals = [field, ''] if isinstance(results, (list, tuple))\
                else [results, '']
        print ' '*indent, heading_color, field, basic_color
        print ' '*indent*2, colorama.Fore.YELLOW, '1.', basic_color,  vals[0]
        if len(vals) > 1:
            print ' '*indent*2, colorama.Fore.YELLOW, '2.', basic_color, vals[1]
        print


def collect_human_friendly(results, exclude_fields):
    output = []
    if exclude_fields is None:
        exclude_fields = []
    for element in results:
        if isinstance(element, dict):
            field, vals = element.items()[0]
            if field in exclude_fields:
                continue
        else:  # string error code?
            field = 'Field sets are different!'
            vals = [field, ''] if isinstance(results, (list, tuple))\
                else [results, '']
        #print ' '*indent, heading_color, field, basic_color
        output.append({'field': field, 'f1': vals[0], 'f2': vals[1] if len(vals) > 1 else ''})
    return output


def _start_print():
    colorama.init()
    print colorama.Back.BLACK


def _finish_print():
    print colorama.Back.RESET


def match(f1, f2, fields2exclude=None, strip_get_args=None,
          skip_urls=None, print_output=True):
    total_urls = 0
    matched_urls = 0

    if print_output:
        _start_print()

    f1 = open(f1).readlines()
    f2 = open(f2).readlines()

    try:
        f1 = [json.loads(l.strip()) for l in f1 if l.strip()]
        f2 = [json.loads(l.strip()) for l in f2 if l.strip()]
    except ValueError:
        return {'diff': [], 'total_urls': 0, 'matched_urls': 0}

    result_mismatched = []

    for i, json1 in enumerate(f1):
        if not 'url' in json1:
            continue
        url1 = json1['url']
        if strip_get_args:
            url1 = _strip_get_args(url1)

        total_urls += 1

        if skip_urls:
            if skip_urls in url1:
                continue

        for json2 in f2:
            if not json2:
                continue
            if not 'url' in json2.keys():
                continue
            url2 = json2['url']
            if strip_get_args:
                url2 = _strip_get_args(url2)
            if url1 == url2:
                matched_urls += 1
                # mis_fields = _get_mismatching_fields(json1, json2,
                #                                      fields2exclude)
                mis_fields = _compare_dicts(json1, json2, fields2exclude)
                if mis_fields:
                    if print_output:
                        print 'LINE', i
                        print colorama.Fore.GREEN
                        print_human_friendly(mis_fields, fields2exclude)
                        print colorama.Fore.RESET
                    else:
                        result_mismatched.append({
                            'line': i,
                            'diff': collect_human_friendly(mis_fields, fields2exclude),
                            'data1': json1,
                            'data2': json2,
                        })

    if print_output:
        print 'TOTAL URLS:', total_urls
        print 'MATCHED URLS:', matched_urls

    if print_output:
        _finish_print()

    return {'diff': result_mismatched, 'total_urls': total_urls,
            'matched_urls': matched_urls}


if __name__ == '__main__':
    args = parse_cmd_args()
    fields2exclude = _parse_exclude_fields_from_arg(
        args.exclude_fields if args.exclude_fields else '')
    result = match(
        f1=args.f1, f2=args.f2,
        fields2exclude=fields2exclude,
        strip_get_args=args.strip_get_args,
        skip_urls=args.skip_urls,
        print_output=False
    )
    print '*' * 100
    # print result['diff'][0]['diff']
    print result['diff'][0].keys()