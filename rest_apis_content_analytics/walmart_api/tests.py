import os
import time
import sys
import json

from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser, User
import requests
import lxml.html

CWD = os.path.dirname(os.path.abspath(__file__))

"""
>>> from django.test import Client
>>> c = Client()
>>> response = c.post('/login/', {'username': 'john', 'password': 'smith'})
>>> response.status_code
200
>>> response = c.get('/customer/details/')
>>> response.content
b'<!DOCTYPE html...'
"""


from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class RestAPIsTests(StaticLiveServerTestCase):
    # TODO: browserless authentication
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        super(RestAPIsTests, cls).setUpClass()
        cls.selenium = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(RestAPIsTests, cls).tearDownClass()

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

    def _auth_requests(self):
        """ Returns "logged-in" requests session """
        session = requests.Session()
        session.auth = (self.username, self.password)
        return session

    def test_login(self):
        self._auth()
        self.assertIn('/accounts/profile/', self.selenium.current_url)
        self.assertTrue(self.selenium.get_cookie('sessionid'))

    def _test_validate_walmart_product_xml_file_browser(self, xml_file):
        self._auth()
        self.selenium.get(self.live_server_url+'/validate_walmart_product_xml_file/')
        self.selenium.find_element_by_name('xml_file_to_validate').send_keys(xml_file)
        self.selenium.find_element_by_xpath('//*[contains(@class, "form-actions")]/button').click()
        self.assertIn('success', self.selenium.page_source)
        self.assertIn('This xml is validated by Walmart product xsd files', self.selenium.page_source)

    @staticmethod
    def _get_csrf_cookie_from_html(html):
        doc = lxml.html.fromstring(html)
        return doc.xpath('//input[@name="csrfmiddlewaretoken"]/@value')[0]

    def _test_validate_walmart_product_xml_file_requests(self, xml_file):
        session = self._auth_requests()
        with open(xml_file, 'rb') as payload:
            result = session.post(self.live_server_url+'/validate_walmart_product_xml_file/',
                                  files={'xml_file_to_validate': payload}, verify=False)
            #self.assertIn('CSRF Failed: CSRF cookie not set', result.text)  # this is correct
            self.assertEqual(json.loads(result.text)['success'], 'This xml is validated by Walmart product xsd files.')

    def test_validate_walmart_product_xml_file(self):
        xml_file1 = os.path.join(CWD, 'walmart_product_xml_samples', 'SupplierProductFeed.xsd.xml')
        xml_file2 = os.path.join(CWD, 'walmart_product_xml_samples', 'Verified Furniture Sample Product XML.xml')
        self._test_validate_walmart_product_xml_file_browser(xml_file2)
        self._test_validate_walmart_product_xml_file_requests(xml_file2)