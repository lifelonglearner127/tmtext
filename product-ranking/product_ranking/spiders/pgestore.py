from scrapy.selector import Selector
from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR
import re



class PGEStoreProductSpider(BaseProductsSpider):
    name = 'pgestore_products'
    allowed_domains = ["pgestore.com"]

    SEARCH_URL = "http://www.pgestore.com/on/demandware.store/Sites-PG-Site/default/Search-Show?q={search_term}"

    def parse_product(self, response):
        sel = Selector(response)
        prod = response.meta['product']
        self._populate_from_html(response.url, sel, prod)

        result = prod
        return result

    def _populate_from_html(self, url, sel, product):

        re1 = '.*?(\'(.*\w))'
        rg = re.compile(re1, re.IGNORECASE | re.DOTALL)
        m = rg.search(sel.xpath("//*[@id='pdpMain']/div[1]/script[2]/text()").extract()[0])
        if m:
            brand = m.group(2)
        else:
            self.log("Found no brand name.", ERROR)

        cond_set(product, 'title',
                 sel.xpath("//*[@id='pdpMain']/div[2]/h1/text()").extract())
        cond_set(product, 'upc',
                 sel.xpath("//*[@id='prodSku']/text()").extract())
        cond_set(product, 'image_url',
                 sel.xpath("//*[@id='pdpMain']/div[1]/div[2]/img/@src").extract())
        product['brand'] = brand
        product['price'] = sel.xpath("//*[@id='pdpATCDivpdpMain']/div[1]/div[7]/div[1]/div/div/div/text()") \
            .extract()[0].strip()
        description = sel.xpath("//*[@id='pdpTab1']/div/text()").extract()
        description.extend(sel.xpath("//*[@id='pdpTab1']/div/ul/li/text()").extract())
        cond_set(product, 'description',
                 description)
        cond_set(product, 'locale', ['en-US'])  # Default locale.

        #self.parse_related_products(sel.response)

    def parse_related_products(self, response):
        sel = Selector(response)
        product = response.meta['product']

        data = sel.xpath("//*[@id='crossSell']/script[1]/@src").extract()[0]

        otherproducts = sel.xpath("//*[@id='gmm']/div[1]/text()").extract()[0].strip()
        urls = sel.xpath("//*[@id='igdrec_2']/div[2]/div[1]/a[1]/@href").extract()
        titles = sel.xpath("//*[@id='igdrec_2']/div[1]/h2/text()").extract()
        if otherproducts == "Other Shoppers Purchased":
            product['related_products'] = {
                "Other Shoppers Purchased": list(
                    RelatedProduct(title, url)
                    for url in sel.xpath("//*[@id='igdrec_2']/div[2]/div[1]/a[2]/@href").extract()
                    for title in sel.xpath("//*[@id='igdrec_2']/div[2]/div[1]/a[2]/text()").extract()
                ),
            }

        return product

    def _scrape_product_links(self, sel):
        links = sel.xpath("//*[@class='description']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):
        mynum = sel.xpath("//*[@id='deptmainheaderinfo']/text()").extract()
        words = mynum[0].split(" ")
        if words[2]:
            return int(words[2])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        # next_pages = sel.css(".padbar ul.pagination a.next::attr(href)").extract()
        next_pages = sel.xpath("//*[@id='pdpTab1']/div[3]/div[1]/ul/li[6]/a/@href").extract()
        next_page = None
        if len(next_pages) == 1:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page



