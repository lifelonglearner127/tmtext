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
import shutil
import datetime
from requests.auth import HTTPProxyAuth

import scrapy
from scrapy.conf import settings
from scrapy.http import Request, FormRequest
from scrapy.log import INFO, WARNING, ERROR
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

DEBUG_MODE = False  # TODO! fix

try:
    from search.captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    CaptchaBreakerWrapper = None
    print 'Error loading captcha breaker!', str(e)


class ScreenshotItem(scrapy.Item):
    url = scrapy.Field()
    image = scrapy.Field()
    via_proxy = scrapy.Field()  # IP via webdriver
    site_settings = scrapy.Field()  # site-specified settings that were activated (if any)

    def __repr__(self):
        return '[image data]'  # don't dump image data into logs


def _get_random_proxy():
    proxy_file = '/tmp/http_proxies.txt'
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as fh:
            lines = [l.strip().replace('http://', '')
                     for l in fh.readlines() if l.strip()]
            return random.choice(lines)


def _get_domain(url):
    return urlparse.urlparse(url).netloc.replace('www.', '')

"""
def authenticate_driver_and_get(driver, url):
    driver.set_page_load_timeout(60)
    # handle http basic auth for Crawlera proxy, if needed

    driver.get(url)

    from selenium.webdriver.common.alert import Alert
    time.sleep(3)
    alert = Alert(driver)
    time.sleep(3)
    #alert.authenticate(CRAWLERA_APIKEY, '')
    #import pdb; pdb.set_trace()
    alert.send_keys(settings['CRAWLERA_APIKEY'] + '\n')
    alert.accept()
    #alert.send_keys('\t')
    #alert.send_keys('\n')
    #import pdb; pdb.set_trace()
    driver.set_page_load_timeout(30)
"""


def _check_bad_results_macys(driver):
    if u'something went wrong' in driver.page_source.lower():
        return True
    if u'Access Denied' in driver.page_source and u"You don't have permission" in driver.page_source:
        return True


