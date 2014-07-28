import urlparse
from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class AmazonFreshSCProductsSpider(BaseProductsSpider):
    name = "amazonfresh_southerncalifornia_products"
    allowed_domains = ["fresh.amazon.com"]
    start_urls = []
    SEARCH_URL = "https://fresh.amazon.com/Search?browseMP=A241IQ0793UAL2" \
                 "&resultsPerPage=50" \
                 "&predictiveSearchFlag=false&recipeSearchFlag=false" \
                 "&comNow=&input={search_term}"


    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//div[@class="buying"]/h1/text()').extract()
        brand = response.xpath('//div[@class="byline"]/a/text()').extract()
        price = response.xpath('//div[@class="price"]/span[@class="value"]/text()').extract()
        des = response.xpath('//*[@id="productDescription"]/p/text()').extract()
        img_url = response.xpath('//div[@id="mainImgWrapper"]/img/@src').extract()
        prod['title'] = title[0].strip() if title else ''
        prod['brand'] = brand[0].strip() if brand else ''
        prod['price'] = price[0].strip() if price else  ''
        prod['description'] = des[0].strip() if des else ''
        prod['image_url'] = img_url[0].strip() if img_url else ''
        prod['url'] = response.url
        # GET ASIN instead of model
        paras = urlparse.parse_qs(urlparse.urlsplit(response.url).query)
        prod['model'] = paras['asin'][0] if paras.has_key('asin') else ''
        if prod['title']:
            cond_set(prod, 'locale', ['en-US'])
            return prod
        return None


    def _search_page_error(self, response):
        try:
            found1 = response.xpath('//div[@class="warning"]/p/text()').extract()[0]
            found2 = response.xpath('//div[@class="warning"]/p/strong/text()').extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except:
            return False


    def _scrape_total_matches(self, sel):
        count = sel.xpath('//div[@class="numberOfResults"]/text()').re('(\d+)')[-1]
        if count:
            return int(count)
        return 0


    def _scrape_product_links(self, sel):
        for link in sel.xpath('//div[@class="itemDetails"]/h4/a/@href').extract():
            yield link, SiteProductItem()


    def _scrape_next_results_page_link(self, sel):
        try:
            link = sel.xpath('//div[@class="pagination"]/a/@href').extract()[-1]
            return link
        except:
            self.log("AmazoFresh crawler error: Can't get the next page", ERROR)
            return None