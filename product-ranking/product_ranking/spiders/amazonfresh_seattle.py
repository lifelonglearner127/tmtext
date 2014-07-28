from amazonfresh_southerncalifornia import AmazonFreshSCProductsSpider


class AmazonFreshSeattleProductsSpider(AmazonFreshSCProductsSpider):
    name = "amazonfresh_seattle_products"
    allowed_domains = ["fresh.amazon.com"]
    start_urls = []
    SEARCH_URL = "https://fresh.amazon.com/Search?browseMP=A83PXQN2224PA" \
                 "&resultsPerPage=50" \
                 "&predictiveSearchFlag=false&recipeSearchFlag=false" \
                 "&comNow=&input={search_term}"