class URL2ScreenshotSpider(scrapy.Spider):
    name = 'url2screenshot_products'
    # allowed_domains = ['*']  # do not remove comment - used in find_spiders()
    available_drivers = ['chromium', 'firefox']

    handle_httpstatus_list = [403, 404, 502, 500]

    def __init__(self, *args, **kwargs):
        self.product_url = kwargs['product_url']
        self.width = kwargs.get('width', 1280)
        self.height = kwargs.get('height', 1024)
        self.timeout = kwargs.get('timeout', 60)
        self.image_copy = kwargs.get('image_copy', None)
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0")
        )
        self.crop_left = kwargs.get('crop_left', 0)
        self.crop_top = kwargs.get('crop_top', 0)
        self.crop_width = kwargs.get('crop_width', None)
        self.crop_height = kwargs.get('crop_height', None)
        self.remove_img = kwargs.get('remove_img', True)
        # proxy support has been dropped after we switched to Chrome
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_auth = None
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.code_200_required = kwargs.get('code_200_required', True)
        self.close_popups = kwargs.get('close_popups', kwargs.get('close_popup', None))
        self.driver = kwargs.get('driver', None)  # if None, then a random UA will be used

        self.disable_site_settings = kwargs.get('disable_site_settings', None)
        if not self.disable_site_settings:
            self.set_site_specified_settings()

        settings.overrides['ITEM_PIPELINES'] = {}
        super(URL2ScreenshotSpider, self).__init__(*args, **kwargs)

    def set_site_specified_settings(self):
        """ Override some settings if they are site-specified """
        domain = _get_domain(self.product_url)
        if domain == 'hm.com':
            self.proxy = _get_random_proxy()
            self.proxy_type = 'http'
            self.code_200_required = False
            self._site_settings_activated_for = domain
            self.log('Site-specified settings activated for: %s' % domain)
        if domain == 'macys.com' or domain == 'www1.macys.com':
            self.code_200_required = False
            #self.proxy = _get_random_proxy()
            #self.proxy_type = 'http'
            settings.overrides['CRAWLERA_ENABLED'] = True
            self.make_screenshot = self.make_screenshot_for_macys
            self._site_settings_activated_for = domain
            self.log('Site-specified settings activated for: %s' % domain)
            self.check_bad_results_function = _check_bad_results_macys
        if domain == 'walmart.com':
            self.code_200_required = True
            self.proxy_auth = HTTPProxyAuth("4810848337264489a1d2f2230da5c981", "")
            self.proxy = "content.crawlera.com:8010/"
            self.proxy_type = 'http'
            settings.overrides['CRAWLERA_URL'] = 'http://content.crawlera.com:8010'
            settings.overrides['CRAWLERA_APIKEY'] = "4810848337264489a1d2f2230da5c981"
            settings.overrides['CRAWLERA_ENABLED'] = True
            self._site_settings_activated_for = domain
            self.log('Site-specified settings activated for: %s' % domain)

    def make_screenshot_for_macys(self, driver, output_fname):
        #time.sleep(7*60)  # delay for PhantomJS2 unpacking?
        rasterize_script = os.path.join(CWD, 'rasterize.js')
        phantomjs_binary = 'phantomjs' if not os.path.exists('/usr/sbin/phantomjs2') else '/usr/sbin/phantomjs2'
        # cmd = 'phantomjs --ssl-protocol=any {script} "{url}" {output_fname} {width}px*{height}px'.format(
        #     script=rasterize_script, url=self.product_url, output_fname=output_fname,
        #     width=self.width)#, height=self.height
        cmd = '{phantomjs_binary} --ssl-protocol=any {script} "{url}" {output_fname} {width}px'.format(
            script=rasterize_script, url=self.product_url, output_fname=output_fname,
            width=self.width, phantomjs_binary=phantomjs_binary)#, height=self.height
        self.log('Using %s' % phantomjs_binary)
        self.log(cmd)
        # extra debug data
        version_file = '/tmp/phantomjs_version.txt'
        if not os.path.exists(version_file):
            os.system('{phantomjs_binary} -v > {version_file} 2>&1'.format(
                phantomjs_binary=phantomjs_binary, version_file=version_file))
        if os.path.exists(version_file):
            self.log('PhantomJS real version: %s' % open(version_file, 'r').read())
        _start = datetime.datetime.now()
        os.system(cmd)
        self.log('Command finished in %s second(s)' % ((datetime.datetime.now() - _start).total_seconds()))
        assert os.path.exists(output_fname), 'Output file does not exist'
        if self.image_copy:  # save a copy of the file if needed
            shutil.copyfile(output_fname, self.image_copy)
        try:
            driver.quit()
        except:
            pass

    def start_requests(self):
        req = Request(self.product_url, dont_filter=True)
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

    def _get_js_body_height(self, driver):
        scroll = driver.execute_script('return document.body.scrollHeight;')
        window_outer = driver.execute_script('return window.outerHeight;')
        window_inner = driver.execute_script('return window.innerHeight;')
        height = scroll + window_outer - window_inner
        self.log("Detected JS page height: %s" % height, INFO)
        return height

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

    def _click_on_element_with_id(self, driver, _id):
        script = """
            var element = document.getElementById('%s');
            element.click();
        """ % _id
        try:
            driver.execute_script(script)
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

    def _init_phantomjs(self):
        from selenium import webdriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        self.log('No product links found at first attempt'
                 ' - trying PhantomJS with UA %s' % self.user_agent)
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self.user_agent
        service_args = []
        if self.proxy:
            service_args.append('--proxy="%s"' % self.proxy)
            service_args.append('--proxy-type=' + self.proxy_type)
            proxy_auth = getattr(self, '_proxy_auth', None)
            if proxy_auth:
                service_args.append("--proxy-auth=\"%s\":" % proxy_auth)

        #assert False, service_args
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        return driver

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

    def prepare_driver(self, driver):
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_script_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))

    def make_screenshot(self, driver, output_fname):
        driver.get(self.product_url)
        time.sleep(6)
        # maximize height of the window
        _body_height = self._get_js_body_height(driver)
        if _body_height and _body_height > 10:
            driver.set_window_size(self.width, _body_height)
        self._solve_captha_in_selenium(driver)

        if self.close_popups:
            time.sleep(3)
            self._click_on_element_with_xpath(driver, '//*[contains(@class, "monetate_lightbox_close_")]')  # for ralphlauren.com
            self._click_on_elements_with_class(driver, 'close')
            self._remove_element_with_xpath(
                driver, '//body/*[contains(@class, "email-lightbox")]')  # for levi.com
            self._click_on_element_with_id(driver, 'closeBtn')  # for macys
            self._click_on_element_with_id(driver, 'closeBtn')  # 2 times - first time doesn't work sometimes
            self._click_on_elements_with_class(driver, 'brdialog-close')  # for madewell.com
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "lightboximg")]//*[contains(@class, "closePopup")]')  # for madewell.com
            self._click_on_element_with_id(driver, 'skipSignup')  # for madewell.com
            self._click_on_element_with_xpath(driver, '//*[contains(@class, "padiPopupContent")]//*[contains(@class, "padiClose")]')  # for carters.com
            self._click_on_element_with_id(driver, 'oo_no_thanks')  # for levi.com
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "cookiebar")]//button')  # for HM.com
            self._remove_element_with_xpath(driver, '//*[contains(@id, "emailAcqPopupContainer")]')  # for http://bananarepublic.gap.com
            self._click_on_element_with_id(driver, 'welcomeMatStart')  # for jcrew.com

            self._click_on_element_with_xpath(
                driver, '//*[contains(@class, "featherlight-content")]//*[contains(@class, "featherlight-close")]')  # for agjeans.com
            time.sleep(2)
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "top")]//*[contains(@id, "closeButton")]')  # for agjeans.com
            self._click_on_element_with_xpath(driver, '/html/body/div[contains(@class, "ui-widget")]'
                                                      '/div[contains(@class, "ui-dialog-titlebar")]'
                                                      '/a/span[contains(@class, "ui-icon-closethick")]')  # for childrensplace.com
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "popup-subcription-closes-link")'
                                                      ' and contains(text(), "lose")]')  # for luckybrand.com
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "emOv-container")]//*[contains(@id, "emOv-signupClose")]')  # for uniqlo.com
            self._click_on_element_with_xpath(driver, '//*[contains(@id, "topbar")]/*[contains(@id, "close")]/a')  # for gap.com

        time.sleep(4)
        driver.save_screenshot(output_fname)
        if self.image_copy:  # save a copy of the file if needed
            driver.save_screenshot(self.image_copy)

        _check_bad_results_function = getattr(self, 'check_bad_results_function', None)
        if _check_bad_results_function is not None and callable(_check_bad_results_function):
            if _check_bad_results_function(driver):
                assert False, 'Bad results returned'

        if not DEBUG_MODE:
            driver.quit()

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

        if not DEBUG_MODE:
            display = Display(visible=int(bool(DEBUG_MODE)), size=(self.width, self.height))
            display.start()

        # we will use requesocks for checking response code
        r_session = requests.session()
        if self.timeout:
            self.timeout = int(self.timeout)
        r_session.timeout = self.timeout
        # Proxies activated again because of walmart bans
        if self.proxy:
            r_session.proxies = {'http': self.proxy_type+'://'+self.proxy,
                                'https': self.proxy_type+'://'+self.proxy}
            r_session.auth = self.proxy_auth

        if self.user_agent:
            r_session.headers = {'User-Agent': self.user_agent}

        # check if the page returns code != 200
        if self.code_200_required and str(self.code_200_required).lower() not in ('0', 'false', 'off'):
            page_code = r_session.get(self.product_url, verify=False).status_code
            if page_code != 200:
                self.log('Page returned code %s at %s' % (page_code, self.product_url), ERROR)
                yield ScreenshotItem()  # return empty item
                if not DEBUG_MODE:
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
            self.log('Screenshot was made for file %s' % t_file.name)
        except Exception as e:
            self.log('Exception while getting response using selenium! %s' % str(e))
            # lets try with another driver
            another_driver_name = self._choose_another_driver()
            try:
                if not DEBUG_MODE:
                    driver.quit()  # clean RAM
            except Exception as e:
                pass
            driver = self.init_driver(name=another_driver_name)
            self.prepare_driver(driver)
            self.make_screenshot(driver, t_file.name)
            self.log('Screenshot was made for file %s (2nd attempt)' % t_file.name)
            try:
                if not DEBUG_MODE:
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
            self.log('Screenshot was cropped and saved to %s' % t_file.name)
            if self.image_copy:  # save a copy of the file if needed
                area.save(self.image_copy, 'png')

        with open(t_file.name, 'rb') as fh:
            img_content = fh.read()
            self.log('Screenshot content was read, size: %s bytes' % len(img_content))

        if self.remove_img is True:
            os.unlink(t_file.name)  # remove old output file
            self.log('Screenshot file was removed: %s' % t_file.name)

        # yield the item
        item['url'] = response.url
        item['image'] = base64.b64encode(img_content)
        item['site_settings'] = getattr(self, '_site_settings_activated_for', None)

        if not DEBUG_MODE:
            display.stop()

        self.log('Item image key length: %s' % len(item.get('image', '')))

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
