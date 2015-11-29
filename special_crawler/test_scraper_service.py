#!/usr/bin/python
#
import unittest
import json
import re
import copy
import random
import psycopg2
import psycopg2.extras
import requests
import sys
import urllib
from datetime import date

SUPPORTED_SITES = ["amazon", "bestbuy", "homedepot","statelinetack","tesco","walmart","argos",
                    "kmart","ozon","pgestore","pgshop","vitadepot","wayfair","impactgel",
                    "chicksaddlery","bhinneka","maplin","hersheysstore","target","chicago",
                    "samsclub","babysecurity","staples","soap","drugstore","staplesadvantage",
                    "freshamazon","souq","freshdirect","quill","george","peapod"]


class JsonDiff:
    def __init__(self, sample_json, test_json, list_depth=0):
        self.log = ""

        self.sample_json = sample_json
        self.test_json = test_json

        self.difference = []
        # variable to control how deep to recursively search
        # currently not used
        self.list_depth = list_depth
        self.occurrence_value_change = 0
        self.occurrence_structural_change = 0
        self.occurrence_type_change = 0

    def logger(self, log_level, message):
#        self.log += log_level + ": " + message + "\n"
        self.log += message + "\n"

    def _one_to_one(self, strings, regexes):
        dim = len(strings)
        match_chart = [[0 for i in range(dim)] for j in range(dim)]

        # set up matching table
        # will be a 2d array with:
        # 0s indicating no match
        # 1s indicating a match
        for r in range(dim):
            for s in range(dim):
                match = re.match(regexes[r], strings[s])
                if match:
                    match_chart[r][s] = 1

        # minimize match table
        # sum the rows and columns
        # rows
        sums = [sum(match_chart[k][:]) for k in range(dim)]
        # add in columns
        sums.extend(sum([match_chart[i][j] for i in range(dim)])
                    for j in range(dim))

        num_matches, index, turns_wo_match = 0, 0, 0
        max_index = 2 * dim
        minimized = [False for i in range(2 * dim)]
        # loop until all matched or no more minimization is possible
        while num_matches < max_index and turns_wo_match < max_index \
                and not sums == [1] * (2 * dim):
            if sums[index] == 0:
                return {}  # no match for one of the fields
            elif sums[index] == 1 and not minimized[index]:
                # find coordinate
                if index < dim:  # in a row
                    for i in range(dim):
                        if match_chart[index][i] == 1:
                            self._clear_match_col(match_chart, i, index)
                            minimized[index] = True
                            continue
                else:  # in a col
                    for i in range(dim):
                        if match_chart[i][index] == 1:
                            self._clear_match_row(match_chart, i, index)
                            minimized[index] = True
                            continue
                turns_wo_match = 0
                num_matches += 1
                # update sums
                sums = [sum(match_chart[k][:]) for k in range(dim)]
                # add in columns
                sums.extend(sum([match_chart[i][j] for i in range(dim)])
                            for j in range(dim))

            else:
                turns_wo_match += 1

            index = (index + 1) % max_index

        if num_matches == max_index or sums == [1] * (2 * dim):
            final_mapping = {}
            for i in range(dim):
                # find match
                for j in range(dim):
                    if match_chart[i][j] == 1:
                        final_mapping[regexes[i]] = strings[j]
                        continue
            return final_mapping

        else:  # ambiguous
            self.logger("error", "Ambiguous matching please fix your model "
                         "to use more specific regexes")
            raise Exception("skip")

    def _lists_equal(self, json_list, regex_list):
        # length check
        if not len(json_list) == len(regex_list):
            return False

        # go through indices and ensure they are all equal
        for index in range(len(json_list)):
            if not type(json_list[index]) == type(regex_list[index]):
                return False

            if type(json_list[index]) is dict:
                # do json comparison
                if not self.equals_model(json_list[index], regex_list[index]):
                    return False

            elif type(json_list[index]) is list:
                # another list comparison
                if not self._lists_equal(json_list[index], regex_list[index]):
                    return False

            elif type(json_list[index]) is unicode:
                # regex match
                if not re.match(regex_list[index], json_list[index]):
                    return False

            else:
                # some other type
                if not json_list[index] == regex_list[index]:
                    return False

        return True

    def equals_model(self, json_input, model):
        """
        General process will be to read both inputs as json objects
        It will then conduct a DFS
        At each level, check that the size of the key set is the same
        Check that the key set has a 1-1 correspondence
        Check for each key that the values are the same

        The model will treat all keys as regexes. All values will be
        dicts, lists, or regexes
        """
        if type(json_input) is dict and type(model) is dict:
            json_keys = json_input.keys()
            model_keys = model.keys()
        elif type(json_input) is list and type(model) is list:
            return self._lists_equal(json_input, model)
        elif type(json_input) is not type(model):
            return False
        else:
            self.logger("error", "Not proper JSON format. Please check your input.")
            raise Exception("skip")

        # check size
        if not len(json_keys) == len(model_keys):
            return False

        # check 1-1 correspondence
        key_matches = self._one_to_one(json_keys, model_keys)

        if not len(json_keys) == len(key_matches.keys()):
            return False

        # check values
        for key in key_matches.keys():
            if not type(json_input.get((key_matches[key]))) == \
                    type(model[key]):
                return False
            if type(model[key]) is dict:
                # recursive search
                if not self.equals_model(json_input.get(key_matches[key]),
                                         model[key]):
                    return False
                    # otherwise continue

            elif type(model[key]) is list:
                # lists are deterministic! yay!
                if not self._lists_equal(json_input.get(key_matches[key]),
                                         model[key]):
                    return False

            elif type(model[key]) is unicode:
                if not re.match(model[key], json_input.get(key_matches[key])):
                    return False

            # maybe an int or something?
            else:
                if not json_input.get(key_matches[key]) == model[key]:
                    return False

        # if we make it through all of this, hooray! Match
        return True

    def diff_model(self, _json1, _json2, path='', depth=-1):
        if not type(_json1) == type(_json2):
            if type(_json2) is unicode and type(_json1) not in [list, dict]:
                # Potential regex match
                self._diff_json_item(_json1, _json2, path, True)
            else:
                '''
                self.difference.append(u'TypeDifference : {} - {}:'
                                       u' ({}), {}: ({})'
                                       .format(path, type(_json1).__name__,
                                               str(_json1),
                                               type(_json2).__name__,
                                               str(_json2)))
                '''
                print u"TypeDifference : {} - {}: ({}), {}: ({})".format(path, type(_json1).__name__,
                                               str(_json1),
                                               type(_json2).__name__,
                                               str(_json2))
                self.difference.append(u'<tr style="background-color: green; color: white;">'
                                       u'<td>{}</td><td>{}</td><td>{}</td></tr>'
                                       .format(path, type(_json1).__name__, type(_json2).__name__))
                self.occurrence_type_change += 1
        else:
            # they are the same type
            # Three choices: dict, list, item
            if type(_json1) is dict:
                self._diff_json_dict(_json1, _json2, path, depth, True)
            elif type(_json1) is list:
                self._diff_json_list(_json1, _json2, path, depth, True)
            else:
                self._diff_json_item(_json1, _json2, path, True)

    def diff_json(self, _json1, _json2, path='', depth=-1):
        """
        This code computes the diff between two different JSON objects.
        It also computes a line by line delta to be used to determine
        similarity
        This scoring will be especially useful in the regex version as it will
        allow for easier classification

        Assume json1 is new and json2 is old

        Depth should be -1 for full recursive search
        Depth == 0 -> do straight list or dict equivalence
        Depth > 0 do recursive search, but decrement depth so we do not search
        forever

        ** Currently depth is not used. This code is added to ease enhancements
        in the future should we decide **

        Resulting difference is stored in the class's self.difference variable
        """
        if not type(_json1) == type(_json2):
            '''
            self.difference.append(u'TypeDifference : {} - is {}: ({}),'
                                   u' but was {}: ({})'
                                   .format(path, type(_json1).__name__,
                                           str(_json1), type(_json2).__name__,
                                           str(_json2)))
            '''
            '''
            print u"TypeDifference : {} - is {}: ({}), but was {}: ({})".format(path, type(_json1).__name__,
                                           str(_json1), type(_json2).__name__,
                                           str(_json2))
            '''
            self.difference.append(u'<tr style="background-color: green; color: white;"><td>{}</td>'
                                   u'<td>{}</td><td>{}</td></tr>'
                                   .format(path, type(_json1).__name__, type(_json2).__name__))
            self.occurrence_type_change += 1
        else:
            # they are the same type
            # Three choices: dict, list, item
            if type(_json1) is dict:
                self._diff_json_dict(_json1, _json2, path, depth, False)
            elif type(_json1) is list:
                self._diff_json_list(_json1, _json2, path, depth, False)
            else:
                self._diff_json_item(_json1, _json2, path, False)

    def _diff_json_dict(self, _json1, _json2, path, depth, use_regex):
        # Depth greater > 0 indicates we should compare keys
        # Negative depth means continuously recursively search
        if not depth == 0:
            json1_keys = _json1.keys()
            json2_keys = _json2.keys()
            matched_keys = []
            for key in json1_keys:
                if len(path) == 0:
                    new_path = key
                else:
                    new_path = '{}.{}'.format(path, key)
                if key in json2_keys:
                    # match
                    matched_keys.append(key)
                    json2_keys.remove(key)
                else:
                    # key in json1 that is not in json2
                    # expand that k-v pair into diff
                    self._expand_diff(_json1[key], new_path, True)
            for key in json2_keys:
                if len(path) == 0:
                    new_path = key
                else:
                    new_path = '{}.{}'.format(path, key)
                # all keys remaining are in 2, but not 1
                # expand these k-v pairs into diff as well
                self._expand_diff(_json2[key], new_path, False)

            # now that we have matched keys, recursively search
            for key in matched_keys:
                if len(path) == 0:
                    new_path = key
                else:
                    new_path = '{}.{}'.format(path, key)
                if use_regex:
                    self.diff_model(_json1[key], _json2[key], new_path,
                                    depth - 1)
                else:
                    self.diff_json(_json1[key], _json2[key], new_path,
                                   depth - 1)

    def _diff_json_list(self, _json1, _json2, path, depth, use_regex):
        # save a snapshot of difference for comparison
        # in the different recursive branches
        current_difference = copy.deepcopy(self.difference)
        json2_original = copy.deepcopy(_json2)
        json1_matches = []
        # Try to find a match for each item in JSON1
        '''
        ' This WILL find a match for the first item in a a list of similar
        ' dictionaries even if later dicts in the list are a better match
        '
        ' TODO Fix this bug -- 2 pass diff?
        '''
        cur_index = 0
        for (index, item) in enumerate(_json1):
            prev_index = cur_index
            # map from the index in the list to irrelevance score
            # irrelevance score is higher the more unrelated
            #  0 is perfect match
            index_to_irrelevance = {}
            # map from the index in the list to the changeset associated
            # between this 'item' and _json2[index]
            index_to_changeset = {}
            while cur_index < len(_json2):
                if not use_regex and item == _json2[cur_index]:
                    # perfect match
                    index_to_irrelevance[cur_index] = 0
                    json1_matches.append(item)
                    _json2.remove(_json2[cur_index])
                    break
                elif use_regex and type(item) not in [list, dict]:
                    if type(_json2[cur_index]) is unicode:
                        # we can use as a pattern though item could be an
                        # integer say
                        match = re.match(_json2[cur_index], str(item))
                        if match:
                            index_to_irrelevance[cur_index] = 0
                            json1_matches.append(item)
                            _json2.remove(_json2[cur_index])
                            break
                        else:
                            # no possible match
                            index_to_irrelevance[cur_index] = -1
                    else:
                        # Can't use regex-- test strict equality
                        if item == _json2[cur_index]:
                            # perfect match
                            index_to_irrelevance = 0
                            json1_matches.append(item)
                            _json2.remove(_json2[cur_index])
                        else:
                            # no match possible
                            index_to_irrelevance[cur_index] = -1
                            continue
                elif depth == 0 or type(item) not in [list, dict] or type(
                        item) is not type(_json2[cur_index]):
                    # failed surface match
                    # there might be a match later on in the list
                    index_to_irrelevance[
                        cur_index] = -1  # to indicate no possible match
                else:
                    # failed, but do recursive search to find best match
                    new_path = "{}[{}]".format(path, index)
                    if use_regex:
                        self.diff_model(item, _json2[cur_index], new_path,
                                        depth - 1)
                    else:
                        self.diff_json(item, _json2[cur_index], new_path,
                                       depth - 1)
                    # determine the difference of the recursive branch to find
                    # best match
                    index_to_irrelevance[cur_index] = len(
                        [diff_item for diff_item in self.difference if
                         diff_item not in current_difference])
                    index_to_changeset[cur_index] = [diff_item for diff_item in
                                                     self.difference if
                                                     diff_item not in
                                                     current_difference]
                    # set difference back to before the diff
                    self.difference = copy.deepcopy(current_difference)
                cur_index += 1

            '''
            ' Matching strategy
            '
            ' 1) If there is a 0 irrelevance: perfect match, move to next item
            ' 2) If there are all -1 irrelevance: no match, pick lowest index
            ' 3) If there are any with > 0 irrelevance pick the lowest one as
            '   best match
            '     - In case of tie, lowest index wins
            '''
            indices = index_to_irrelevance.keys()
            if len(indices) == 0:
                break
            indices.sort()
            best_match_score = -1
            match_index = indices[0]
            for i in indices:
                if index_to_irrelevance[i] == 0:
                    best_match_score = 0
                    break
                elif index_to_irrelevance[i] < 0:
                    continue
                else:
                    if best_match_score < 0 \
                            or index_to_irrelevance[i] < best_match_score:
                        best_match_score = index_to_irrelevance[i]
                        match_index = i
            if best_match_score > 0:
                # treat as: 'better than nothing match so we'll take it'
                self.difference.extend(index_to_changeset[match_index])
                json1_matches.append(item)
                _json2.remove(_json2[match_index])
                cur_index = match_index  # Should be the after the match
            elif best_match_score < 0:
                cur_index = prev_index

        # At this point we have two lists with the items that weren't matched
        match_index = 0
        for index in range(len(_json1)):
            if match_index < len(json1_matches) and _json1[index] == \
                    json1_matches[match_index]:
                match_index += 1
            else:
                new_path = "{}[{}]".format(path, index)
                self._expand_diff(_json1[index], new_path, True)

        original_index = 0
        for index in range(len(_json2)):
