import fnmatch
import os
import bz2
import json


def file_is_bzip2(fname):
    """ Tests if the given file is bzipped """
    if not os.path.exists(fname):
        return
    fh = bz2.BZ2File(fname)
    try:
        _ = fh.next()
        fh.close()
        return True
    except Exception, e:
        fh.close()
        return False


def compress_and_rename_old(fname):
    if file_is_bzip2(fname):
        return  # compressed already
    os.system('bzip2 "%s"' % fname)
    os.rename(fname+'.bz2', fname)
    print '  File compressed:', fname


def uncompress_and_rename_old(fname):
    if not file_is_bzip2(fname):
        return  # uncompressed already
    os.system('bzip2 -d "%s"' % fname)
    if os.path.exists(fname+'.out'):
        os.rename(fname+'.out', fname)
    print '  File uncompressed:', fname


def change_buyer_reviews(line):
    line = line.strip()
    if not 'average_rating' in line:
        return line  # nothing to fix
    line = json.loads(line)
    br = line.get('buyer_reviews', '')
    if not br:
        return line  # nothing no fix
    num_of_reviews = br.get('num_of_reviews', 0)
    average_rating = br.get('average_rating', 0)
    rating_by_star = br.get('rating_by_star', {})
    line['buyer_reviews'] = [num_of_reviews, average_rating, rating_by_star]
    return json.dumps(line)


def validate_2_lines(line1, line2):
    line1 = json.loads(line1)
    line2 = json.loads(line2)
    line1.pop('buyer_reviews')
    line2.pop('buyer_reviews')
    return line1 == line2


def change_br_in_file(fname):
    with open(fname, 'r') as fh:
        lines = fh.readlines()
    lines_replaced = [change_buyer_reviews(line) for line in lines]
    if len(lines_replaced) != len(lines):
        assert False, 'arrays length mismatch!'
    for i in range(len(lines)):
        if not validate_2_lines(lines[i], lines_replaced[i]):
            assert False, 'lines mismatch'
    with open(fname, 'w') as fh:
        for line in lines_replaced:
            fh.write(line.strip()+'\n')


if __name__ == '__main__':
    DIR = '/home/web_runner/virtual-environments/scrapyd/items/product_ranking/amazon_products/'
    matches = []
    for root, dirnames, filenames in os.walk(DIR):
        for filename in fnmatch.filter(filenames, '*.jl'):
            matches.append(os.path.join(root, filename))

    print 'Found %i files totally' % len(matches)
    for m in matches:
        if file_is_bzip2(m):
            print 'File [%s] compressed, decompressing...' % m
            uncompress_and_rename_old(m)
            change_br_in_file(m)