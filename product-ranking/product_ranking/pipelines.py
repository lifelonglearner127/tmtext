# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import division, absolute_import, unicode_literals

import string
import unittest
import json

from scrapy import Selector
from scrapy.exceptions import DropItem
from scrapy import logformatter
from scrapy import log
import tldextract
try:
    import mock
except ImportError:
    pass  # Optional import for test.

from .items import Price


class PipelineFormatter(logformatter.LogFormatter):
    # redefine this method to change log level for DropItem exception
    def dropped(self, item, exception, response, spider):
        log_format = super(PipelineFormatter, self).dropped(
            item, exception, response, spider)
        log_format['level'] = log.ERROR
        return log_format


class CheckGoogleSourceSiteFieldIsCorrectJson(object):

    def process_item(self, item, spider):
        google_source_site = item.get('google_source_site')
        if google_source_site:
            try:
                json.loads(google_source_site)
            except:
                raise DropItem("Invalid JSON format at 'google_source_site'"
                               " field at item:")
        return item


class CutFromTitleTagsAndReturnStringOnly(object):

    def process_item(self, item, spider):
        if "title" in item:
            item["title"] = self._title_without_tags(item["title"])
        return item

    @staticmethod
    def _title_without_tags(title):
        if isinstance(title, str) or isinstance(title, unicode):
            return Selector(text=title).xpath("string()").extract()[0]
        return title


class WalmartRedirectedItemFieldReplace(object):
    """ Replaces fields of the "variant" item with the data of the "parent"
        (original) one
    """
    def process_item(self, item, spider):
        _walmart_current_id = item.get('_walmart_current_id', None)
        _walmart_original_id = item.get('_walmart_original_id', None)
        _walmart_original_oos = item.get('_walmart_original_oos', None)
        _walmart_original_price = item.get('_walmart_original_price', None)
        if _walmart_original_oos:
            item['is_out_of_stock'] = _walmart_original_oos
        if _walmart_original_price and item.get('price', None):
            item['price'] = Price(priceCurrency=item['price'].priceCurrency,
                                  price=_walmart_original_price)
        return item


class SetMarketplaceSellerType(object):
    def process_item(self, item, spider):
        spider_main_domain = spider.allowed_domains[0]
        spider_main_domain = tldextract.extract(spider_main_domain).domain
        marketplaces = item.get('marketplace', {})
        # extend the marketplace dict with the seller_type (see BZ 1869)
        for marketplace in marketplaces:
            name = marketplace.get('name', '')
            if name:
                name_domain = tldextract.extract(name).domain
                if spider_main_domain and name_domain:
                    if spider_main_domain.lower() in name_domain.lower():
                        marketplace['seller_type'] = 'site'
                    else:
                        marketplace['seller_type'] = 'marketplace'
        return item


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
    def process_item(item, spider):
        if not item.has_key("is_single_result"):
            AddSearchTermInTitleFields.add_search_term_in_title_fields(
                item, item['search_term'])

        return item

    @staticmethod
    def is_a_partial_match(title_words, words):
        return any(word in title_words for word in words)

    @staticmethod
    def add_search_term_in_title_fields(product, search_term):
        # Initialize item.
        product['search_term_in_title_exactly'] = False
        product['search_term_in_title_partial'] = False
        product['search_term_in_title_interleaved'] = False

        try:
            # Normalize data to be compared.
            title_norm = AddSearchTermInTitleFields._normalize(
                product['title'])
            title_words = title_norm.split()
            search_term_norm = AddSearchTermInTitleFields._normalize(
                search_term)
            search_term_words = search_term_norm.split()

            if search_term_norm in title_norm:
                product['search_term_in_title_exactly'] = True
            elif AddSearchTermInTitleFields._is_title_interleaved(
                    title_words, search_term_words):
                product['search_term_in_title_interleaved'] = True
            else:
                product['search_term_in_title_partial'] \
                    = AddSearchTermInTitleFields.is_a_partial_match(
                        title_words, search_term_words)
        except KeyError:
            pass

    @staticmethod
    def _is_title_interleaved(title_words, search_term_words):
        result = False

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


class FilterNonPartialSearchTermInTitle(object):
    """Filters Items where the title doesn't contain any of the
     required_keywords.

     This pipeline stage will override AddSearchTermInTitleFields as if the
     required_keywords where the search_term.
     """

    @staticmethod
    def process_item(item, spider):
        title_words = AddSearchTermInTitleFields._normalize(
            item['title']
        ).split()
        required_words = spider.required_keywords.lower().split()
        if not AddSearchTermInTitleFields.is_a_partial_match(
                title_words, required_words):
            raise DropItem(
                "Does not match title partially: %s" % item['title'])

        AddSearchTermInTitleFields.add_search_term_in_title_fields(
            item, spider.required_keywords)

        return item


class AddSearchTermInTitleFieldsTest(unittest.TestCase):

    def test_exact_multi_word_match(self):
        item = dict(title="Mary has a little Pony! ",
                    search_term=" littLe pony ")

        result = AddSearchTermInTitleFields.process_item(item, None)

        assert not result['search_term_in_title_interleaved']
        assert not result['search_term_in_title_partial']
        assert result['search_term_in_title_exactly']

    def test_search_term_in_title_interleaved(self):
        item = dict(title="My Mary has a little Pony!",
                    search_term="Mary, a pony")

        result = AddSearchTermInTitleFields.process_item(item, None)

        assert result['search_term_in_title_interleaved']
        assert not result['search_term_in_title_partial']
        assert not result['search_term_in_title_exactly']


class FilterNonPartialSearchTermInTitleTest(unittest.TestCase):

    def test_when_an_item_does_not_match_partially_then_it_should_be_filtered(self):
        item = dict(title="one two three")
        spider = mock.MagicMock()
        spider.required_keywords = "none of the ones in the title"
        self.assertRaises(
            DropItem,
            FilterNonPartialSearchTermInTitle.process_item,
            item,
            spider,
        )

    def test_when_an_item_matches_partially_then_it_should_have_the_title_match_fields(self):
        item = dict(title="one two three")
        spider = mock.MagicMock()
        spider.required_keywords = "has one word in the title"
        FilterNonPartialSearchTermInTitle.process_item(item, spider)

        assert item['search_term_in_title_partial']
        assert not item['search_term_in_title_interleaved']
        assert not item['search_term_in_title_exactly']


if __name__ == '__main__':
    unittest.main()
