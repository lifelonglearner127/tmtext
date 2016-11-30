import resource
from extract_walmart_data import WalmartScraper

url = 'https://www.walmart.com/ip/42719028'

print 'A', 'Memory usage: %s' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000)

site_scraper = WalmartScraper(url=url, bot=None)
var = site_scraper.product_info()
del var

print 'B', 'Memory usage: %s' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000)

site_scraper = WalmartScraper(url=url, bot=None)
var = site_scraper.product_info()
del var

print 'C', 'Memory usage: %s' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000)

site_scraper = WalmartScraper(url=url, bot=None)
var = site_scraper.product_info()
del var

print 'D', 'Memory usage: %s' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000)
