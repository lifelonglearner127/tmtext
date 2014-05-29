# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import division, absolute_import, unicode_literals

import unittest
import string


class AddCalculatedFields(object):

    _TRANSLATE_TABLE = string.maketrans('', '')

    @staticmethod
    def _normalize(s):
        return str(s).translate(
            AddCalculatedFields._TRANSLATE_TABLE,
            string.punctuation
        ).lower()

    @staticmethod
    def process_item(product, spider):
        title = AddCalculatedFields._normalize(product['title'])
        search_term = AddCalculatedFields._normalize(product['search_term'])
        search_term_words = search_term.split()

        product['search_term_in_title_exactly'] = search_term in title

        product['search_term_in_title_partial'] = st_partial = any(
            word in title for word in search_term_words)

        product['search_term_in_title_interleaved'] = False
        if st_partial:
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
                product['search_term_in_title_interleaved'] = True

        return product


class AddCalculatedFieldsTest(unittest.TestCase):

    def test_search_term_in_title_interleaved(self):
        item = dict(title="My Mary has a little Pony!",
                    search_term="Mary, a pony")

        result = AddCalculatedFields.process_item(item, None)

        assert result['search_term_in_title_interleaved']


if __name__ == '__main__':
    unittest.main()
