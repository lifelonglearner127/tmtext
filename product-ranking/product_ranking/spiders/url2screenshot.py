#
# turns pages into screenshots
#

import base64
import tempfile
import os
import sys
import time
import socket

import scrapy
from scrapy.conf import settings
from scrapy.http import Request, FormRequest
from scrapy.log import INFO, WARNING, ERROR, DEBUG
import lxml.html
try:
    from pyvirtualdisplay import Display
except ImportError:
    print('pyvirtualdisplay not installed')

try:
    import requesocks as requests
except ImportError:
    import requests

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', '..', '..', '..'))

try:
    from search.captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    CaptchaBreakerWrapper = None
    print 'Error loading captcha breaker!', str(e)


class ScreenshotItem(scrapy.Item):
    url = scrapy.Field()
    image = scrapy.Field()

    def __repr__(self):
        return '[image data]'  # don't dump image data into logs


class URL2ScreenshotSpider(scrapy.Spider):
    name = 'url2screenshot_products'
    # allowed_domains = ['*']  # do not remove comment - used in find_spiders()

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
        # proxy support has been dropped after we switched to Firefox
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.code_200_required = kwargs.get('code_200_required', True)

        settings.overrides['ITEM_PIPELINES'] = {}
        super(URL2ScreenshotSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        req = Request(self.product_url)
        req.headers.setdefault('User-Agent', self.user_agent)
        yield req

    def _solve_captha_in_selenium(self, driver, max_tries=15):
        for i in xrange(max_tries):
            if self._has_captcha(driver.page_source):
                self.log('Found captcha in selenium response at %s' % driver.current_url)
                driver.save_screenshot('/tmp/_captcha_pre.png')
                captcha_text = self._solve_captcha(driver.page_source)
                self.log('Recognized captcha text is %s' % captcha_text)
                driver.execute_script("document.getElementById('captchacharacters').value='%s'" % captcha_text)
                time.sleep(2)
                driver.save_screenshot('/tmp/_captcha_text.png')
                driver.execute_script("document.getElementsByTagName('button')[0].click()")
                time.sleep(2)
                driver.save_screenshot('/tmp/_captcha_after.png')

    def _log_proxy(self, r_session):
        self.log("IP via proxy: %s" % r_session.get('http://icanhazip.com').text)

    def parse(self, response):

        from selenium import webdriver
        from selenium.webdriver import FirefoxProfile

        socket.setdefaulttimeout(self.timeout)

        # temporary file for the output image
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        t_file.close()
        print('Created temporary image file: %s' % t_file.name)

        # tweak user agent
        ff_profile = FirefoxProfile()
        ff_profile.set_preference("general.useragent.override", self.user_agent)

        display = Display(visible=0, size=(self.width, self.height))
        display.start()

        # we will use requesocks for checking response code
        r_session = requests.session()
        r_session.timeout = self.timeout
        if self.proxy:
            r_session.proxies = {'http': self.proxy_type+'://'+self.proxy,
                                 'https': self.proxy_type+'://'+self.proxy}
        if self.user_agent:
            r_session.headers = {'User-Agent': self.user_agent}
        self._log_proxy(r_session)

        # check if the page returns code != 200
        if self.code_200_required and str(self.code_200_required).lower() not in ('0', 'false', 'off'):
            page_code = r_session.get(self.product_url).status_code
            if page_code != 200:
                self.log('Page returned code %s at %s' % (page_code, self.product_url), ERROR)
                yield ScreenshotItem()  # return empty item
                display.stop()
                return

        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.Firefox(ff_profile)
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_script_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))

        try:
            driver.get(self.product_url)
            self._solve_captha_in_selenium(driver)
        except Exception as e:
            self.log('Exception while getting response using selenium! %s' % str(e))

        time.sleep(10)
        driver.save_screenshot(t_file.name)
        if self.image_copy:  # save a copy of the file if needed
            driver.save_screenshot(self.image_copy)
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

        display.stop()

        yield item

    def _has_captcha(self, response_or_text):
        if not isinstance(response_or_text, (str, unicode)):
            response_or_text = response_or_text.body_as_unicode()
        return '.images-amazon.com/captcha/' in response_or_text

    def _solve_captcha(self, response_or_text):
        if not isinstance(response_or_text, (str, unicode)):
            response_or_text = response_or_text.body_as_unicode()
        doc = lxml.html.fromstring(response_or_text)
        forms = doc.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src')[0]

        self.log("Extracted capcha url: %s" % captcha_img, level=WARNING)

        return CaptchaBreakerWrapper().solve_captcha(captcha_img)

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
