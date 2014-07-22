# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import division, absolute_import, unicode_literals

import unittest
import string


class AddSearchTermInTitleFields(object):

    _TRANSLATE_TABLE = string.maketrans('', '')

    @staticmethod
    def _normalize(s):
        try:
            return str(s).translate(
                AddSearchTermInTitleFields._TRANSLATE_TABLE,
                string.punctuation
            ).lower()
        except UnicodeEncodeError:
            # Less efficient version for truly unicode strings.
            for c in string.punctuation:
                s = s.replace(c, '')
            return s

    @staticmethod
    def process_item(product, spider):
        product['search_term_in_title_exactly'] = False
        product['search_term_in_title_partial'] = False
        product['search_term_in_title_interleaved'] = False

        try:
            title = AddSearchTermInTitleFields._normalize(product['title'])
            search_term = AddSearchTermInTitleFields._normalize(
                product['search_term'])
            search_term_words = search_term.split()

            if search_term in title:
                product['search_term_in_title_exactly'] = True
            elif AddSearchTermInTitleFields._is_title_interleaved(
                    title, search_term_words):
                product['search_term_in_title_interleaved'] = True
            else:
                product['search_term_in_title_partial'] = any(
                    word in title for word in search_term_words)
        except KeyError:
            pass

        return product

    @staticmethod
    def _is_title_interleaved(title, search_term_words):
        result = False

        title_words = title.split()
        offset = 0
        for st_word in search_term_words:
            for i, title_word in enumerate(title_words[offset:]):
                if st_word == title_word:
                    offset += i + 1
                    break  # Found one!
            else:
                break  # A search term was not in the title.
        else:
            # The whole search term was traversed so it's interleaved.
            result = True

        return result


class AddSearchTermInTitleFieldsTest(unittest.TestCase):

    def test_search_term_in_title_interleaved(self):
        item = dict(title="My Mary has a little Pony!",
                    search_term="Mary, a pony")

        result = AddSearchTermInTitleFields.process_item(item, None)

        assert result['search_term_in_title_interleaved']
        assert not result['search_term_in_title_partial']
        assert not result['search_term_in_title_exactly']


if __name__ == '__main__':
    unittest.main()