#            while not _json2[index] == json2_original[::-1][original_index]:
#                original_index += 1
            new_path = "{}[{}]".format(path, len(
                json2_original) - original_index - 1)
            self._expand_diff(_json2[index], new_path, False)
            original_index += 1

    def _diff_json_item(self, _json1, _json2, path, use_regex):
        if use_regex and type(_json2) is unicode:
            match = re.match(_json2, str(_json1))
            if not match:
                print u'Changed: {} to {} from {}'.format(path, _json1, _json2)
                self.difference.append(
#                    u'Changed: {} to {} from {}'.format(path, _json1, _json2))
                    u'<tr style="background-color: blue; color: white;"><td>{}</td>'
                    u'<td>{}</td><td>{}</td></tr>'.format(path, _json1, _json2))
                self.occurrence_value_change += 1
        else:
            if not _json1 == _json2:
                print u'Changed: {} to {} from {}'.format(path, _json1, _json2)
                self.difference.append(
#                    u'Changed: {} to {} from {}'.format(path, _json1, _json2))
                    u'<tr style="background-color: blue; color: white;"><td>{}</td>'
                    u'<td>{}</td><td>{}</td></tr>'.format(path, _json1, _json2))
                self.occurrence_value_change += 1

    def _expand_diff(self, blob, path, new_item):
        """
        recursively add everything at this 'level' to the diff

        :param blob: The item (can be list, dict or item) to expand into the
        diff
        :param path: current path of the item
        :param new_item: true if we are in new json (things added),
        false if old (things removed)
        """
        # Three possibilities: dict, list, item
        if new_item:
            c = '+'
            color = 'red'
        else:
            c = '-'
            color = 'black'

        if type(blob) is dict:
            for key in blob.keys():
                if len(path) == 0:
                    new_path = key
                else:
                    new_path = "{}.{}".format(path, key)
                if type(blob[key]) not in [list, dict]:
                    print u'{}: {}={}'.format(c, new_path, blob[key])
                    self.difference.append(
#                        u'{}: {}={}'.format(c, new_path, blob[key]))
                        u'<tr style="background-color:' + color + u'; color: white;">'
                        u'<td collspan="2">{}</td><td>{}</td></tr>'.format(new_path, blob[key]))
                    self.occurrence_structural_change += 1
                else:
                    self._expand_diff(blob[key], new_path, new_item)
        elif type(blob) is list:
            for (index, item) in enumerate(blob):
                new_path = "{}[{}]".format(path, index)
                if type(blob[index]) in (list, dict):
                    self._expand_diff(item[index], new_path, new_item)
                else:
                    print u'{}: {}={}'.format(c, new_path, blob[index])
                    self.difference.append(
#                        u'{}: {}={}'.format(c, new_path, blob[index]))
                        u'<tr style="background-color:' +  color + u'; color: white;">'
                        u'<td>{}</td><td colspan="2">{}</td></tr>'.format(new_path, blob[index]))
                    self.occurrence_structural_change += 1
        else:
            print u"{}: {}={}".format(c, path, blob)
