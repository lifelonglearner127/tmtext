import requests
from flask import Flask, jsonify, abort, request
import os
import json
import unittest

class SpecTest(unittest.TestCase):
    pass

# levenshtein distance formula - used from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
# this is able to tell how similar two strings are
# note it doesn't compare the whole string if long, just the ends
def lev(self, seq1, seq2):
    seq1 = seq1.strip()
    seq2 = seq2.strip()
    ends = 30 #how much of the ends to compare
    if(len(seq1) > (2*ends)):
        seq1 = seq1[0:ends] + seq1[len(seq1)-ends:]
    if(len(seq2) > (2*ends)):
        seq2 = seq2[0:ends] + seq2[len(seq2)-ends:]
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    dist = thisrow[len(seq2) - 1]
    percent = dist/(1.*len(seq1)+len(seq2))*2
    return percent


def create_test (expected, actual):
    def do_test_expected(self):
        if(isinstance(expected, int) 
                or isinstance(expected, bool) 
                or isinstance(expected, float)):
            self.assertEqual(expected, actual)

        elif(isinstance(expected, str)):
            self.assertTrue(lev(pair[0]), pair[1])

        elif(isinstance(expected, list)):
            self.assertEqual(expected, actual)

        else:
            pass
    return do_test_expected

def load_test(expected, actual, name):
    test_method = create_test(expected, actual)
    test_method.__name__ = 'test_%s' % name
    setattr (SpecTest, test_method.__name__, test_method)

SUPPORTED_SITES = [
                   "amazon" ,
                   "argos",
                   "bestbuy" ,
                   "homedepot" ,
                   "kmart" ,
                   "ozon" ,
                   "pgestore" ,
                   "statelinetack" ,
                   "target" ,
                   "tesco" ,
                   "vitadepot",
                   "walmart" ,
                   "wayfair" ,
                   ]



def build_unit_test():
    for site in SUPPORTED_SITES:
        path = 'extract_%s_test.json'%site
        test_json = []
        #print os.getcwd()
        if os.path.isfile(path):
            try:
                f = open(path, 'r')
                s = f.read()
                if len(s) > 1:
                    test_json = json.loads(s)
                else:
                    Raise("json file not long enough")
            except Exception as e:
                print "Error loading json file: ", e
                f.close()
                break
            else:
                f.close()

            for expected in test_json:
                url = expected['url']
                test_url = "http://localhost/get_data?site=%s&url=%s"%(site, url)
                actual = requests.get(test_url).text
                actual = json.loads(actual)
                compare_dict(expected, actual, "")

               

# traverse down 2 proposedly similar dictionaries and test if they're identical
# expected dict, actual dict, and the current branch within the dictionary tree
def compare_dict(expected, actual, branch):
     # KEY DIFFERENCES
    expected_extra_keys = [x for x in expected.keys() if x not in actual.keys()]
    actual_extra_keys = [x for x in actual.keys() if x not in expected.keys()]

    load_test([], expected_extra_keys, "extra_keys_in_expected_not_in_actual")
    load_test([], actual_extra_keys, "extra_keys_in_actual_not_in_expected")


    # VALUE DIFFERENCES - The following codes was assisted by : http://stackoverflow.com/questions/2798956/python-unittest-generate-multiple-tests-programmatically                    
    union_keys = set(actual.keys()) & set(expected.keys())
    for key in union_keys:
        print key
        print "returned_value_for_%s_is_same"%key
        load_test(expected[key], actual[key], "returned_value_for_%s_is_same"%(key))


    
if __name__ == '__main__':
    build_unit_test()
    unittest.main()

    # app = Flask(__name__)
    # app.run('0.0.0.0', port=80, threaded=True)

