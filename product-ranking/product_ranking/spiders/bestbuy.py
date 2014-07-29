from scrapy.selector import Selector
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class BestBuyProductSpider(BaseProductsSpider):
    name = 'bestbuy_products'
    allowed_domains = ["bestbuy.com"]

    SEARCH_URL = "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-" \
                 "8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=15&sp=&qp=" \
                 "&list=n&iht=y&usc=All+Categories&ks=960&st={search_term}"

    def parse_product(self, response):
        sel = Selector(response)
        prod = response.meta['product']

        self._populate_from_html(response.url, sel, prod)

        return prod

    def _populate_from_html(self, url, sel, product):
        cond_set(product, 'title',
                 sel.xpath("//*[@itemprop='name']/a/text()").extract())
        cond_set(product, 'price',
                 sel.xpath("//*[@itemprop='price']/text()").extract())
        cond_set(product, 'upc',
                 sel.xpath("//*[@class='hproduct']/div[3]/div[1]/h5[2]/strong/text()").extract())
        cond_set(product, 'model',
                 sel.xpath("//*[@class='hproduct']/div[3]/div[1]/h5[1]/strong/text()").extract())
        cond_set(product, 'image_url',
                 sel.xpath("//*[@itemprop='image']/@src").extract())
        cond_set(product, 'brand',
                 sel.xpath("//*[@itemprop='manufacturer']/span/@content").extract())
        cond_set(product, 'description',
                 sel.xpath("//*[@itemprop='description']/text()").extract())
        cond_set(product, 'locale', ['en-US'])  # Default locale.


    def _scrape_product_links(self, sel):
        links = sel.xpath("//*[@itemprop='name']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):
        mynum = sel.css("#searchstate > b:nth-child(1)::text").extract()
        mynum = mynum[0]
        if mynum:
            return int(mynum)
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css(".padbar ul.pagination a.next::attr(href)").extract()
        next_page = None
        if len(next_pages) == 2:
            next_page = next_pages[0]
        elif len(next_pages) > 2:
            self.log("Found more than two 'next page' link.", ERROR)
        return next_page


