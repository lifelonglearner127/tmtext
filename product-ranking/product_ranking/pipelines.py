# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import division, absolute_import, unicode_literals

import string
import unittest
import json
import random
import sys
import copy
import os

from scrapy import Selector
from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import tldextract
try:
    import mock
except ImportError:
    pass  # Optional import for test.

from .items import Price
from .validation import _get_spider_output_filename

STATISTICS_ENABLED = False
STATISTICS_ERROR_MSG = None
try:
    from .statistics import report_statistics
    STATISTICS_ENABLED = True
except ImportError as e:
    STATISTICS_ERROR_MSG = str(e)


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 'deploy'))
from sqs_ranking_spiders.libs import convert_json_to_csv


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


class SetRankingField(object):
    """ Explicitly set "ranking" field value (needed for
        Amazon Shelf spider, temporary solution """
    def process_item(self, item, spider):
        if hasattr(spider, 'ranking_override'):
            ranking_override = getattr(spider, 'ranking_override')
            item['ranking'] = ranking_override
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
                try:
                    name_domain = tldextract.extract(name).domain
                except UnicodeEncodeError:  # non-ascii name (not domain)
                    marketplace['seller_type'] = 'marketplace'
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
        if not "is_single_result" in item:
            AddSearchTermInTitleFields.add_search_term_in_title_fields(
                item, item.get('search_term', ''))

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


def transform_jcpenney_variants(has_size_range, variants):
    # see BZ #9913

    # TODO: move this method to shared variants to support CH?

    if not variants:
        return variants

    for i, variant in enumerate(variants):
        properties = variant.get('properties', None)
        if 'lot' in variant and not 'lot' in properties:
            properties['lot'] = variant['lot']
        if properties:
            # BZ case 3
            if 'size' in properties and 'lot' in properties and has_size_range:
                lot_value = properties.pop('lot')
                size_value = properties.pop('size')
                properties['size'] = lot_value + '/' + str(size_value)
            else:
                # BZ case 1
                if 'inseam' in properties and not 'length' in properties:
                    inseam_value = properties.pop('inseam')
                    properties['length'] = inseam_value
                # BZ case 2
                if 'waist' in properties:
                    if (set(properties.keys()) - set(['lot']) - set(['color'])) == set(['waist']):
                        waist_value = properties.pop('waist')
                        properties['size'] = waist_value
        variants[i]['properties'] = properties

    return variants


class MergeSubItems(object):
    """ A quote: You can't have the same item being filled in parallel requests.
        You either need to make sure the item is passed along in a chain like fashion,
         with each callback returning a request for the next page of information with
          the partially filled item in meta, or you need to write a pipeline that
           will collect and group the necessary data.
    """
    _mapper = {}
    _subitem_mode = False

    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        # use extra 'create_csv_output' option for debugging
        args_ = u''.join([a.decode('utf8') for a in sys.argv])
        self.create_csv_output = (u'create_csv_output' in args_
                                  or u'save_csv_output' in args_)

    @staticmethod
    def _get_output_filename(spider):
        # TODO: better code for parsing command-line arguments
        cmd = ' '.join(sys.argv).split(' -o ')
        if not cmd or len(cmd) == 1:
            return spider._crawler.settings.attributes['FEED_URI'].value
        cmd = cmd[-1].strip()
        if ' ' in cmd:
            cmd = cmd.split(' ', 1)[0].strip()
        return cmd

    @staticmethod
    def _serializer(val):
        if isinstance(val, type(MergeSubItems)):  # class
            return val.__dict__
        else:
            return str(val)

    def spider_opened(self, spider):
        pass

    def _dump_mapper_to_fname(self, fname):
        # only for JCPenney - transform variants, see BZ 9913
        with open(fname, 'w') as fh:
            for url, item in self._mapper.items():
                if 'jcpenney' in url:
                    item['variants'] = transform_jcpenney_variants(item['_jcpenney_has_size_range'], item['variants'])
                fh.write(json.dumps(item, default=self._serializer)+'\n')

    def _dump_output(self, spider):
        if self._subitem_mode:  # rewrite output only if we're in "subitem mode"
            output_fname = self._get_output_filename(spider)
            if output_fname:
                self._dump_mapper_to_fname(output_fname)

    def spider_closed(self, spider):
        if self._subitem_mode:  # rewrite output only if we're in "subitem mode"
            self._dump_output(spider)
            _validation_filename = _get_spider_output_filename(spider)
            self._dump_mapper_to_fname(_validation_filename)
            if self.create_csv_output and self._get_output_filename(spider):
                # create CSV file as well
                _output_file = self._get_output_filename(spider).lower().replace('.jl', '')
                try:
                    _output_csv = convert_json_to_csv(_output_file)
                    print('Created CSV output: %s.csv' % _output_csv)
                except Exception as e:
                    print('Could not create CSV output: %s' % str(e))

    def process_item(self, item, spider):
        _item = copy.deepcopy(item)
        item = copy.deepcopy(_item)
        del _item
        _subitem = item.get('_subitem', None)
        if not _subitem:
            return item  # we don't need to merge sub-items
        self._subitem_mode = True  # switch a flag if there's at least one item with "subitem mode" found
        if 'url' in item:  # sub-items: collect them and dump them on "on_close" call
            _url = item['url']
            if not _url in self._mapper:
                self._mapper[_url] = {}
            self._mapper[_url].update(item)
            del item
            if random.randint(0, 100) == 0:
                # dump output from time to time to show progress (non-empty output file)
                self._dump_output(spider)
            raise DropItem('Multiple Sub-Items found')


class CollectStatistics(object):
    """ Gathers server and spider statistics, such as RAM, HDD, CPU etc. """

    @staticmethod
    def process_item(item, spider):
        if STATISTICS_ENABLED:
            _gather_stats = False
            if getattr(spider, 'product_url', None):
                _gather_stats = True
            else:
                _gather_stats = bool(random.randint(0, 50) == 0)
            if _gather_stats:
                try:
                    item['_statistics'] = report_statistics()
                except Exception as e:
                    item['_statistics'] = str(e)
            else:
                item['_statistics'] = ''
        else:
            item['_statistics'] = STATISTICS_ERROR_MSG
        return item


if __name__ == '__main__':
    unittest.main()
