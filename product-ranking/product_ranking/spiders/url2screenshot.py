#
# turns pages into screenshots
#

import base64
import tempfile
import os

import scrapy
from scrapy.conf import settings
from scrapy.http import Request, FormRequest
from scrapy.log import INFO, WARNING, ERROR, DEBUG


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
        self.image_copy = kwargs.get('image_copy', None)
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

    def _get_scrapy_cookies(self, response):
        resp_cookies = [c.split(';') for c in response.headers.getlist('Set-Cookie')]
        cookies_dicts = []
        for cook in resp_cookies:
            _cookie = {}
            for cook_part in cook:
                if not '=' in cook_part:
                    continue
                c_name, c_value = cook_part.split('=', 1)
                c_name = c_name.strip()
                c_value = c_value.strip()
                if c_name not in ('path', 'domain', 'expires'):
                    _cookie['name'] = c_name
                    _cookie['value'] = c_value
            if _cookie:
                cookies_dicts.append(_cookie)
        return cookies_dicts

    def parse(self, response):
        if self._has_captcha(response):
            self.log('Processing captcha at %s' % response.url)
            yield self._handle_captcha(response, self.parse)
            self.log('Captcha processing done at %s' % response.url)
            return

        scrapy_cookies = self._get_scrapy_cookies(response)

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
        driver.get(self.product_url)
        for scrapy_cookie in scrapy_cookies:
            driver.add_cookie(scrapy_cookie)
        try:
            driver.get(self.product_url)
            if self._has_captcha(driver.page_source):
                self.log('Found captcha in PhantomJS response at %s' % driver.current_url)
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
            if self.image_copy:  # save a copy of the file if needed
                area.save(self.image_copy, 'png')

        with open(t_file.name, 'rb') as fh:
            img_content = fh.read()

        if self.remove_img is True:
            os.unlink(t_file.name)  # remove old output file

        # create and yield item
        item = ScreenshotItem()
        item['url'] = response.url
        item['image'] = base64.b64encode(img_content)

        yield item

    def _has_captcha(self, response_or_text):
        if not isinstance(response_or_text, (str, unicode)):
            response_or_text = response_or_text.body_as_unicode()
        return '.images-amazon.com/captcha/' in response_or_text

    def _solve_captcha(self, response):
        forms = response.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src').extract()[0]

        self.log("Extracted capcha url: %s" % captcha_img, level=DEBUG)
        return self._cbw.solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        # FIXME This is untested and wrong.
        captcha_solve_try = response.meta.get('captcha_solve_try', 0)
        url = response.url

        self.log("Captcha challenge for %s (try %d)."
                 % (url, captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)
        if captcha is None:
            self.log(
                "Failed to guess captcha for '%s' (try: %d)." % (
                    url, captcha_solve_try),
                level=ERROR
            )
            result = None
        else:
            self.log(
                "On try %d, submitting captcha '%s' for '%s'." % (
                    captcha_solve_try, captcha, url),
                level=INFO
            )

            meta = response.meta.copy()
            meta['captcha_solve_try'] = captcha_solve_try + 1

            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback,
                dont_filter=True,
                meta=meta)

        return result
