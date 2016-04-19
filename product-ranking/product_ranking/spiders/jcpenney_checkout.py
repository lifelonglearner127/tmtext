#
# turns pages into screenshots
#

import base64
import tempfile
import os
import sys
import time
import socket
import random
import re
import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def _get_random_proxy():
    proxy_file = '/tmp/http_proxies.txt'
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as fh:
            lines = [l.strip().replace('http://', '')
                     for l in fh.readlines() if l.strip()]
            return random.choice(lines)


def _get_domain(url):
    return urlparse.urlparse(url).netloc.replace('www.', '')


class JCpenneySpider(scrapy.Spider):
    name = 'jcpenney_checkout_products'
    # allowed_domains = ['*']  # do not remove comment - used in find_spiders()
    available_drivers = ['chromium', 'firefox']

    handle_httpstatus_list = [403, 404, 502, 500]

    SHOPPING_CART_URL = 'http://www.jcpenney.com/jsp/cart/viewShoppingBag.jsp'

    def __init__(self, product_urls, timeout=600, *args, **kwargs):
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0")
        )

        self.product_urls = product_urls
        self.close_popups = kwargs.get('close_popups', kwargs.get('close_popup', None))
        self.driver = kwargs.get('driver', None)  # if None, then a random UA will be used
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.timeout = timeout
        self.disable_site_settings = kwargs.get('disable_site_settings', None)
        
        self.driver = self.init_driver(name="firefox")
        self.wait = WebDriverWait(self.driver, 25)
        socket.setdefaulttimeout(int(self.timeout))
        
        settings.overrides['ITEM_PIPELINES'] = {}
        super(JCpenneySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for product_url in self.product_urls.split('|'):
            # Open product URL
            self._parse_product(product_url)


        self._parse_shopping_cart()
        return None

    def _parse_product(self, product_url):
        self.driver.get(product_url)
        # Click add button
        self._click_on_element_with_id('addtobagbopus')
        time.sleep(6)
        
    def _parse_shopping_cart(self):
        self.driver.get(self.SHOPPING_CART_URL)
        # print "element"
        # element = self.wait.until(EC.visibility_of_element_located((By.ID, 'shoppingBagPageId')))
        # print "disponible"
        # from scrapy import Selector
        elements = driver.find_elements(By.ID, 'shoppingBagPageId')
        if elements:
            selector = Selector(text=elements[0].get_attribute('outerHTML'))
            print selector.xpath('//*[@class="brand_name flt_lft bp-brand-name"]/a/text()')
        else:
            "Not elements founds"

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

    def _click_on_elements_with_class(self, driver, cls):
        script = """
            var elements = document.getElementsByClassName('%s');
            for (var i=0; i<elements.length; i++) {
                elements[i].click();
            }
        """ % cls
        try:
            driver.execute_script(script)
        except Exception as e:
            self.log('Error on clicking (JS) element with class %s: %s' % (cls, str(e)))
        try:
            for element in driver.find_elements_by_class_name(cls):
                element.click()
        except Exception as e:
            self.log('Error on clicking element with class %s: %s' % (cls, str(e)))

    def _click_on_element_with_id(self, _id):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.ID, _id)))
            element.click()
        except Exception as e:
            self.log('Error on clicking element with ID %s: %s' % (_id, str(e)))

    def _click_on_element_with_xpath(self, driver, xpath):
        try:
            for element in driver.find_elements_by_xpath(xpath):
                element.click()
        except Exception as e:
            self.log('Error on clicking elements with XPath %s: %s' % (xpath, str(e)))

    def _remove_element_with_xpath(self, driver, xpath):
        try:
            for element in driver.find_elements_by_xpath(xpath):
                driver.execute_script("""
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """, element)
        except Exception as e:
            self.log('Error on removing elements with XPath %s: %s' % (xpath, str(e)))

    def _choose_another_driver(self):
        for d in self.available_drivers:
            if d != self._driver:
                return d

    def _init_chromium(self):
        from selenium import webdriver
        chrome_flags = webdriver.DesiredCapabilities.CHROME  # this is for Chrome?
        chrome_options = webdriver.ChromeOptions()  # this is for Chromium
        if self.proxy:
            chrome_options.add_argument(
                '--proxy-server=%s' % self.proxy_type+'://'+self.proxy)
        chrome_flags["chrome.switches"] = ['--user-agent=%s' % self.user_agent]
        chrome_options.add_argument('--user-agent=%s' % self.user_agent)
        executable_path = '/usr/sbin/chromedriver'
        if not os.path.exists(executable_path):
            executable_path = '/usr/local/bin/chromedriver'
        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.Chrome(desired_capabilities=chrome_flags,
                                      chrome_options=chrome_options,
                                      executable_path=executable_path)
        return driver

    def _init_firefox(self):
        from selenium import webdriver
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
        profile.set_preference("network.proxy.type", 1)  # manual proxy configuration
        if self.proxy:
            if 'socks' in self.proxy_type:
                profile.set_preference("network.proxy.socks", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.socks_port", int(self.proxy.split(':')[1]))
            else:
                profile.set_preference("network.proxy.http", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.http_port", int(self.proxy.split(':')[1]))
        profile.update_preferences()
        driver = webdriver.Firefox(profile)
        return driver

    def init_driver(self, name=None):
        if name:
            self._driver = name
        else:
            if not self.driver:
                self._driver = 'chromium'
            elif self.driver == 'random':
                self._driver = random.choice(self.available_drivers)
            else:
                self._driver = self.driver
        print('Using driver: ' + self._driver)
        self.log('Using driver: ' + self._driver)
        init_driver = getattr(self, '_init_'+self._driver)
        return init_driver()

    @staticmethod
    def _get_proxy_ip(driver):
        driver.get('http://icanhazip.com')
        ip = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', driver.page_source)
        if ip:
            ip = ip.group(1)
            return ip

    def parse(self, response):
        socket.setdefaulttimeout(int(self.timeout))

        # temporary file for the output image
        t_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        t_file.close()
        print('Created temporary image file: %s' % t_file.name)
        self.log('Created temporary image file: %s' % t_file.name)

        display = Display(visible=0, size=(self.width, self.height))
        display.start()

        # we will use requesocks for checking response code
        r_session = requests.session()
        r_session.timeout = self.timeout
        #if self.proxy:
        #    r_session.proxies = {'http': self.proxy_type+'://'+self.proxy,
        #                         'https': self.proxy_type+'://'+self.proxy}
        if self.user_agent:
            r_session.headers = {'User-Agent': self.user_agent}

        # check if the page returns code != 200
        if self.code_200_required and str(self.code_200_required).lower() not in ('0', 'false', 'off'):
            page_code = r_session.get(self.product_url, verify=False).status_code
            if page_code != 200:
                self.log('Page returned code %s at %s' % (page_code, self.product_url), ERROR)
                yield ScreenshotItem()  # return empty item
                display.stop()
                return

        driver = self.init_driver()
        item = ScreenshotItem()

        if self.proxy:
            ip_via_proxy = URL2ScreenshotSpider._get_proxy_ip(driver)
            item['via_proxy'] = ip_via_proxy
            print 'IP via proxy:', ip_via_proxy
            self.log('IP via proxy: %s' % ip_via_proxy)

        try:
            self.prepare_driver(driver)
            self.make_screenshot(driver, t_file.name)
        except Exception as e:
            self.log('Exception while getting response using selenium! %s' % str(e))
            # lets try with another driver
            another_driver_name = self._choose_another_driver()
            try:
                driver.quit()  # clean RAM
            except Exception as e:
                pass
            driver = self.init_driver(name=another_driver_name)
            self.prepare_driver(driver)
            self.make_screenshot(driver, t_file.name)
            try:
                driver.quit()
            except:
                pass

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

        # yield the item
        item['url'] = response.url
        item['image'] = base64.b64encode(img_content)
        item['site_settings'] = getattr(self, '_site_settings_activated_for', None)

        display.stop()

        if img_content:
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