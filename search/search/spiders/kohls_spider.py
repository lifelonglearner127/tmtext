from search.spiders.search_product_spider import SearchProductSpider
from scrapy.selector import HtmlXPathSelector
from spiders_utils import Utils
from scrapy import log
import re

class KohlsSpider(SearchProductSpider):

    name = "kohls"

    # initialize fields specific to this derived spider
    def init_sub(self):
        self.target_site = "kohls"
        self.start_urls = [ "http://www.kohls.com" ]

    def extract_results(self, response):
        hxs = HtmlXPathSelector(response)

        results_relative_urls = hxs.select("//div[@class='product-info']/h2/a/@href").extract()
        results_abs_urls = map(lambda url: "http://www.kohls.com" + url, results_relative_urls)

        return results_abs_urls

    def extract_product_data(self, response, item):
        hxs = HtmlXPathSelector(response)

        try:
            item['product_name'] = hxs.xpath("//h1[@class='title productTitleName']//text()").extract()[0].strip()
        except:
            try:
                item['product_name'] = hxs.xpath("//div[@class='pdp_title']//text()[normalize-space()!='']").extract()[0].strip()
            except:
                self.log("Error: No product name: " + str(response.url) + " from product: " + item['origin_url'], level=log.ERROR)
                # ignore products with no name
                return

        price_node = hxs.select("//meta[@itemprop='price']/@content").extract()

        if price_node:

            try:
                price_currency = price_node[0][0]
                price_amount = "".join(price_node[0][1:])
            
                price_amount = re.sub(",","",price_amount)

                m1 = re.match("[0-9]+\.?[0-9]*", price_amount)
                m2 = re.match("(\xa3)|(\$)", price_currency)
                if not m1 or not m2:
                    self.log("Didn't match product price: " + price_amount + price_currency + " " + response.url + "\n", level=log.WARNING)
                else:
                    price = Utils.convert_to_dollars(float(price_amount), price_currency)
                    item['product_target_price'] = price
            except Exception:
                self.log("Didn't find product price: " + response.url + "\n", level=log.INFO)

        try:
            product_model_node = hxs.select("//div[@class='prod_description1']//li[contains(text(), 'Style')]/text()").re("[sS]tyle +[nN]o\.? +[a-zA-Z0-9]+")
            item['product_model'] = re.match("[sS]tyle +[nN]o\.? +([a-zA-Z0-9]+)", product_model_node[0]).group(1)
        except Exception:
            pass

        try:
            item['product_brand'] = hxs.select("//meta[@itemprop='brand']/@content").extract()[0]
        except Exception:
            pass

        try:
            js_body = hxs.select("//script[contains(text(),'Upc')]/text()").extract()[0]
            item['product_upc'] = re.match('.*"skuUpcCode":"([0-9a-zA-Z]+)".*', js_body, re.DOTALL|re.MULTILINE).group(1)
        except Exception:
            pass

        return item



