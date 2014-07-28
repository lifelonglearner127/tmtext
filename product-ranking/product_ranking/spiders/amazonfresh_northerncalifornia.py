from amazonfresh_southerncalifornia import AmazonFreshSCProductsSpider


class AmazonFreshNCProductsSpider(AmazonFreshSCProductsSpider):
    name = "amazonfresh_northerncalifornia_products"
    allowed_domains = ["fresh.amazon.com"]
    start_urls = []
    SEARCH_URL = "https://fresh.amazon.com/Search?browseMP=A3FX2TOAMS7SFL" \
                 "&resultsPerPage=50" \
                 "&predictiveSearchFlag=false&recipeSearchFlag=false" \
                 "&comNow=&input={search_term}"



