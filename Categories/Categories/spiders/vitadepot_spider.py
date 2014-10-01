import urlparse
import re

from scrapy.spider import BaseSpider
from scrapy import Request
from scrapy.log import msg, WARNING
from scrapy.selector.unified import SelectorList

from Categories.items import CategoryItem
from spiders_utils import Utils


class VitaDepotSpider(BaseSpider):
    name = "vitadepot"
    allowed_domains = ["vitadepot.com"]
    start_urls = ["http://vitadepot.com/"]

    EXCLUDED_DEPARTMENTS = [
        "/shop-by-brand.html",
        "/shop-by-health-concern.html",
    ]

    def __init__(self, *args, **kwargs):
        self.id_counter = 0
        super(VitaDepotSpider, self).__init__(*args, **kwargs)

    def _is_excluded(self, url):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        return path in self.EXCLUDED_DEPARTMENTS

    def _get_id(self):
        self.id_counter += 1
        return self.id_counter

    def _set_value(self, item, key, value, convert=lambda val: val):
        """Set item["key"] to value if value is not None"""
        if value is not None:
            item[key] = convert(value)

    def parse(self, response):
        top_level_links = response.css('li.level0')
        for link in top_level_links:
            url = link.css('::attr(href)').extract()[0]
            text = link.css('::text').extract()[0]
            if self._is_excluded(url):
                continue
            category = CategoryItem(text=text)
            yield Request(url, callback=self._parse_category, meta={"category": category})

    def _parse_category(self, response):
        category = response.meta['category']
        self._populate_category(response)
        classifications = self._scrape_classifications(response)
        categories = classifications.pop("Shop By Category", [])
        for url, text, nr_products in categories:
            new_category = CategoryItem(text=text, nr_products=nr_products)
            yield Request(url, self._parse_category, meta={"category": new_category, "parent": category})
        if category.get('nr_products') is None:
            category['nr_products'] = sum((item[2] for item in categories))
        category['classification'] = {key: [{'name': itm[1], 'nr_products': itm[2]} for itm in value]
                                       for key,value in classifications.iteritems()}
        yield category

    def _populate_category(self, response):
        category = response.meta['category']
        parent = response.meta.get('parent', {})
        category['url'] = response.url
        category['level'] = parent.get('level', 0) + 1
        category['catid'] = self._get_id()
        self._set_value(category, 'parent_text', parent.get('text'))
        self._set_value(category, 'parent_url', parent.get('url'))
        self._set_value(category, 'parent_catid', parent.get('catid'))
        self._set_value(category, 'grandparent_text', parent.get('parent_text'))
        self._set_value(category, 'grandparent_url', parent.get('parent_url'))
        category['department_text'] = parent.get('department_text', category['text'])
        category['department_url'] = parent.get('department_url', category['url'])
        category['department_id'] = parent.get('department_id', category['catid'])
        self._populate_from_html(response)

    def _populate_from_html(self, response):
        category = response.meta['category']
        #description = response.xpath('//div[@class="category-description std"]/*[not(a[@class="viewAllCats"])]')
        description = response.xpath('//div[@class="category-description std"]/node()')
        description = SelectorList(filter(lambda itm: not len(itm.css('.viewAllCats')), description))
        description = ' '.join(description.extract()) or None
        description = description.strip(' \n\r\t')
        desc_title = (response.css('.category-title h1::text').extract() or [None])[0]
        self._set_value(category, 'description_text', description)
        self._set_value(category, 'description_title', desc_title)
        tokenized = Utils.normalize_text(description) if description else []
        category['description_wc'] = len(tokenized)
        #if description and desc_title:
        #    category['keyword_count'], category['keyword_density'] = Utils.phrases_freq(desc_title, description)

    def _scrape_classifications(self, response):
        names = response.css('dl#narrow-by-list dt::text').extract()
        fields = response.css('dl#narrow-by-list dd')
        result = {}
        for name, field in zip(names, fields):
            this_result = []
            result[name.strip()] = this_result
            for li in field.css('ol li'):
                link = li.css('a')
                url = link.css('::attr(href)').extract()[0]
                anchor = ''.join(link.xpath('./text()|./*/text()').extract())
                match = re.search('\d+', ''.join(li.xpath('./text()').extract()))
                if match:
                    nr_products = int(match.group())
                else:
                    msg('Not found product nr for %s on %s' % (anchor or 'UNKNOWN', response.url), WARNING)
                    nr_products = 0
                this_result.append((url, anchor, nr_products))
        return result