#            self.difference.append(u"{}: {}={}".format(c, path, blob))
            self.difference.append(
                u'<tr style="background-color:' + color + u'; color: white;">'
                u'<td>{}</td><td colspan="2">{}</td></tr>'.format(path, blob))
            self.occurrence_structural_change += 1

    def diff(self):
        difference = []
        self.diff_json(self.sample_json, self.test_json)

#        self.logger("info", 'Diff from {}\n'.format(model_name))
        for change in self.difference:
            # log instead of print,
            # in case a module wants to suppress output
#            self.logger("info", change.encode('ascii', 'replace'))
            self.logger("info", change.encode('ascii', 'replace'))
        difference.append(self.difference)
        # Reinitialize so that we can run against multiple models
        self.difference = []
        self.list_depth = 0

        return difference if len(difference) > 1 else difference[0]


class ServiceScraperTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ServiceScraperTest, self).__init__(*args, **kwargs)

        is_valid_param = False

        if specified_website != "":
            for site in SUPPORTED_SITES:
                if site == specified_website:
                    is_valid_param = True
                    break

            if not is_valid_param:
                print "\nPlease input valid website name.\n-----------------------------------"

                for site in SUPPORTED_SITES:
                    sys.stdout.write(site + " ")

                print "\n"
                exit(1)

        try:
            self.con = None
