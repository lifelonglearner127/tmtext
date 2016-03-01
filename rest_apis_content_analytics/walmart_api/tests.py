import os
import time
import sys
import json

from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser, User
import requests
import lxml.html

CWD = os.path.dirname(os.path.abspath(__file__))


from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class RestAPIsTests(StaticLiveServerTestCase):

    reset_sequences = True

    xml_file1 = os.path.join(CWD, 'walmart_product_xml_samples', 'SupplierProductFeed.xsd.xml')
    xml_file2 = os.path.join(CWD, 'walmart_product_xml_samples', 'Verified Furniture Sample Product XML.xml')
    xml_file3 = os.path.join(CWD, 'walmart_product_xml_samples', 'Invalid verified furniture sample product xml.xml')

    @classmethod
    def setUpClass(cls):
        super(RestAPIsTests, cls).setUpClass()
        cls.selenium = webdriver.Chrome()
        with open(settings.TEST_TWEAKS['item_upload_ajax_ignore'], 'w') as fh:
            fh.write('1')

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(RestAPIsTests, cls).tearDownClass()
        if os.path.exists(settings.TEST_TWEAKS['item_upload_ajax_ignore']):
            os.remove(settings.TEST_TWEAKS['item_upload_ajax_ignore'])

    def setUp(self):
        # create user
        self.username = 'admin4'
        self.email = 'admin@admin.com'
        self.password = 'admin46'
        self.user = User.objects.create_superuser(self.username, self.email, self.password)

    def tearDown(self):
        self.user.delete()

    def _auth(self):
        #self.selenium.get(self.live_server_url+'/admin/')
        self.selenium.get(self.live_server_url+'/api-auth/login/')
        self.selenium.find_element_by_name('username').send_keys(self.username)
        self.selenium.find_element_by_name('password').send_keys(self.password + '\n')
        time.sleep(1)  # let the database commit transactions?

    def _http_auth(self, url):
        self.selenium.set_page_load_timeout(4)
        try:
            self.selenium.get(url)
        except:
            self.selenium.set_page_load_timeout(30)
            self.selenium.get('http://'+self.username+':'+self.password+'@'+url.replace('http://', ''))
            return

    def _auth_requests(self):
        session = requests.Session()
        session.auth = (self.username, self.password)
        return session

    def test_login(self):
        self._auth()
        self.assertIn(settings.LOGIN_REDIRECT_URL, self.selenium.current_url)
        self.assertTrue(self.selenium.get_cookie('sessionid'))

    def _test_validate_walmart_product_xml_file_browser(self, xml_file):
        self._auth()
        self.selenium.get(self.live_server_url+'/validate_walmart_product_xml_file/')
        self.selenium.find_element_by_name('xml_file_to_validate').send_keys(xml_file)
        self.selenium.find_element_by_xpath('//*[contains(@class, "form-actions")]/button').click()
        self.assertIn('success', self.selenium.page_source)
        self.assertIn('is validated by Walmart product xsd files', self.selenium.page_source)

    def _test_validate_walmart_product_xml_file_requests(self, xml_file):
        session = self._auth_requests()
        with open(xml_file, 'rb') as payload:
            result = session.post(self.live_server_url+'/validate_walmart_product_xml_file/',
                                  files={'xml_file_to_validate': payload}, verify=False)
            self.assertIn('success', result.text)
            self.assertIn('is validated by Walmart product xsd files', result.text)

    def _test_validate_walmart_product_xml_file_requests_multiple(self, *xml_files):
        session = self._auth_requests()
        xml_files_opened = [open(f, 'rb') for f in xml_files]
        files2post = {'file_'+str(i): f for (i, f) in enumerate(xml_files_opened)}
        result = session.post(self.live_server_url+'/validate_walmart_product_xml_file/',
                              files=files2post, verify=False)
        result_json = json.loads(result.text)
        self.assertIn('success', str(result_json['Verified Furniture Sample Product XML.xml']))
        self.assertIn('error', result_json['SupplierProductFeed.xsd.xml'])

    def test_validate_walmart_product_xml_file(self):
        self._test_validate_walmart_product_xml_file_browser(self.xml_file2)
        self._test_validate_walmart_product_xml_file_requests(self.xml_file2)
        self._test_validate_walmart_product_xml_file_requests_multiple(self.xml_file1, self.xml_file2)

    def test_items_update_with_xml_file_by_walmart_api(self):
        request_url_pattern = 'request_url'
        request_method_pattern = 'request_method'
        xml_file_to_upload_pattern = 'xml_file_to_upload'
        payload = {
            request_url_pattern: 'https://marketplace.walmartapis.com/v2/feeds?feedType=item',
            request_method_pattern: 'POST',
            request_url_pattern+'_2': 'https://marketplace.walmartapis.com/v2/feeds?feedType=item',
            request_method_pattern+'_2': 'POST',
        }
        files = {
            xml_file_to_upload_pattern: open(self.xml_file1, 'rb'),
            xml_file_to_upload_pattern+'_2': open(self.xml_file2, 'rb')
        }
        session = self._auth_requests()
        result = session.post(self.live_server_url+'/items_update_with_xml_file_by_walmart_api/',
                              data=payload, files=files, verify=False)
        result_json = json.loads(result.text)
        self.assertEqual(result_json.get('default', {}).get('error', ''), 'could not find <productId> element')
        self.assertIn('feedId', result_json.get('_2', ''))

    def test_detect_duplicate_content(self):
        # TODO: better test coverage
        # now we only check that this view works for both authenticated and non-authenticated users (in browser)
        self.selenium.delete_all_cookies()  # "logout"
        self._http_auth(self.live_server_url+'/detect_duplicate_content/')
        self.selenium.get(self.live_server_url+'/detect_duplicate_content/')
        self.assertTrue(bool(self.selenium.find_element_by_xpath('//h1[contains(text(), "Detect Duplicate Content")]')))
        self._auth()
        self.selenium.get(self.live_server_url+'/detect_duplicate_content/')
        self.assertTrue(bool(self.selenium.find_element_by_xpath('//h1[contains(text(), "Detect Duplicate Content")]')))

    def test_statistics(self):
        # TODO: the code below is WRONG! fix it
        """
        self.test_items_update_with_xml_file_by_walmart_api()
        self.selenium.delete_all_cookies()  # "logout"
        # remove ajax blocker
        if os.path.exists(settings.TEST_TWEAKS['item_upload_ajax_ignore']):
            os.remove(settings.TEST_TWEAKS['item_upload_ajax_ignore'])
        self.selenium.set_page_load_timeout(2)
        try:
            self._auth()
            self.selenium.get(self.live_server_url+'/items_update_with_xml_file_by_walmart_api/')
        except TimeoutException:
            pass  # sometimes it takes too long to process all requests
        self.selenium.set_page_load_timeout(30)
        import pdb; pdb.set_trace()
        self.assertEqual(self.selenium.find_element_by_id('stat_counter_today').text, '1 / 1')
        self.assertEqual(self.selenium.find_element_by_id('stat_counter_all_time').text, '1')
        self.assertEqual(self.selenium.find_element_by_id('stat_counter_success').text, '1')
        # put ajax blocker back
        # remove ajax blocker
        with open(settings.TEST_TWEAKS['item_upload_ajax_ignore'], 'w') as fh:
            fh.write('1')
        """