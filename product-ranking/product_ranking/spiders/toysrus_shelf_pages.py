import re
import urlparse
import random
import hjson

import requests
from lxml import html
import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request

from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None

from .toysrus import ToysrusProductsSpider


class ToysrusShelfPagesSpider(ToysrusProductsSpider):
    name = 'toysrus_shelf_urls_products'
    allowed_domains = ["toysrus.com", "www.toysrus.com"]  # without this find_spiders() fails
    # Browser agent string list
    BROWSER_AGENT_STRING_LIST = {"Firefox": ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
                                             "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
                                             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"],
                                 "Chrome":  ["Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                                             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
                                             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                                             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"],
                                 "Safari":  ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
                                             "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
                                             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2"]
                                 }

    def _select_browser_agents_randomly(self, agent_type=None):
        if agent_type and agent_type in self.BROWSER_AGENT_STRING_LIST:
            return random.choice(self.BROWSER_AGENT_STRING_LIST[agent_type])

        return random.choice(random.choice(self.BROWSER_AGENT_STRING_LIST.values()))

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zip_code = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(ToysrusShelfPagesSpider, self).__init__(*args, **kwargs)
        self._setup_class_compatibility()

        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        urls = response.xpath('//div[@class="prodloop_cont"]/div/a[@class="prodtitle"]/@href').extract()
        urls = [urlparse.urljoin(response.url, x) for x in urls]

        shelf_categories = response.xpath('//a[@class="breadcrumb"]/text()').extract()
        shelf_category = None
        if shelf_categories:
            shelf_category = shelf_categories[len(shelf_categories) - 1]

        if len(urls) > 0:
            for url in urls:
                item = SiteProductItem()
                if shelf_category:
                    item['shelf_name'] = shelf_category
                if shelf_categories:
                    item['shelf_path'] = shelf_categories
                yield url, item
        else:
            self.num_pages = 1
            urls = []
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories


            # top sections except for  Toy BOx Favorites
            Resonance_URL = "http://www.res-x.com/ws/r2/Resonance.aspx?appid=toysrus01" \
                            "&tk=91392014501448&ss=549026946524962&sg=1&pg=27185259054672" \
                            "&vr=5.5x&bx=true&sc=thome_rr&sc=thome2_rr&sc=thome3_rr" \
                            "&sc=tcategory_rr&sc=bhome_rr&sc=bhome2_rr&sc=bhome3_rr&no=16" \
                            "&siteid=TRU&cb=certonaResx.showResponse&cv1=" \
                            "&cv2=0158136c2dc000770491f0442d000506d00380650093c" \
                            "&ur=http%3A%2F%2Fwww.toysrus.com%2Fshop%2Findex.jsp%3FcategoryId%3D{categoryId}" \
                            "&plk=&rf="
            categoryId = re.findall(r'categoryId=(\d+)', response.url)
            if len(categoryId) > 0:
                Resonance_URL = Resonance_URL.format(categoryId=categoryId[0])
                content = requests.get(
                    Resonance_URL,
                    headers={'User-Agent': self._select_browser_agents_randomly()}).content
                html_txt = re.findall(r'certonaResx\.showResponse\((.*?\})\);', content)

                if len(html_txt) > 0:
                    data = hjson.loads(html_txt[0])
                    schemes = [
                        'thome_rr', 'thome2_rr', 'thome3_rr',
                        'tcategory_rr',
                        'bhome_rr', 'bhome2_rr', 'bhome3_rr'
                        ]
                    for scheme in schemes:
                        ids = response.xpath('//div[@id="{scheme}"]//@id'.format(scheme=scheme)).extract()
                        if len(ids) > 0:
                            for entry in data['Resonance']['Response']:
                                if entry['scheme'] == scheme:
                                    tree = html.fromstring(entry['output'])
                                    scheme_urls = tree.xpath(
                                        '//li[contains(@class,"prodBox")]//a[contains(@class,"prodtitle")]/@href'
                                    )
                                    urls += scheme_urls

            # Toy Box Favorites section
            ToyBoxFavorites_URL = "http://www.hlserve.com/delivery/api/taxonomy?taxonomy=home" \
                            "&hlpt=H&pubpagetype=home&usestate=1&platform=web&_=51331231450" \
                            "&~uid=c718db2c-bad3-4eea-8df4-ad5e2cdce6c0" \
                            "&puserid=%5BCS%5Dv1%7C2C0AAD9705010DBF-60000102600716CA%5BCE%5D" \
                            "&creative=780x450_B-C-OG_TI_4-4_Homepage&minmes=4&maxmes=4&minorganic=0" \
                            "&~it=js&json=hl_c7365396&apiKey=DB1D4221-1C70-46F9-8F5E-26D0B09A40C7"
            content = requests.get(
                ToyBoxFavorites_URL,
                headers={'User-Agent': self._select_browser_agents_randomly()}).content
            html_txt = re.findall(r'\((\{\"ProductAd\"\:.*?\"\})\)', content)

            if len(html_txt) > 0:
                data = hjson.loads(html_txt[0])
                try:
                    for entry in data['ProductAd']:
                        a_url = "http://www.toysrus.com/product/index.jsp?productId=%s" % entry['ProductSKU']
                        urls += [a_url]
                except:
                    pass

            if len(urls) > 0:
                for url in urls:
                    item = SiteProductItem()
                    if shelf_category:
                        item['shelf_name'] = shelf_category
                    if shelf_categories:
                        item['shelf_path'] = shelf_categories
                    yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        spliturl = self.product_url.split('?')
        nextlink = spliturl[0]
        if len(spliturl) == 1:
            return (nextlink + "?page=%d" % self.current_page)
        else:
            nextlink += "?"
            for s in spliturl[1].split('&'):
                if not "page=" in s:
                    nextlink += s + "&"
            return (nextlink + "page=%d" % self.current_page)

    def parse_product(self, response):
        return super(ToysrusShelfPagesSpider, self).parse_product(response)
