from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR

import urllib2
import json

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, \
    FormatterWithDefaults, cond_set_value


class ArgosProductsSpider(BaseProductsSpider):

    """Implements a very basic spider for Argos.co.uk.
    """

    name = 'argos_products'
    allowed_domains = ["argos.co.uk"]

    SEARCH_URL = "http://www.argos.co.uk/static/Search/fs/0/p/1/pp/50/q/" \
        "{search_term}/s/Relevance.htm"

    def __init__(self, *args, **kwargs):
        super(ArgosProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
            ),
            *args, **kwargs)

    def parse_product(self, response):

        prod = response.meta['product']

        prod['locale'] = "en-UK"

        prod['title'] = response.xpath(
            '//h1[@class="fn"]//text()'
        ).extract()[0].strip()

        description_xpath = response.xpath(
            "//div[@class='fullDetails']//text()"
        ).extract()

        for el in description_xpath:
            if "EAN:" in el:
                prod['upc'] = el[5:-1]

        description_text = "".join(description_xpath).strip()

        cond_set_value(prod, 'description', description_text)

        prod['price'] = response.xpath(
            "//div[@class='content']"
            "/div[@id='pdpProductInformation']"
            "/div[@id='pdpRightBar']"
            "/div[@id='pdpPricing']"
            "/span[@class='actualprice']"
            "/span[@class='price']//text()"
        ).extract()[1]

        prod['url'] = response.url

        # catching image from XHR

        prod_id = response.url.split("/")[-1].replace(".htm","")

        find_set_url = 'http://argos.scene7.com/is/image/Argos?req=set,json&imageSet='+prod_id+'_R_SET'

        catch_ajax = urllib2.urlopen(
            find_set_url).read()

        catch_ajax = catch_ajax.replace("s7jsonResponse(","")
        catch_ajax = catch_ajax.replace(',"");','')
        
        # self.log( "ff: " + find_set_url)
        # self.log( "cc: " + catch_ajax)

        try:

            decoded = json.loads(catch_ajax)

            if type(decoded['set']['item']) is dict:
                img = decoded['set']['item']['i']['n']  

            if type(decoded['set']['item']) is list:
                img = decoded['set']['item'][0]['i']['n'] 

            prod['image_url'] = "http://argos.scene7.com/is/image/"+img+"?$TMB$&wid=312&hei=312"

        except:
            pass    


        # related - TBD
        # http://service.avail.net/2009-02-13/dynamic/38e5c972-174d-11e0-a152-12313b032222/scr?r=js&s=D8E1EC3E-4F43-4A4E-B0C8-EAA58049BF6F&q={%22ret0%22:[%22getRecommendations%22,{%22TemplateName%22:%2233016918_Technology_Xbox_360_YouMayAlsoLike%22,%22Input%22:[%22ProductId:9130005%22],%22ColumnNames%22:[%22ProductId%22],%22DynamicParameters%22:[]}],%22ret1%22:[%22getRecommendations%22,{%22TemplateName%22:%22ProductPage_Alternatives%22,%22Input%22:[%22ProductId:9130005%22],%22ColumnNames%22:[%22ProductId%22],%22DynamicParameters%22:[]}]}
        # http://www.argos.co.uk/webapp/wcs/stores/servlet/FetchProductDetailsForP2P?storeId=10151&langId=110&partNumberCsv=1337600,1388903,1985306,1528897,191634,191636,138082


        return prod

    def _search_page_error(self, response):
        if not self._scrape_total_matches(response):
            self.log("Argos: unable to find a match", ERROR)
            return True
        return False

    def _scrape_total_matches(self, response):
        try:
            count = response.xpath(
                "//li[@class='extrainfo totalresults']/text()"
            ).re('(\d+)')[-1]
            if count:
                return int(count)
            return 0
        except IndexError:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//a[@class='desc nogrouping']/@href"
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            "//a[contains(text(),'Next >')]/@href"
        ).extract()
        if links:
            link = links[0]
        else:
            link = None

        return link
