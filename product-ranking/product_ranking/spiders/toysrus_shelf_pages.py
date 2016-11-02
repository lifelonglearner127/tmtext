import re
import urlparse

import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None

from .toysrus import ToysrusProductsSpider


class ToysrusShelfPagesSpider(ToysrusProductsSpider):
    name = 'toysrus_shelf_urls_products'
    allowed_domains = ["toysrus.com", "www.toysrus.com"]  # without this find_spiders() fails

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
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories

            Resonance_URL = "http://www.res-x.com/ws/r2/Resonance.aspx?appid=toysrus01" \
                            "&tk=91392014501448&sg=1&vr=5.5x&bx=true&sc=thome_rr&sc=thome2_rr" \
                            "&sc=thome3_rr&no=16&siteid=TRU&pagetype=home&cb=certonaResx.showResponse" \
                            "&cv1=&cv2=0158136c2dc000770491f0442d000506d00380650093c" \
                            "&ur=http%3A%2F%2Fwww.toysrus.com%2Fshop%2Findex.jsp%3FcategoryId%3D2255956&plk=&rf="

            resonance_URLs = Request(
                    Resonance_URL,
                    dont_filter=True,
                    callback=self.parse_resonance
            )
            yield resonance_URLs

            toyboxfavorites_URL = "http://www.hlserve.com/delivery/api/taxonomy?taxonomy=home" \
                                  "&hlpt=H&pubpagetype=home&usestate=1&platform=web" \
                                  "&puserid=%5BCS%5Dv1%7C2C0AAD9705010DBF-60000102600716CA%5BCE%5D" \
                                  "&creative=780x450_B-C-OG_TI_4-4_Homepage&minmes=4" \
                                  "&maxmes=4&minorganic=0&~it=js&json=hl_c4265876" \
                                  "&apiKey=DB1D4221-1C70-46F9-8F5E-26D0B09A40C7"
            # reqs.append(
            #     Request(
            #         toyboxfavorites_URL,
            #         dont_filter=True,
            #         callback=self.parse_toyboxfavorites
            #     )
            # )
            # yield Request(
            #         toyboxfavorites_URL,
            #         dont_filter=True,
            #         callback=self.parse_toyboxfavorites
            #         ), item

            # if reqs:
            #     return self.send_next_request(reqs, response)
            # return

    def parse_resonance(self, response):
        urls = [
            "http://beam.hlserve.com/beacon?fid=128&bd=1477966741&hl_qs=tCKx3Iu5JbI8WZgbo1wn%2BxZMGKSTIx5BXzb3lVWTvk1VlMBq%2B9BcpZrDdsuUShud7c0xsBkNh3k393fpLWDQWLgtqEztr63EHZaMAa3KB2668c6sQqYMXfuBu17A%2FnnnjgXrykexs8rk1E3WG%2Bh68tMsbzWFZgZVI7CMQJ7WXmdIVFu7rndbhkQc1IdckIl4o38S1p31trzPBJNbXZZm%2F0SugYKy5SAK%2BLdA%2BjSEPjhSPi2DUvcr%2F7ZWONkjgTKkIXwqjxrfXKk%2Bam5C0TYoNp1NKQLRoMKQwISrJOyvnkbUT%2Fg7rqEqUUGzYNFdCfWeN%2BmIQz5thYvFTDQ9RFHIIIyagjz%2FbDIDBmujggn9Ns%2BVBw5Uk0eWxISRTM5ESjhuIDP%2Bd9dFuSCowo76WBhc911ZL6fVIZPHDxtmioJzhbbYiEUqt7unWDRFNWdVlKk%2F28dnXluRDKJxGqxcGYWJso8eKVlk8dfMhlA%2BdpRXUMk56g%2FmxV1JTz3EGOLydh8DloVOeR5pwdNk0nWzFoxcjTefqvaT2z2wB9%2BDd3ssAtlKAG9GQUMrRjMiVDpGm%2F%2BETC0NXXeHI%2BvSyPRDZcyy6RbTQGWJQP6JYbtQNCd4%2FWwCRJ%2FZ%2B9VuM%2FJ%2FEnOVWPeD0qcKN7Wy%2FbbyLuCNcc19GcmZM8Bny%2FitkjbLdpTqoOWM676zrheex9fcoSZn8ciGCku1ASX7FvfY%2BmFSLUSm0PkCVjGen8ZlrErX7I7BlvRPri8J3OCFf%2Ff2w6ntnSg%2Fmexvw%2F71NaMA6QDe7E0GfpLyYyZk1gp4EYdLfUEnpk27JCVuCmu2xCAf%2FIO4Rs3mfvaAnBx4Pt23Sd7Xs%2FV6oVmNZ4NF8M66kYQA86%2FX9XDEdbgWGe6QyjOr9KUz9QYBVPBZqQ3FtgJ07wczogC8Pq4AYYwIQwUCI7K7JYwZCBxKrOJ7w2QDFZzse2ylRn5IT2E2AenOkGBcxsxcmXXlpZjlvQXRErbxMwuCJVHT9JMzTjyWxa3HvA%2FCuuxzPZP2ZFRYqhWvjR5Egn%2Fcz6kjs1yqeBVzq0UnGXOPwPuuxJE%3D&ev=1&action=click&hmguid=a9dc05b3-74ef-442c-1146-0ec05ac36185&impressionpid=220fd9d3-39a8-41a7-9054-c6a968b693de%3A0&rn=460498438&dest=http%3A%2F%2Fwww.toysrus.com%2Fproduct%2Findex.jsp%3FproductId%3D101687166",
            "http://beam.hlserve.com/beacon?fid=128&bd=1477966741&hl_qs=A4HOTpB5Tl6KIJ3jMjt9RSxbguhqXYzuDvb7AaQHWmiauloMumOwNynuzr0rVC7irgZ86Az7fmhzuxfTcL%2ByYHYpBrGsUmy2W66rQZzbgtGGx9nIs%2FmK2e3Rum6%2FfkzHBX8TfJpRuLS07p1oSik%2BBJcQPcB58nQ9SUnqOOLed0ZCJEU2S7R60M8N%2Flr5er%2FF2pl5uF3sqLoc6nVRqZEFcT651SY1ccGiaxPd44vl7ylTw%2BRst0V1TVqPbIieqXlAEdpKbTzC%2BYPpBtXnfwdeVR8tHjB3nxIco64yXgm6bBQ2YmluscgB2yrBkWRJ%2FI2c0CEa4SUvAPhwNygZEACBaypAjFXhOX5gHzriRxTBDQJ5JNc5LfcSwVHGeLDzn%2BKk3mpx%2B3EU%2FOI9ikkKPI8yaa2OfO%2FGqFcZ%2FwwDMOOSsatHrbOmwS3CGeTdLcXYglPuk2hlqacFymnob8RvKw6txDNU%2BkFovM44DVCZ%2FOK7T24fYLUn9cY3fjXahUT77C9exzQysb3ofaEI660tMa6WWU3agAW0sqBPVCyL0xYT9zoOeK6XGFtnGXr74SLFiEYUeMeQAgxkxrNVE3ZYrGDRWG6kCRv3YNMALT9tXSy%2BRo0Ck0V7%2BwgqOXNTay8WUNhxhoV%2Bq0%2FwTE7JqvIFKFWCfEQAcFDmb9Ewmy6vpF0HFcny348O%2Bb%2FdRZNtX2cJSj3W%2FKGm%2BDpVCO2o%2FP%2BpVo7A4bD1YtN4dSNlOEX4WTjyW5%2BEg6T2fO95fQrmA25OntS4cMcXuXkKoUlLd2xFd2cLjPjqWdgG4td3JdEZqlY9pxcAmnoCnfkeg%2FtuHOB0Xh7r9x7Y1oHX5wgfc8%2B9q2UPMudKi4S79prHbJPzcgP9NcSYsHYIC7vVBiOouYeBn9fRlxhwSMgGTPYCbJhEEnxQT41Oi05UHfFtT0gCbo2ZX%2BnDz64w96rA12lK9G5Y0D%2FuhsT3VOj72ElrvyHckvIAI4JDvw8X3wh4E0lUYezVmVdfXRDZTt2f6BdYkE3toCvwvmL7s8MrgwKpTtzpuF0ADg%3D%3D&ev=1&action=click&hmguid=a9dc05b3-74ef-442c-1146-0ec05ac36185&impressionpid=220fd9d3-39a8-41a7-9054-c6a968b693de%3A1&rn=506776886&dest=http%3A%2F%2Fwww.toysrus.com%2Fproduct%2Findex.jsp%3FproductId%3D60959146"
        ]
        for u in urls:
            yield u, SiteProductItem()


    def parse_toyboxfavorites(self, response):
        new_meta = dict(response.meta)
        item = new_meta['item']
        return

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        :rtype : object
        """
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

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