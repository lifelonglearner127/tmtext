#
# turns pages into screenshots
#

import base64
import tempfile
import os

import scrapy
from scrapy.conf import settings
from scrapy.log import WARNING, ERROR
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem


class ScreenshotItem(scrapy.Item):
    url = scrapy.Field()
    image = scrapy.Field()


class URL2ScreenshotSpider(scrapy.Spider):
    name = 'url2screenshot_products'

    def __init__(self, *args, **kwargs):
        self.product_url = kwargs['product_url']
        self.width = kwargs.get('width', 1280)
        self.height = kwargs.get('height', 1024)
        self.timeout = kwargs.get('timeout', 30)
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
             "(KHTML, like Gecko) Chrome/15.0.87")
        )
        settings.overrides['ITEM_PIPELINES'] = {}
        super(URL2ScreenshotSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        req = Request(self.product_url)
        req.headers.setdefault('User-Agent', self.user_agent)
        yield req

    def parse(self, response):
        from selenium import webdriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

        t_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        t_file.close()

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self.user_agent

        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))
        try:
            driver.get(self.product_url)
        except Exception as e:
            print('Exception while loading url: %s' % str(e))
        driver.save_screenshot(t_file.name)
        driver.quit()

        with open(t_file.name, 'rb') as fh:
            img_content = fh.read()

        os.unlink(t_file.name)

        item = ScreenshotItem()
        item['url'] = response.url
        item['image'] = base64.b64encode(img_content)

        yield item