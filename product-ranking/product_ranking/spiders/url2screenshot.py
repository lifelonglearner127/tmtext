#
# turns pages into screenshots
#

import base64
import tempfile
import os

import scrapy
from scrapy.conf import settings
from scrapy.http import Request


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
        self.crop_left = kwargs.get('crop_left', 0)
        self.crop_top = kwargs.get('crop_top', 0)
        self.crop_width = kwargs.get('crop_width', None)
        self.crop_height = kwargs.get('crop_height', None)
        self.remove_img = kwargs.get('remove_img', True)

        settings.overrides['ITEM_PIPELINES'] = {}
        super(URL2ScreenshotSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        req = Request(self.product_url)
        req.headers.setdefault('User-Agent', self.user_agent)
        yield req

    def parse(self, response):
        from selenium import webdriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

        # temporary file for the output image
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        t_file.close()
        print('Created temporary image file: %s' % t_file.name)

        # tweak user agent
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self.user_agent

        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))
        try:
            driver.get(self.product_url)
        except Exception as e:
            print('Exception while loading url: %s' % str(e))
        driver.save_screenshot(t_file.name)
        driver.quit()

        # crop the image if needed
        if self.crop_width and self.crop_height:
            self.crop_width = int(self.crop_width)
            self.crop_height = int(self.crop_height)
            from PIL import Image
            # size is width/height
            img = Image.open(t_file.name)
            box = (self.crop_left,
                   self.crop_top,
                   self.crop_left+self.crop_width,
                   self.crop_top+self.crop_height)
            area = img.crop(box)
            area.save(t_file.name, 'png')

        with open(t_file.name, 'rb') as fh:
            img_content = fh.read()

        if self.remove_img is True:
            os.unlink(t_file.name)  # remove old output file

        # create and yield item
        item = ScreenshotItem()
        item['url'] = response.url
        item['image'] = base64.b64encode(img_content)

        yield item