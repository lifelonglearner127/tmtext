# -*- coding: utf-8 -*-
#!/usr/bin/python


import urllib, urllib2
import re
import sys
import json
from lxml import html
import requests
from extract_data import Scraper
import os
from PIL import Image
import cStringIO # *much* faster than StringIO
from pytesseract import image_to_string
from requests.auth import HTTPProxyAuth

sys.path.append(os.path.abspath('../search'))
import captcha_solver
import compare_images
from socket import timeout
import random
from spiders_shared_code.amazon_variants import AmazonVariants
import datetime
import functools

def handle_badstatusline(f):
    """https://github.com/mikem23/keepalive-race
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        for _ in range(2):
            try:
                return f(*args, **kwargs)
            except requests.exceptions.ConnectionError as e:
                if 'httplib.BadStatusLine' in e.message:
                    continue
                raise
        else:
            raise
    return wrapper

class AmazonScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http(s)://www.amazon.com/dp/<product-id> or http(s)://www.amazon.co.uk/dp/<product-id>"

    CB = captcha_solver.CaptchaBreakerWrapper()
    # special dir path to store the captchas, so that the service has permissions to create it on the scraper instances
    CB.CAPTCHAS_DIR = '/tmp/captchas'
    CB.SOLVED_CAPTCHAS_DIR = '/tmp/solved_captchas'

    MAX_PROXY_RETRIES = 3

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.av = AmazonVariants()
        self.is_review_checked = False
        self.review_list = None
        self.max_review = None
        self.min_review = None
        self.is_marketplace_sellers_checked = False
        self.marketplace_prices = None
        self.marketplace_sellers = None
        self.is_variants_checked = False
        self.variants = None
        self.no_image_available = 0

        self.proxy_host = self.CRAWLERA_HOST
        self.proxy_port = self.CRAWLERA_PORT
        self.proxy_auth = HTTPProxyAuth(self.CRAWLERA_APIKEY, "")
        self.proxies = {"http": "http://{}:{}/".format(self.proxy_host, self.proxy_port), \
                        "https": "https://{}:{}/".format(self.proxy_host, self.proxy_port)}

        self.proxies_enabled = False # first, they are OFF to save allowed requests

    @handle_badstatusline
    def _request(self, url, data=None, allow_redirects=True):
        #print 'REQUESTING %s WITH PROXIES %s' % (url, self.proxies_enabled)
        if self.proxies_enabled and 'amazon.com' in url:
            return requests.get(url, \
                    data=data, \
                    proxies=self.proxies, \
                    auth=self.proxy_auth, \
                    verify=False, \
                    timeout=300,
                    allow_redirects=allow_redirects)
        else:
            headers = {'User-Agent': self.select_browser_agents_randomly()}
            return requests.get(url, data=data, headers=headers, timeout=20)

    def _extract_page_tree(self, retry=0, proxy_retry=0, captcha_data=None):
        # request https instead of http
        if re.match('http://', self.product_page_url):
            self.product_page_url = 'https://' + re.match('http://(.+)', self.product_page_url).group(1)

        if not re.search('showDetailTechData=1', self.product_page_url):
            if '?' in self.product_page_url:
                self.product_page_url = self.product_page_url + '&showDetailTechData=1'
            else:
                self.product_page_url = self.product_page_url + '?showDetailTechData=1'

        self.is_timeout = False

        try:
            if captcha_data:
                data = urllib.urlencode(captcha_data)
                resp = self._request(self.product_page_url, data, \
                    allow_redirects=False)
            else:
                resp = self._request(self.product_page_url, allow_redirects=False)

            # 3xx are redirections.
            while str(resp.status_code).startswith('3'):
                print 'REDIRECTED {code}: {url}'.format(
                    code=resp.status_code,
                    url=resp.request.url
                )
                if 'location' not in resp.headers:
                    self.ERROR_RESPONSE['failure_type'] = \
                        '3xx location not found'
                    return

                url = resp.headers['location']
                resp = self._request(url, allow_redirects=False)

            if resp.status_code != 200:
                print 'Got response %s for %s with headers %s' % (resp.status_code, self.product_page_url, resp.headers)

                if resp.status_code == 429:
                    self.is_timeout = True
                    self.ERROR_RESPONSE['failure_type'] = '429'
                    return

                elif resp.status_code == 404:
                    self.is_timeout = True
                    self.ERROR_RESPONSE['failure_type'] = '404'
                    return

                self.is_timeout = True
                self.ERROR_RESPONSE['failure_type'] = resp.status_code

        except requests.exceptions.ProxyError, e:
            print 'Error extracting', self.product_page_url, type(e), e

            self.is_timeout = True
            self.ERROR_RESPONSE['failure_type'] = 'proxy'
            return

        except requests.exceptions.ConnectionError, e:
            print 'Error extracting', self.product_page_url, type(e), e

            if 'Max retries exceeded' in str(e):
                self.is_timeout = True
                self.ERROR_RESPONSE['failure_type'] = 'max_retries'
                return

            self.is_timeout = True
            self.ERROR_RESPONSE['failure_type'] = str(e)

        except Exception, e:
            print 'Error extracting', self.product_page_url, type(e), e

            self.is_timeout = True # set self.is_timeout so we will return an error response
            self.ERROR_RESPONSE['failure_type'] = str(e)

        if self.is_timeout:
            if retry >= self.MAX_RETRIES or proxy_retry >= self.MAX_PROXY_RETRIES:
                return
            else:
                if self.proxies_enabled:
                    return self._extract_page_tree(retry, proxy_retry+1)
                elif retry == self.MAX_RETRIES - 1:
                    self.proxies_enabled = True
                    return self._extract_page_tree(retry, proxy_retry+1)
                else:
                    return self._extract_page_tree(retry+1)

        try:
            # replace NULL characters
            contents = self._clean_null(resp.text)
            self.tree_html = html.fromstring(contents.decode("utf8"))
        except UnicodeError, e:
            # if string was not utf8, don't deocde it
            print "Warning creating html tree from page content: ", e.message

            # replace NULL characters
            contents = self._clean_null(resp.text)
            self.tree_html = html.fromstring(contents)

        # it's a captcha page
        if self.tree_html.xpath("//form[contains(@action,'Captcha')]"):
            print 'GOT CAPTCHA for', self.product_page_url
            if retry < self.MAX_RETRIES - 1:
                image = self.tree_html.xpath(".//img/@src")
                if image:
                    captcha_text = self.CB.solve_captcha(image[0])

                # value to use if there was an exception
                if not captcha_text:
                    captcha_text = ''

                return self._extract_page_tree(retry+1, proxy_retry, captcha_data={'field-keywords' : captcha_text})

            if retry == self.MAX_RETRIES - 1:
                # If we have tried the maximum number of retries, try once more with proxies
                self.proxies_enabled = True
                return self._extract_page_tree(retry, proxy_retry+1)

            # If we still get a CAPTCHA, return failure
            self.is_timeout = True # set self.is_timeout so we will return an error response
            self.ERROR_RESPONSE["failure_type"] = "CAPTCHA"

        # if we got it we can exit the loop and stop retrying
        return

    def check_url_format(self):
        m = re.match(r"^https?://www.amazon.com/([a-zA-Z0-9%\-\%\_]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]*)?$", self.product_page_url)
        n = re.match(r"^https?://www.amazon.co.uk/([a-zA-Z0-9%\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]*)?$", self.product_page_url)
        o = re.match(r"^https?://www.amazon.ca/([a-zA-Z0-9%\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]*)?$", self.product_page_url)
        l = re.match(r"^https?://www.amazon.co.uk/.*$", self.product_page_url)
        self.scraper_version = "com"

        if (not not n) or (not not l): self.scraper_version = "uk"
        if (not not o): self.scraper_version = "ca"

        return (not not m) or (not not n) or (not not l) or (not not o)

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        self.av.setupCH(self.tree_html, self.product_page_url)

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        if self.scraper_version == "uk":
            product_id = re.match("^https?://www.amazon.co.uk/([a-zA-Z0-9%\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\&\=]*)?", self.product_page_url).group(3)
        elif self.scraper_version == "ca":
            product_id = re.match("^https?://www.amazon.ca/([a-zA-Z0-9%\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\&\=]*)?", self.product_page_url).group(3)
        else:
            product_id = re.match("^https?://www.amazon.com/([a-zA-Z0-9%\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\&\=]*)?", self.product_page_url).group(3)
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return 'success'

    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        pn = self.tree_html.xpath('//h1[@id="title"]/span[@id="productTitle"]')
        if len(pn)>0:
            return self._clean_text(pn[0].text)
        pn = self.tree_html.xpath('//h1[@class="parseasinTitle " or @class="parseasinTitle"]/span[@id="btAsinTitle"]//text()')
        if len(pn)>0:
            return self._clean_text(" ".join(pn).strip())
        pn = self.tree_html.xpath('//h1[@id="aiv-content-title"]//text()')
        if len(pn)>0:
            return self._clean_text(pn[0])
        pn = self.tree_html.xpath('//div[@id="title_feature_div"]/h1//text()')
        if len(pn)>0:
            return self._clean_text(pn[0].strip())
        pn = self.tree_html.xpath('//div[@id="item_name"]/text()')
        return self._clean_text(pn[0].strip())

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
        #return None

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        try:
            model = self.tree_html.xpath("//tr[@class='item-model-number']/td[@class='value']//text()")[0].strip()
            return model
        except:
            pass

        try:
            model = self.tree_html.xpath("//span[@class='a-text-bold' and contains(text(), 'Item model number:')]/following-sibling::span/text()")[0].strip()
            return model
        except:
            pass

        return None

    def _upc(self):
        upc = re.search('UPC:</b> (\d+)', html.tostring(self.tree_html))
        if upc:
            return upc.group(1)

    # Amazon's version of UPC
    def _asin(self):
        asin_text = self.tree_html.xpath('//*[contains(text(),"ASIN:")]/..')
        if asin_text:
            if 'productASIN' not in asin_text[0].text_content():
                return re.search('ASIN:\s*(\S+)', asin_text[0].text_content()).group(1)

        asin_text = self.tree_html.xpath('//tr/th[contains(text(),"ASIN")]/..')
        if asin_text:
            if 'productASIN' not in asin_text[0].text_content():
                return re.search('ASIN\s*(\S+)', asin_text[0].text_content()).group(1)

        asin = re.search(r'/dp/([0-9a-zA-Z]+)/', self._url())
        if asin:
            asin = asin.group(1)
            return asin
        asin = re.search(r'/dp/([0-9a-zA-Z]+)$', self._url())
        if asin:
            asin = asin.group(1)
            return asin

    def _specs(self):
        specs = {}

        for r in self.tree_html.xpath('//table[@id="productDetails_techSpec_section_1"]/tr'):
            key = r.xpath('./th/text()')[0].strip()
            value = r.xpath('./td/text()')[0].strip()

            specs[key] = value

        if not specs:
            for r in self.tree_html.xpath('//div[@id="technicalProductFeatures"]/following-sibling::div/ul/li'):
                key = r.xpath('./b/text()')[0]
                value = r.text_content().split(': ')[-1]

                specs[key] = value

        if specs:
            return specs

    def _features(self):
        rows = self.tree_html.xpath("//div[@class='content pdClearfix'][1]//tbody//tr")
        if len(rows)==0:
            rows = self.tree_html.xpath("//div[@id='dv-center-features']//table//tr")
        if len(rows)==0:
            rows = self.tree_html.xpath("//table[@id='aloha-ppd-glance-table']//tr")
        # list of lists of cells (by rows)
        cells=[]
        for row in rows:
            r = row.xpath(".//*[not(self::script)]//text()")
            if len(r)>0 and len(r[0])>1 and r[0].find('Customer Review') < 0 \
               and r[0].find('function(') < 0 and  r[0].find('Delivery') < 0 \
               and r[0].find('Date ') < 0 and r[0].find('Best Seller') < 0 \
               and r[0].find('Manufacturer ref') < 0 and r[0].find('ASIN') < 0:
                cells.append(r)
#            cells = map(lambda row: row.xpath(".//*[not(self::script)]//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        # return dict with all features info
     #   return all_features_text

        if rows_text:
            return rows_text

        return None

    def _feature_count(self): # extract number of features from tree
        rows = self._features()

        if not rows:
            return 0

        return len(rows)

    def _model_meta(self):
        return None

    def _description(self):
        description = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]")
        if description:
            description = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]")[0]

            hidden = description.xpath('//*[@class="aok-hidden"]')
            more_button = description.xpath('//div[@id="fbExpanderMoreButtonSection"]')
            expander = description.xpath(".//*[contains(@class, 'a-expander-extend-header')]")

            # remove expander(=show mores) from description
            if expander:
                expander[0].getparent().remove(expander[0])

            description = html.tostring(description)

            for exclude in hidden + more_button:
                description = re.sub(html.tostring(exclude), '', description)

            return self._clean_text(self._exclude_javascript_from_description(description))

        short_description = " " . join(self.tree_html.xpath("//div[@class='dv-simple-synopsis dv-extender']//text()")).strip()

        if short_description is not None and len(short_description)>0:
            return self._exclude_javascript_from_description(short_description.replace("\n"," "))

        return self._long_description_helper()

    def _bullet_feature_1(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 0:
            return self._clean_text(bullets[0].text_content())

    def _bullet_feature_2(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 1:
            return self._clean_text(bullets[1].text_content())

    def _bullet_feature_3(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 2:
            return self._clean_text(bullets[2].text_content())

    def _bullet_feature_4(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 3:
            return self._clean_text(bullets[3].text_content())

    def _bullet_feature_5(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 4:
            return self._clean_text(bullets[4].text_content())

    def _bullet_feature_6(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 5:
            return self._clean_text(bullets[5].text_content())


    def _bullet_feature_7(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 6:
            return self._clean_text(bullets[6].text_content())


    def _bullet_feature_8(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 7:
            return self._clean_text(bullets[7].text_content())


    def _bullet_feature_9(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 8:
            return self._clean_text(bullets[8].text_content())


    def _bullet_feature_10(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 9:
            return self._clean_text(bullets[9].text_content())


    def _bullet_feature_11(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 10:
            return self._clean_text(bullets[10].text_content())


    def _bullet_feature_12(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 11:
            return self._clean_text(bullets[11].text_content())


    def _bullet_feature_13(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 12:
            return self._clean_text(bullets[12].text_content())


    def _bullet_feature_14(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 13:
            return self._clean_text(bullets[13].text_content())


    def _bullet_feature_15(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 14:
            return self._clean_text(bullets[14].text_content())


    def _bullet_feature_16(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 15:
            return self._clean_text(bullets[15].text_content())


    def _bullet_feature_17(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 16:
            return self._clean_text(bullets[16].text_content())


    def _bullet_feature_18(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 17:
            return self._clean_text(bullets[17].text_content())


    def _bullet_feature_19(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 18:
            return self._clean_text(bullets[18].text_content())

    def _bullet_feature_20(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]")
        if bullets and len(bullets) > 19:
            return self._clean_text(bullets[19].text_content())

    def _bullets(self):
        bullets = self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//ul/li[not(contains(@class,'hidden'))]//text()")
        bullets = [self._clean_text(r) for r in bullets if len(self._clean_text(r))>0]
        if len(bullets) > 0:
            return "\n".join(bullets)
        return None

    def _seller_ranking(self):
        seller_ranking = []

        if self.tree_html.xpath("//li[@id='SalesRank']"):
            ranking_info = self.tree_html.xpath("//li[@id='SalesRank']/text()")[1].strip()

            if ranking_info:
                seller_ranking.append({"category": ranking_info[ranking_info.find(" in ") + 4:ranking_info.find("(")].strip(),
                                       "ranking": int(ranking_info[1:ranking_info.find(" ")].strip().replace(",", ""))})

            ranking_info_list = [item.text_content().strip() for item in self.tree_html.xpath("//li[@id='SalesRank']/ul[@class='zg_hrsr']/li")]

            for ranking_info in ranking_info_list:
                seller_ranking.append({"category": ranking_info[ranking_info.find("in") + 2:].strip(),
                                       "ranking": int(ranking_info[1:ranking_info.find(" ")].replace(",", "").strip())})
        else:
            ranking_info_list = self.tree_html.xpath("//td[preceding-sibling::th/@class='a-color-secondary a-size-base prodDetSectionEntry' and contains(preceding-sibling::th/text(), 'Best Sellers Rank')]/span/span")
            ranking_info_list = [ranking_info.text_content().strip() for ranking_info in ranking_info_list]

            for ranking_info in ranking_info_list:
                seller_ranking.append({"category": ranking_info[ranking_info.find("in") + 2:ranking_info.find("(See Top ")].strip(),
                                       "ranking": int(ranking_info[1:ranking_info.find(" ")].replace(",", "").strip())})

        if seller_ranking:
            return seller_ranking

        return None

    def _long_description(self):
        d1 = self._description()
        d2 = self._long_description_helper()
        if d1 == d2:
            return None
        return d2

    def _exclude_images_from_description(self, block):
        all_items_list = block.xpath(".//*")
        remove_candidates = []

        for item in all_items_list:
            if item.tag == "img":
                remove_candidates.append(item)

            if item.xpath("./@style") and ('border-top' in item.xpath("./@style")[0] or 'border-bottom' in item.xpath("./@style")[0]):
                remove_candidates.append(item)

        for item in remove_candidates:
            item.getparent().remove(item)

    def _long_description_helper(self):
        try:
            description = ""
            block = self.tree_html.xpath('//*[@class="productDescriptionWrapper"]')[0]

            for item in block:
                description = description + html.tostring(item)

            description = self._clean_text(self._exclude_javascript_from_description(description))

            if description is not None and len(description) > 5:
                return description
        except:
            pass

        try:
            description = ""
            block = self.tree_html.xpath('//div[@id="psPlaceHolder"]/preceding-sibling::noscript')[0]

            for item in block:
                description = description + html.tostring(item)

            description = self._clean_text(self._exclude_javascript_from_description(description))

            if description is not None and len(description) > 5:
                return description
        except:
            pass

        try:
            description = ""
            children = self.tree_html.xpath("//div[@id='productDescription']/child::*[not(@class='disclaim') and not(name()='script') and not(name()='style')]")
            skip_manufacturer_flag = False

            for child in children:
                if skip_manufacturer_flag:
                    skip_manufacturer_flag = False
                    continue

                self._exclude_images_from_description(child)

                if 'Product Description' in html.tostring(child):
                    continue

                if child.tag == "h3" and child.text.lower().strip() == 'from the manufacturer':
                    skip_manufacturer_flag = True
                    continue

                description += self._clean_text(self._exclude_javascript_from_description(html.tostring(child)))

            if description is not None and len(description) > 5:
                return description
        except:
            pass

        try:
            description = ""
            block = self.tree_html.xpath("//h2[contains(text(),'Product Description')]/following-sibling::*")[0]

            all_items_list = block.xpath(".//*")
            remove_candidates = []

            for item in all_items_list:
                if item.tag == "img":
                    remove_candidates.append(item)

                if item.xpath("./@style") and ('border-top' in item.xpath("./@style")[0] or 'border-bottom' in item.xpath("./@style")[0]):
                    remove_candidates.append(item)

            for item in remove_candidates:
                item.getparent().remove(item)

            for item in block:
                description = description + html.tostring(item)

            description = self._clean_text(self._exclude_javascript_from_description(description))

            if description is not None and len(description) > 5:
                return description
        except:
            pass

        try:
            description = '\n'.join(self.tree_html.xpath('//script//text()'))
            description = re.findall(r'var iframeContent = "(.*)";', description)
            description = urllib.unquote_plus(str(description))
            description = html.fromstring(description)
            description = description.xpath('//div[@class="productDescriptionWrapper"]')
            res = ""
            for d in description:
                if len(d.xpath('.//div[@class="aplus"]'))==0:
                    res += self._clean_text(' '.join(d.xpath('.//text()')))+" "
            if res != "":
                return res
        except:
            pass

        return None

    def _apluscontent_desc(self):
        res = self._clean_text(' '.join(self.tree_html.xpath('//div[@id="aplusProductDescription"]//text()')))
        if res != "" : return res
        desc = '\n'.join(self.tree_html.xpath('//script//text()'))
        desc = re.findall(r'var iframeContent = "(.*)";', desc)
        desc = urllib.unquote_plus(str(desc))
        desc = html.fromstring(desc)
        res = self._clean_text(' '.join(desc.xpath('//div[@id="aplusProductDescription"]//text()')))
        if res != "" : return res
        res = self._clean_text(' '.join(desc.xpath('//div[@class="productDescriptionWrapper"]/div[@class="aplus"]//text()')))
        if res != "" : return res
        return None

    def _get_variant_images(self):
        result = []
        for img in self.tree_html.xpath('//*[contains(@id, "altImages")]'
                                        '//img[contains(@src, "/")]/@src'):
            result.append(re.sub(r'\._[A-Z\d,_]{1,50}_\.jpg', '.jpg', img))
        return result

    def _variants(self):
        if self.is_variants_checked:
            return self.variants

        self.is_variants_checked = True

        self.variants = self.av._variants()

        if self.variants:
            # find default ("selected") variant and insert its images
            for variant in self.variants:
                if variant.get('selected', None):
                    variant['associated_images'] = self._get_variant_images()

        return self.variants

    def _swatches(self):
        return self.av._swatches()

    def _ingredients(self):
        page_raw_text = html.tostring(self.tree_html)

        try:
            ingredients = re.search('<b>Ingredients</b><br>(.+?)<br>', page_raw_text).group(1)
            r = re.compile(r'(?:[^,(]|\([^)]*\))+')
            ingredients = r.findall(ingredients)
            ingredients = [ingredient.strip() for ingredient in ingredients]

            if ingredients:
                return ingredients
        except:
            pass

        try:
            desc = '\n'.join(self.tree_html.xpath('//script//text()'))
            desc = re.findall(r'var iframeContent = "(.*)";', desc)
            desc = urllib.unquote_plus(str(desc))
            ingredients = re.search('Ingredients:(.+?)(\\n|\.)', desc).group(1)

            if "</h5>" in ingredients:
                return None

            r = re.compile(r'(?:[^,(]|\([^)]*\))+')
            ingredients = r.findall(ingredients)

            ingredients = [ingredient.strip() for ingredient in ingredients]

            if ingredients:
                return ingredients
        except:
            pass

        try:
            start_index = page_raw_text.find('<span class="a-text-bold">Ingredients</span>')

            if start_index < 0:
                raise Exception("Ingredients doesn't exist!")

            start_index = page_raw_text.find('<p>', start_index)
            end_index = page_raw_text.find('</p>', start_index)
            ingredients = page_raw_text[start_index + 3:end_index]
            r = re.compile(r'(?:[^,(]|\([^)]*\))+')
            ingredients = r.findall(ingredients)
            ingredients = [ingredient.strip() for ingredient in ingredients]

            if ingredients:
                return ingredients
        except:
            pass

        return None

    def _ingredient_count(self):
        if self._ingredients():
            return len(self._ingredients())

        return 0

    def _nutrition_facts(self):
        page_raw_text = html.tostring(self.tree_html)
        page_raw_text = urllib.unquote_plus(page_raw_text)

        try:
            start_index = page_raw_text.find('<h5>Nutritional Facts and Ingredients:</h5>')

            if start_index < 0:
                raise Exception("Nutritional info doesn't exist!")

            start_index = page_raw_text.find('<p>', start_index)
            end_index = page_raw_text.find('</p>', start_index)

            nutrition_facts = page_raw_text[start_index + 3:end_index]
            r = re.compile(r'(?:[^,(]|\([^)]*\))+')
            nutrition_facts = r.findall(nutrition_facts)

            nutrition_facts = [nutrition_fact.strip() for nutrition_fact in nutrition_facts]

            if nutrition_facts:
                return nutrition_facts
        except:
            pass

        return None

    def _nutrition_fact_count(self):
        if self._nutrition_facts():
            return len(self._nutrition_facts())

        return 0

    def _no_longer_available(self):
        availability = self.tree_html.xpath('//*[@id="availability" or @id="pantry-availability"]')

        if availability:
            if re.search('Currently [uU]navailable', availability[0].text_content()):
                return 1

        return 0

    def _important_information_helper(self, name):
        important_information = self.tree_html.xpath('//div[@id="importantInformation"]/div/div')

        if important_information:
            important_information = html.tostring( self.tree_html.xpath('//div[@id="importantInformation"]/div/div')[0])

            tags = ['<b>', '<h5>']
            tail_tags = ['</b>', '</h5>']
            idx = 0
            for t in tags:
                name_index = important_information.find(t + name)

                if name_index == -1:
                    idx += 1
                    continue

                start_index = important_information.find(tail_tags[idx], name_index) + len(tail_tags[idx])

                # end at the next bold element
                end_index = important_information.find(t, start_index + 1)

                return important_information[start_index : end_index]

    def _amazon_ingredients(self):
        return self._important_information_helper('Ingredients')

    def _usage(self):
        return self._important_information_helper('Usage')

    def _directions(self):
        return self._important_information_helper('Directions')

    def _warnings(self):
        return self._important_information_helper('Safety')

    def _indications(self):
        return self._important_information_helper('Indications')

    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #extract meta tags exclude http-equiv
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        if re.match("https?://www.amazon.com", canonical_link):
            return canonical_link
        else:
            return "http://www.amazon.com" + canonical_link

    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        url = self.product_page_url
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        pc_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        img_list = []
        for h in [mobile_headers, pc_headers]:
            contents = requests.get(url, headers=h).text
            tree = html.fromstring(contents)
            image_url = self._image_urls(tree)
            img_list.extend(image_url)
        if len(img_list) == 2:
            return img_list[0] == img_list[1]
        return None

    def _get_origin_image_urls_from_thumbnail_urls(self, thumbnail_urls):
        origin_image_urls = []

        for url in thumbnail_urls:
            if url == u'http://ecx.images-amazon.com/images/I/31138xDam%2BL.jpg':
                continue

            if "PKmb-play-button-overlay-thumb_.png" in url:
                continue

            image_file_name = url.split("/")[-1]
            offset_index_1 = image_file_name.find(".")
            offset_index_2 = image_file_name.rfind(".")

            if offset_index_1 == offset_index_2:
                if not url in origin_image_urls:
                    origin_image_urls.append(url)
            else:
                image_file_name = image_file_name[:offset_index_1] + image_file_name[offset_index_2:]
                url = url[:url.rfind("/")] + "/" + image_file_name
                if not url in origin_image_urls:
                    origin_image_urls.append(url)

        if not origin_image_urls:
            return None

        return origin_image_urls

    def _swatch_image_helper(self, image, swatch_images):
        if image.get('hiRes') and image['hiRes'].strip():
            image = image['hiRes']
        elif image.get('large') and image['large'].strip():
            image = image['large']

        image_size = re.search('_SL(\d+)_', image)
        if image_size:
            image_size = int(image_size.group(1))

        duplicate = False

        for i in range(len(swatch_images)):
            swatch_image = swatch_images[i]

            swatch_image_size = re.search('_SL(\d+)_', swatch_image)
            if swatch_image_size:
                swatch_image_size = int(swatch_image_size.group(1))

            if image.split('._')[0] in swatch_image:
                duplicate = True

                if image_size and swatch_image_size:
                    if image_size > swatch_image_size:
                        swatch_images[i] = image

                elif image_size:
                    swatch_images[i] = image

        if not duplicate:
            swatch_images.append(image)

        return swatch_images

    def _image_urls(self, tree = None):
        allimg = self._image_helper()
        n = len(allimg)
        vurls = self._video_urls()
        if vurls==None: vurls=[]
        if tree == None:
            tree = self.tree_html

        try:
            swatch_images = []

            swatch_image_json = json.loads(self._find_between(html.tostring(self.tree_html), 'data["colorImages"] = ', ';\n'))

            if swatch_image_json:
                try:
                    selected_color = self.tree_html.xpath('//span[@class="selection"]/text()')[0].strip()
                except:
                    try:
                        selected_variations = json.loads( re.search('selected_variations":({.*?})', html.tostring(self.tree_html)).group(1))
                        selected_color = ' '.join(reversed(selected_variations.values()))
                    except:
                        selected_color = None

                for color in swatch_image_json:
                    if color == selected_color:
                        for image in swatch_image_json[color]:
                            swatch_images = self._swatch_image_helper(image, swatch_images)

            else:
                # e.g. https://www.amazon.com/Clorox-Bleach-Stain-Remover-Colors/dp/B01CZKEGMA
                swatch_image_json = re.search("'colorImages': { 'initial': ([^\n]*)},", html.tostring(self.tree_html))
                swatch_image_json = json.loads(swatch_image_json.group(1))

                for image in swatch_image_json:
                    swatch_images = self._swatch_image_helper(image, swatch_images)

            if swatch_images:
                return self._remove_no_image_available(swatch_images)

        except:
            pass

        moca_images = self.tree_html.xpath("//div[contains(@class,'verticalMocaThumb')]/span/img/@src")
        if moca_images:
            return self._remove_no_image_available(self._get_origin_image_urls_from_thumbnail_urls(moca_images))

        image_url = []

        #The small images are to the left of the big image
        image_url.extend(tree.xpath("//span[@class='a-button-text']//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls([m for m in image_url if m.find("player")<0 and m.find("video")<0 and m.find("play-button")<0 and m not in vurls])

        #The small images are below the big image
        image_url.extend(tree.xpath("//div[@id='thumbs-image']//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            res = [m for m in image_url if m.find("player")<0 and m.find("video")<0 and m.find("play-button")<0 and m not in vurls]
            return self._get_origin_image_urls_from_thumbnail_urls(res)

        #Amazon instant video
        image_url.extend(tree.xpath("//div[@class='dp-meta-icon-container']//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls(image_url)

        image_url.extend(tree.xpath("//td[@id='prodImageCell']//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls(image_url)

        image_url.extend(tree.xpath("//div[contains(@id,'thumb-container')]//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls([m for m in image_url if m.find("player")<0 and m.find("video")<0 and m.find("play-button")<0 and m not in vurls])

        image_url.extend(tree.xpath("//div[contains(@class,'imageThumb')]//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls(image_url)

        image_url.extend(tree.xpath("//div[contains(@id,'coverArt')]//img/@src"))
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return self._get_origin_image_urls_from_thumbnail_urls(image_url)

        image_url =tree.xpath('//img[@id="imgBlkFront"]')
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return ["inline image"]

        if len(allimg) > 0 and self.no_image(allimg) == 0:
            if len(allimg) >= 7:
                allimg = allimg[:7]

                if vurls:
                    allimg = allimg[:-1]

            return self._get_origin_image_urls_from_thumbnail_urls(allimg)
        return None

    def _image_helper(self):
        res = []
        try:
            all_scripts = self.tree_html.xpath('//script[@type="text/javascript"]//text()')
            for s in all_scripts:
                st = s.find('data["colorImages"]')
                if st > 0:
                    colors = self.tree_html.xpath('//div[@id="variation_color_name"]//span[@class="selection"]//text()')
                    pack = self.tree_html.xpath('//div[@id="variation_item_package_quantity"]//span[@class="selection"]//text()')
                    style = self.tree_html.xpath('//div[@id="variation_style_name"]//span[@class="selection"]//text()')
                    color=""
                    if len(colors)>0:
                        color=colors[0].strip()
                    if len(pack)>0:
                        color=pack[0].strip() + " " + color
                    if  len(style)>0:
                        color=style[0].strip()
                    st = s.find("{",st)
                    e = s.find(";",st)
                    if st>=e: continue
                    imdata=json.loads(s[st:e])

                    if type(imdata) is dict and len(imdata)>0:
                        if color=="" or not imdata.has_key(color):
                            color =imdata.keys()[0]
                        for t in imdata[color]:
                            res.append(t['large'])
                        return res
                st = s.find("'colorImages':")
                if len(res)==0 and st > 0:
                    while s[st]!="{" and st>0:
                        st -= 1
                    e = s.find("};",st)+1
                    if st>=e: continue
                    imdata=json.loads(s[st:e].replace("'",'"'))
                    if type(imdata) is dict and len(imdata)>0  and imdata.has_key('colorImages')\
                     and imdata['colorImages'].has_key('initial'):
                        for d in imdata['colorImages']['initial']:
                            imu = d.get("large","")
                            if len(imu)>10:
                                res.append(imu)
                        return res
                st = s.find("var colorImages")
                if len(res)==0 and st > 0:
                    st = s.find("{",st)
                    e = s.find("};",st)+1
                    if st>=e: continue
                    imdata=json.loads(s[st:e].replace("'",'"'))
                    if type(imdata) is dict and len(imdata)>0  and imdata.has_key('initial'):
                        for d in imdata['initial']:
                            imu = d.get("large","")
                            if len(imu)>10:
                                res.append(imu)
                        return res
        except:
            return []
        return res

    def _mobile_image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
        return image_url

    def _image_count(self):
        iu = self._image_urls()
        if iu ==None:
            return 0
        return len(iu)

    def _remove_no_image_available(self, image_urls):
        filtered_image_urls = []

        for image in image_urls:
            if 'no-img' in image:
                self.no_image_available = 1
            else:
                filtered_image_urls.append(image)

        if filtered_image_urls:
            return filtered_image_urls

    def _no_image_available(self):
        self._image_urls()
        return self.no_image_available

    # return 1 if the "no image" image is found
    def no_image(self,image_url):
        try:
            if len(image_url)>0 and image_url[0].find("no-img")>0:
                return 1
            if self._no_image(image_url[0]):
                return 1
        except Exception, e:
            print "image_urls WARNING: ", e.message
        return 0

    def _video_urls(self):
        video_url = self.tree_html.xpath('//script')  #[@type="text/javascript"]
        temp = []
        for v in video_url:
            st=str(v.xpath('.//text()'))
            r = re.findall("[\'\"]url[\'\"]:[\'\"](http://.+?\.mp4)[\'\"]", st)
            if r:
                temp.extend(r)
            ii=st.find("kib-thumb-container-")
            if ii > 0:
                ij=st.find('"',ii+19)
                if ij-ii<25:
                    vid = st[ii:ij]
                    viurl = self.tree_html.xpath('//div[@id="%s"]//img/@src' % vid)
                    if len(viurl)>0:
                        temp.append(viurl[0])

        #Find video among the  small images.
        image_url = self.tree_html.xpath("//span[@class='a-button-text']//img/@src")
        if len(image_url)==0:
            image_url = self.tree_html.xpath("//div[@id='thumbs-image']//img/@src")
        for v in image_url:
            if v.find("player")>0 and not re.search('\.png$', v):
                temp.append(v)

        video_urls = re.findall('"url":"([^"]+.mp4)"', html.tostring(self.tree_html))
        for video in video_urls:
            if not video in temp:
                temp.append(video)

        if len(temp)==0: return None
        return temp#",".join(temp)

    def _video_count(self):
        if self._video_urls()==None:
            return len(self.tree_html.xpath('//*[@id="cr-video-swf-url"]'))
        return len(self._video_urls())#.split(','))

    # return one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls:
            return len(urls)
        return None

    def _webcollage(self):
        return None

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    def _related_product_urls(self):
        variants = self._variants() or []
        related_product_url_list = []

        for variant in variants:
            if variant["url"] and variant["url"] != self.product_page_url.split('?')[0]:
                related_product_url_list.append(variant["url"])

        if related_product_url_list:
            return related_product_url_list

        return None

    def _best_seller_category(self):
        try:
            return re.search('#[\d,]+ in ([^\(]+) \(', html.tostring(self.tree_html)).group(1)
        except:
            return re.search('#[\d,]+ in ([^<]+)</span>', html.tostring(self.tree_html)).group(1)

    ##########################################
    ################ CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        average_review = self.tree_html.xpath("//span[@id='acrPopover']/@title")
        if len(average_review) == 0:
            average_review = self.tree_html.xpath("//div[@class='gry txtnormal acrRating']//text()")
        if len(average_review) == 0:
            average_review = self.tree_html.xpath("//div[@id='avgRating']//span//text()")
        average_review = re.findall("([0-9]\.?[0-9]?) out of 5 stars", average_review[0])[0]
        return self._tofloat(average_review)

    def _review_count(self):
        if not self.is_review_checked:
            self._reviews()
        if self.review_list and len(self.review_list) == 5:
            sumup = 0
            for i,v in self.review_list:
                sumup +=int(v)
            return sumup

        nr_reviews = self.tree_html.xpath("//span[@id='acrCustomerReviewText']//text()")
        if len(nr_reviews) > 0:
            nr_review = re.findall("([0-9,]+) customer reviews", nr_reviews[0])
            if len(nr_review) == 0:
                nr_review = re.findall("([0-9]+) customer review", nr_reviews[0])
            if len(nr_review) > 0:
                return self._toint(nr_review[0])
        nr_reviews = self.tree_html.xpath("//div[@class='fl gl5 mt3 txtnormal acrCount']//text()")
        if len(nr_reviews) > 1:
            return self._toint(nr_reviews[1])
        nr_reviews = self.tree_html.xpath("//a[@class='a-link-normal a-text-normal product-reviews-link']//text()")
        if len(nr_reviews) > 1:
            return self._toint(nr_reviews[0].replace('(','').replace(')','').replace(',',''))
        if self.scraper_version == "uk":
            nr_reviews = self.tree_html.xpath("//span[@class='crAvgStars']/a//text()")
            if len(nr_reviews) > 0:
                res = nr_reviews[0].split()
                return self._toint(res[0])
        return 0

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        if not self._review_count() or self._review_count() == 0:
            self.review_list = None
            return self.review_list

        review_list = []

        try:
            review_summary_link = self.tree_html.xpath("//a[@class='a-link-emphasis a-nowrap']/@href")[0]
        except:
            review_summary_link = "http://www.amazon.com/product-reviews/{0}/ref=acr_dpx_see_all?ie=UTF8&showViewpoints=1".format(self._product_id())

        mark_list = ["one", "two", "three", "four", "five"]

        for index, mark in enumerate(mark_list):
            if "cm_cr_dp_see_all_summary" in review_summary_link:
                review_link = review_summary_link.replace("cm_cr_dp_see_all_summary", "cm_cr_pr_viewopt_sr")
                review_link = review_link + "&filterByStar={0}_star&pageNumber=1".format(mark)
            elif "acr_dpx_see_all" in review_summary_link:
                review_link = review_summary_link.replace("acr_dpx_see_all", "cm_cr_pr_viewopt_sr")
                review_link = review_link + "&filterByStar={0}_star&pageNumber=1".format(mark)
            review_link = review_link.replace("reviewerType=avp_only_reviews", "reviewerType=all_reviews")
            for retry_index in range(3):
                try:
                    resp = self._request(review_link)
                    if str(resp.status_code).startswith('4'):
                        break
                    contents = resp.text

                    if "Sorry, no reviews match your current selections." in contents:
                        review_list.append([index + 1, 0])
                    else:
                        if not self.max_review or self.max_review < index + 1:
                            self.max_review = index + 1

                        if not self.min_review or self.min_review > index + 1:
                            self.min_review = index + 1

                        review_html = html.fromstring(contents)
                        review_count = review_html.xpath("//div[@id='cm_cr-review_list']//div[contains(@class, 'a-section a-spacing-medium')]//span[@class='a-size-base']/text()")[0]
                        review_count = int(re.search('of (.*) reviews', review_count).group(1).replace(",", ""))
                        review_list.append([index + 1, review_count])

                    break

                except Exception, e:
                    print e
                    continue

        if not review_list:
            self.review_list = None
            return self.review_list

        self.review_list = review_list

        return self.review_list

    def _tofloat(self,s):
        try:
            s = s.replace(",", "")
            s = re.findall(r"[\d\.]+", s)[0]
            t=float(s)
            return t
        except ValueError:
            return 0.0

    def _toint(self,s):
        try:
            s = s.replace(',','')
            t=int(s)
            return t
        except ValueError:
            return 0

    def _max_review(self):
        self._reviews()

        return self.max_review

    def _min_review(self):
        self._reviews()

        return self.min_review

    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################
    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        price = self._price()

        if price[0] == u'£':
            return "GDP"

        if price[0] == u'$':
            return "USD"

        return price[0]

    # extract product price from its product product page tree
    def _price(self):
        currency = u"$"
        price = None

        if self.scraper_version == "uk":
            currency = u"£"

        try:
            price = self._clean_text(self.tree_html.xpath("//b[@class='priceLarge']")[0].text_content())
            price = price.replace(currency, u"").strip()
        except:
            price = None

        if not price:
            try:
                price = self._clean_text(self.tree_html.xpath("//span[@id='priceblock_ourprice']")[0].text_content())
                price = price.replace(currency, u"").strip()
            except:
                price = None

        if not price:
            try:
                price = self._clean_text(self.tree_html.xpath("//span[@id='priceblock_dealprice']")[0].text_content())
                price = price.replace(currency, u"").strip()
            except:
                price = None

        if not price:
            try:
                price = self._clean_text(self.tree_html.xpath("//span[@id='priceblock_saleprice']")[0].text_content())
                price = price.replace(currency, u"").strip()
            except:
                price = None

        if "-" in price:
            if currency not in price:
                price = currency + price.split("-")[0].strip() + u"-" + currency + price.split("-")[1].strip()
            else:
                price = price.split("-")[0].strip() + u"-" + price.split("-")[1].strip()
        else:
            if currency not in price:
                price = currency + price

        if not price:
            return None

        return price

    def _in_stores(self):
        return 0

    def _marketplace(self):
        aa = self.tree_html.xpath("//div[@class='buying' or @id='merchant-info']")
        for a in aa:
            if a.text_content().find('old by ')>0 and a.text_content().find('old by Amazon')<0:
                return 1
            if a.text_content().find('seller')>0 :
                return 1
        a = self.tree_html.xpath('//div[@id="availability"]//a//text()')
        if len(a)>0 and a[0].find('seller')>=0: return 1

        marketplace_sellers = self._marketplace_sellers()

        if marketplace_sellers:
            return 1

        if self.tree_html.xpath("//div[@id='toggleBuyBox']//span[@class='a-button-text' and text()='Shop This Website']"):
            return 1

        s = self._seller_from_tree()
        return s['marketplace']

    def img_parse(self, img_url):
        file = urllib.urlopen(img_url)
        im = cStringIO.StringIO(file.read()) # constructs a StringIO holding the image
        img = Image.open(im)
        txt = image_to_string(img)
        return txt


    def _marketplace_sellers(self):
        if self.is_marketplace_sellers_checked:
            return self.marketplace_sellers

        self.is_marketplace_sellers_checked = True

        mps = []
        mpp = []
        path = '/tmp/amazon_sellers.json'

        try:
            with open(path, 'r') as fp:
                amsel = json.load(fp)
        except:
            amsel = {}

        domain=self.product_page_url.split("/")

        try:
            url = domain[0] + "//" + domain[2] + "/gp/offer-listing/" + self.tree_html.xpath("//input[@id='ASIN']/@value")[0] + "/ref=olp_tab_all"
        except:
            url = domain[0] + "//" + domain[2] + "/gp/offer-listing/" + self._product_id() + "/ref=olp_tab_all"
        fl = 0

        while len(url) > 10:
            contents = self._request(url).text
            tree = html.fromstring(contents)
            sells = tree.xpath('//div[@class="a-row a-spacing-mini olpOffer"]')

            for s in sells:
                price = s.xpath('.//span[contains(@class,"olpOfferPrice")]//text()')
                sname = s.xpath('.//*[contains(@class,"olpSellerName")]/span/a/text()')

                if len(price) > 0:
                    seller_price = self._tofloat(price[0])
                    seller_name = ""

                    if len(sname) > 0 and sname[0].strip() != "":
                        seller_name = sname[0].strip()
                    else:
                        seller_link = s.xpath(".//p[@class='a-spacing-small']/a/@href")

                        if len(seller_link) > 0:
                            sd=seller_link[0].split("/")
                            seller_id = ""

                            if len(sd) > 4:
                                seller_id = sd[4]
#                                print "seller_id",seller_id

                                if seller_id != "" and seller_id in amsel:
                                    seller_name = amsel[seller_id]
#                                    print "seller_name",seller_name

                            if seller_name == "":
                                if seller_link[0].startswith("http://www.amazon."):
                                    seller_content = self._request(seller_link[0]).text
                                else:
                                    if self.scraper_version == "uk":
                                        seller_content = self._request("http://www.amazon.co.uk" + seller_link[0]).text
                                    elif self.scraper_version == "ca":
                                        seller_content = self._request("http://www.amazon.ca" + seller_link[0]).text
                                    else:
                                        seller_content = self._request("http://www.amazon.com" + seller_link[0]).text

                                seller_tree = html.fromstring(seller_content)
                                seller_names = seller_tree.xpath("//h2[@id='s-result-count']/span/span//text()")

                                if len(seller_names) > 0:
                                    seller_name = seller_names[0].strip()
                                else:
                                    seller_names = seller_tree.xpath("//title//text()")

                                    if len(seller_names) > 0:
                                        if seller_names[0].find(":")>0:
                                            seller_name = seller_names[0].split(":")[1].strip()
                                        else:
                                            seller_name = seller_names[0].split("@")[0].strip()

                            if seller_name != "" and seller_id != "":
                                amsel[seller_id] = seller_name
                                fl = 1

                    if seller_name != "":
                        mps.append(seller_name)
                        mpp.append(seller_price)

                        if len(mps) > 20:
                            break

            if len(mps) > 20:
                break

            urls = tree.xpath(".//ul[contains(@class,'a-pagination')]//li[contains(@class,'a-last')]//a/@href")

            if len(urls)>0:
                url = domain[0]+"//"+domain[2]+urls[0]
            else:
                url = ""

        if len(mps)>0:
            if fl == 1:
                try:
                    with open(path, 'w') as fp:
                        json.dump(amsel, fp)
                except Exception as ex:
                    print ex

            self.marketplace_prices = mpp
            self.marketplace_sellers = mps

            return mps

        return None

    def _marketplace_prices(self):
        self._marketplace_sellers()

        return self.marketplace_prices

    def _marketplace_lowest_price(self):
        self._marketplace_sellers()

        return min(self.marketplace_prices) if self.marketplace_prices else None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
        return None

    # extract product seller information from its product product page tree (using h2 visible tags)
    def _seller_from_tree(self):
        seller_info = {}
        h5_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h5//text()[normalize-space()!='']"))
        acheckboxlabel = map(lambda text: self._clean_text(text), self.tree_html.xpath("//span[@class='a-checkbox-label']//text()[normalize-space()!='']"))
        seller_info['owned'] = 1 if "FREE Two-Day" in acheckboxlabel else 0

        a = self.tree_html.xpath('//div[@id="soldByThirdParty"]')
        a = not not a#turn it into a boolean
        seller_info['marketplace'] = 1 if "Other Sellers on Amazon" in h5_tags else 0
        seller_info['marketplace'] = int(seller_info['marketplace'] or a)

        return seller_info

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None

        in_stock = self.tree_html.xpath('//div[contains(@id, "availability")]//text()')
        in_stock = " ".join(in_stock)
        if 'currently unavailable' in in_stock.lower():
            return 1

        in_stock = self.tree_html.xpath('//div[contains(@id, "outOfStock")]//text()')
        in_stock = " ".join(in_stock)
        if 'currently unavailable' in in_stock.lower():
            return 1

        in_stock = self.tree_html.xpath("//div[@id='buyBoxContent']//text()")
        in_stock = " ".join(in_stock)
        if 'sign up to be notified when this item becomes available' in in_stock.lower():
            return 1

        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    # extract the department which the product belongs to
    def _category_name(self):
        categories = self._categories()

        if not categories:
            return None

        return categories[-1]

    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        categories = self.tree_html.xpath("//div[@id='wayfinding-breadcrumbs_feature_div']//ul//a[@class='a-link-normal a-color-tertiary']/text()")
        categories = [category.strip() for category in categories]

        if not categories:
            return None

        return categories

    def _brand(self):
        bn=self.tree_html.xpath('//div[@id="mbc"]/@data-brand')
        if bn and bn[0].strip():
            return bn[0].strip()
        bn=self.tree_html.xpath('//a[@id="brand"]//text()')
        if bn and bn[0].strip():
            return bn[0].strip()
        bn=self.tree_html.xpath('//div[@class="buying"]//span[contains(text(),"by")]/a//text()')
        if bn and bn[0].strip():
            return bn[0].strip()
        bn=self.tree_html.xpath('//a[contains(@class,"contributorName")]//text()')
        if bn and bn[0].strip():
            return bn[0].strip()
        bn=self.tree_html.xpath('//a[contains(@id,"contributorName")]//text()')
        if bn and bn[0].strip():
            return bn[0].strip()
        bn=self.tree_html.xpath('//span[contains(@class,"author")]//a//text()')
        if bn and bn[0].strip():
            return bn[0].strip()
        fts = self._features()
        if fts:
            for f in fts:
                if f.find("Studio:")>=0 or f.find("Network:")>=0:
                    bn = f.split(':')[1]
                    return bn
        bn=self.tree_html.xpath('//div[@id="ArtistLinkSection"]//text()')
        if len(bn)>0:
            return "".join(bn).strip()

        brand = self.tree_html.xpath("//div[@id='brandByline_feature_div']//a[@id='brand']/@href")
        if brand:
            brand = brand[0]
            brand = brand.split("/")[1].strip()
            return brand
        return None


    def _version(self):
        """Determines if Amazon.co.uk page being read
        Returns:
            "uk" for Amazon.co.uk
            "com" for Amazon.com
        """
         # using url to distinguish between page versions.
        if self.product_page_url.find(".co.uk")>1:
            return "uk"
        return "com"

    ##########################################
    ################ RETURN TYPES
    ##########################################
    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc, \
        "asin" : _asin,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "specs" : _specs, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "seller_ranking": _seller_ranking, \
        "long_description" : _long_description, \
        "apluscontent_desc" : _apluscontent_desc, \
        "variants": _variants, \
        "swatches": _swatches, \
        "related_products_urls":  _related_product_urls, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredient_count, \
        "nutrition_facts": _nutrition_facts, \
        "nutrition_fact_count": _nutrition_fact_count, \
        "no_longer_available": _no_longer_available, \
        "bullet_feature_1": _bullet_feature_1, \
        "bullet_feature_2": _bullet_feature_2, \
        "bullet_feature_3": _bullet_feature_3, \
        "bullet_feature_4": _bullet_feature_4, \
        "bullet_feature_5": _bullet_feature_5, \
        "bullet_feature_6": _bullet_feature_6, \
        "bullet_feature_7": _bullet_feature_7, \
        "bullet_feature_8": _bullet_feature_8, \
        "bullet_feature_9": _bullet_feature_9, \
        "bullet_feature_10": _bullet_feature_10, \
        "bullet_feature_11": _bullet_feature_11, \
        "bullet_feature_12": _bullet_feature_12, \
        "bullet_feature_13": _bullet_feature_13, \
        "bullet_feature_14": _bullet_feature_14, \
        "bullet_feature_15": _bullet_feature_15, \
        "bullet_feature_16": _bullet_feature_16, \
        "bullet_feature_17": _bullet_feature_17, \
        "bullet_feature_18": _bullet_feature_18, \
        "bullet_feature_19": _bullet_feature_19, \
        "bullet_feature_20": _bullet_feature_20, \
        "bullets": _bullets, \
        "usage": _usage, \
        "directions": _directions, \
        "warnings": _warnings, \
        "indications": _indications, \
        "amazon_ingredients" : _amazon_ingredients, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "no_image_available" : _no_image_available, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
#        "no_image" : _no_image, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\
        "canonical_link": _canonical_link,
        "best_seller_category" : _best_seller_category, \

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        "scraper" : _version, \


        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }

def getUserAgent():
    platform = random.choice(['Macintosh', 'Windows', 'X11'])
    if platform == 'Macintosh':
        os  = random.choice(['68K', 'PPC'])
    elif platform == 'Windows':
        os  = random.choice(['Win3.11', 'WinNT3.51', 'WinNT4.0', 'Windows NT 5.0', 'Windows NT 5.1', 'Windows NT 5.2', 'Windows NT 6.0', 'Windows NT 6.1', 'Windows NT 6.2', 'Win95', 'Win98', 'Win 9x 4.90', 'WindowsCE'])
    elif platform == 'X11':
        os  = random.choice(['Linux i686', 'Linux x86_64'])
    browser = random.choice(['chrome', 'firefox', 'ie'])
    if browser == 'chrome':
        webkit = str(random.randint(500, 599))
        version = str(random.randint(0, 24)) + '.0' + str(random.randint(0, 1500)) + '.' + str(random.randint(0, 999))
        return 'Mozilla/5.0 (' + os + ') AppleWebKit/' + webkit + '.0 (KHTML, live Gecko) Chrome/' + version + ' Safari/' + webkit
    elif browser == 'firefox':
        currentYear = datetime.date.today().year
        year = str(random.randint(2000, currentYear))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 30)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        gecko = year + month + day
        version = random.choice(['1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0'])
        return 'Mozilla/5.0 (' + os + '; rv:' + version + ') Gecko/' + gecko + ' Firefox/' + version
    elif browser == 'ie':
        version = str(random.randint(1, 10)) + '.0'
        engine = str(random.randint(1, 5)) + '.0'
        option = random.choice([True, False])
        if option == True:
            token = random.choice(['.NET CLR', 'SV1', 'Tablet PC', 'Win64; IA64', 'Win64; x64', 'WOW64']) + '; '
        elif option == False:
            token = ''
        return 'Mozilla/5.0 (compatible; MSIE ' + version + '; ' + os + '; ' + token + 'Trident/' + engine + ')'