#            self.con = psycopg2.connect(database='tmtext', user='postgres', password='password', host='127.0.0.1', port='5432')
            self.con = psycopg2.connect(database='scraper_test', user='root', password='QdYoAAIMV46Kg2qB', host='scraper-test.cmuq9py90auz.us-east-1.rds.amazonaws.com', port='5432')
            self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.urls_by_scraper = {}
        except Exception, e:
            print e

    def _test(self, website, sample_url):
        print "\n-------------------------------Report results for %s-------------------------------" % website
        print ">>>>>>sample url: %s" % sample_url

        today = date.today()

        base = "http://localhost/get_data?url=%s"
        test_json = requests.get(base%(urllib.quote(sample_url))).text

        try:
            test_json = json.loads(test_json)
            test_json_str = json.dumps(test_json, sort_keys=True, indent=4)

            if "sellers" not in test_json.keys():
                raise Exception("Invalid product")

            self.cur.execute("select * from console_urlsample where website='%s' and url='%s' and not_a_product=0" % (website, sample_url))
            row = self.cur.fetchall()

            if row:
                row = row[0]

                sample_json = row["json"]
                sample_json_str = row["json"]
                sample_json = json.loads(sample_json)
                diff_engine = JsonDiff(test_json, sample_json)

                print ">>>>>>reports:"

                diff_engine.diff()

                sql = ("insert into console_reportresult(sample_url, website, "
                       "report_result, changes_in_structure, changes_in_type, changes_in_value, report_date, "
                       "sample_json, current_json) "
                       "values('%s', '%s', $$%s$$, %d, %d, %d, '%s', $$%s$$, $$%s$$)"
                       % (sample_url, website, diff_engine.log, diff_engine.occurrence_structural_change,
                          diff_engine.occurrence_type_change, diff_engine.occurrence_value_change, today.isoformat(),
                          sample_json_str, test_json_str))

                self.cur.execute(sql)
                self.con.commit()

            self.cur.execute("update console_urlsample set not_a_product=0, json=$$%s$$, qualified_date='%s' where url='%s'"
                             % (test_json_str, today.isoformat(), sample_url))
            self.con.commit()
        except:
            test_json_str = ''
            print "This url is not valid anymore.\n"
            self.cur.execute("update console_urlsample set not_a_product=1, json=$$%s$$, qualified_date='%s' where url='%s'"
                             % (test_json_str, today.isoformat(), sample_url))
            self.con.commit()

    def initialize_scraper(self, website):
        # read input urls from database
        today = date.today()

        self.cur.execute("delete from console_reportresult where report_date='%s' and website='%s'" % (today.isoformat(), website))
        self.con.commit()

        self.cur.execute("select url_list from console_massurlimport")

        urls = []

        for row in self.cur:
            urls.extend(row[0].splitlines())

        urls = list(set(urls))
        urls = filter(lambda x: website + ".com" in x, urls)

        print "\nRandomly selected urls of %s:" % website
        print '\n' . join(urls)

        print "Loading urls..."

        for url in urls:
            url = url.strip()

            if website in SUPPORTED_SITES:
                self.cur.execute("select not_a_product from console_urlsample where url='%s'" % url)
                row = self.cur.fetchall()

                if not row:
                    base = "http://localhost/get_data?url=%s"
                    sample_json = requests.get(base%(urllib.quote(url))).text

                    not_a_product = 0

                    try:
                        sample_json = json.loads(sample_json)
                        sample_json_str = json.dumps(sample_json, sort_keys=True, indent=4)

                        if "sellers" not in sample_json.keys():
                            raise Exception('Invalid product')
                    except:
                        not_a_product = 1
                        sample_json_str = ''

                    print url

                    self.cur.execute("insert into console_urlsample(url, website, json, qualified_date, not_a_product)"
                                     " values('%s', '%s', $$%s$$, '%s', %d)"
                                     % (url, website, sample_json_str, today.isoformat(), not_a_product))
                    self.con.commit()

        self.cur.execute("select url from console_urlsample where website = '%s'" % website)
        urls = self.cur.fetchall()

        self.urls_by_scraper[website] = [url[0] for url in urls]
        nTestUrlCounts = len(self.urls_by_scraper[website])

        print "%s - number of test urls : %d" % (website, nTestUrlCounts)


    def test_walmart(self):
        if specified_website and specified_website != "walmart":
            return

        self.initialize_scraper("walmart")

        for url in self.urls_by_scraper["walmart"]:
            try:
                self._test("walmart", url)
            except:
                pass

    def test_amazon(self):
        if specified_website and specified_website != "amazon":
            return

        self.initialize_scraper("amazon")

        for url in self.urls_by_scraper["amazon"]:
            try:
                self._test("amazon", url)
            except:
                pass

if __name__ == '__main__':
    specified_website = ""

    if len(sys.argv) == 2:
        specified_website = sys.argv[1]

    del sys.argv[1:]

    unittest.main()