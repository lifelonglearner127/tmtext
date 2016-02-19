from rest_framework import viewsets
import re
import urllib
import json
import requests
from pprint import pprint
from requests.auth import HTTPProxyAuth
import datetime
import mechanize
import cookielib
import os
import random
import os.path
import tempfile
from collections import OrderedDict
from django.views.generic import View as DjangoView
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from subprocess import Popen, PIPE, STDOUT
from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
from rest_framework import viewsets
from walmart_api.serializers import (WalmartApiFeedRequestSerializer, WalmartApiItemsWithXmlFileRequestSerializer,
                                     WalmartApiItemsWithXmlTextRequestSerializer, WalmartApiValidateXmlTextRequestSerializer,
                                     WalmartApiValidateXmlFileRequestSerializer, WalmartDetectDuplicateContentRequestSerializer,
                                     WalmartDetectDuplicateContentFromCsvFileRequestSerializer)
from statistics.models import stat_xml_item
from lxml import etree
import xmltodict
import unirest
import time


FREE_PROXY_IP_PORT_LIST = ["52.91.67.73",
                           "52.90.231.48",
                           "52.91.35.248",
                           "52.90.102.54",
                           "54.164.142.70",
                           "52.90.206.144",
                           "54.175.31.207",
                           "52.91.180.193",
                           "54.172.22.183",
                           "52.90.182.115"]

BROWSER_AGENT_STRING_LIST = {"Firefox": ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
                                         "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
                                         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0"],
                             "Chrome":  ["Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                                         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
                                         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                                         "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"],
                             "Safari":  ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
                                         "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
                                         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2"]
                             }


def choose_free_proxy_from_candidates():
    driver = webdriver.PhantomJS()
    driver.set_window_size(1440, 900)

    driver.get("https://proxy-list.org/english/index.php")

    select_country = driver.find_element_by_xpath("//form[@id='form-search']//select[@name='country']")
    select_country.click()
    option_usa_and_canada = driver.find_element_by_xpath("//form[@id='form-search']//select[@name='country']/option[@value='usa-and-canada']")
    option_usa_and_canada.click()

    select_type = driver.find_element_by_xpath("//form[@id='form-search']//select[@name='type']")
    select_type.click()
    option_anonymous_and_elite = driver.find_element_by_xpath("//form[@id='form-search']//select[@name='type']/option[@value='anonymous-and-elite']")
    option_anonymous_and_elite.click()

    submit_button = driver.find_element_by_xpath("//form[@id='form-search']//input[@value='Search proxy servers']")
    submit_button.click()

    page_raw_text = driver.page_source
    html_tree = html.fromstring(page_raw_text)

    '''
    select_list_length = driver.find_element_by_xpath("//select[@name='proxylisttable_length']")
    select_list_length.click()
    option_length_80 = driver.find_element_by_xpath("//select[@name='proxylisttable_length']/option[@value='80']")
    option_length_80.click()
    select_elite_proxy = driver.find_elements_by_xpath("//tfoot/tr//select")[3]
    select_elite_proxy.click()
    option_elite_proxy = driver.find_element_by_xpath("//tfoot/tr//select/option[@value='elite proxy']")
    option_elite_proxy.click()
    '''

    proxy_info_list = html_tree.xpath("//div[@id='proxy-table']//li[@class='proxy']/text()")[1:]
    driver.close()
    driver.quit()

    return {"http": random.choice(proxy_info_list)}


def remove_duplication_keeping_order_in_list(seq):
    if seq:
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    return None


def select_browser_agents_randomly(agent_type=None):
    if agent_type and agent_type in BROWSER_AGENT_STRING_LIST:
        return random.choice(BROWSER_AGENT_STRING_LIST[agent_type])

    return random.choice(random.choice(BROWSER_AGENT_STRING_LIST.values()))


def initialize_browser_settings(browser):
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    browser.set_cookiejar(cj)

    # Browser options
    browser.set_handle_equiv(True)
    browser.set_handle_gzip(True)
    browser.set_handle_redirect(True)
    browser.set_handle_referer(True)
    browser.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    browser.addheaders = [('User-agent', select_browser_agents_randomly())]

    return browser

def group_params(data, files, patterns):
    """ data = request.data, files=request.files,
        patterns = [param1_to_group, param2_to_group, etc.]
    """
    output = {}
    for data_item_name in data.keys():
        # there may be multiple files/fields being uploaded/sent at the same time
        for data_item_value in data.getlist(data_item_name):
            for pattern in patterns:
                if pattern in data_item_name:
                    param_reminder = data_item_name.replace(pattern, '').strip()
                    if not param_reminder:
                        param_reminder = 'default'
                    if not param_reminder in output:
                        output[param_reminder] = []
                    _item = {'name': data_item_name, 'value': data_item_value, 'type': 'data',
                             'cleaned_name': data_item_name.replace(param_reminder, '')}
                    if not _item in output[param_reminder]:
                        output[param_reminder].append(_item)
    for data_item_name in files.keys():
        for data_item_value in files.getlist(data_item_name):
            for pattern in patterns:
                if pattern in data_item_name:
                    param_reminder = data_item_name.replace(pattern, '').strip()
                    if not param_reminder:
                        param_reminder = 'default'
                    if not param_reminder in output:
                        output[param_reminder] = []
                    _item = {'name': data_item_name, 'value': data_item_value, 'type': 'file',
                             'cleaned_name': data_item_name.replace(param_reminder, '')}
                    if not _item in output[param_reminder]:
                        output[param_reminder].append(_item)
    return output


def find_in_list(lst, key_name, search_in_values=True):
    """ Returns the element of the list which has the given key_name in it """
    result = []
    for e in lst:
        if key_name in e:
            if e['value'] not in result:
                result.append(e['value'])
        if search_in_values:
            for _key, _value in e.items():
                if _value == key_name:
                    if e['value'] not in result:
                        result.append(e['value'])
    return result


def merge_xml_files_into_one(*files):
    """ See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=6198 """
    output_file_template = """
<SupplierProductFeed xmlns="http://walmart.com/suppliers/">
    <version>1.4.1</version>
%s
</SupplierProductFeed>
"""
    output_file = tempfile.NamedTemporaryFile('wb', suffix='.xml', delete=False)
    _sub_templates = ""
    for f in files:
        file_cont = f.read()
        pos1 = file_cont.find('<SupplierProduct>')
        pos2 = file_cont.find('</SupplierProduct>') + len('</SupplierProduct>')
        if pos1 == -1 or pos2 == -1:
            print('Invalid XML file content - could not find "SupplierProduct" opening or closing tag')
            continue
        _sub_templates += ' '*4 + file_cont[pos1:pos2].strip() + '\n'
    output_file.seek(0)
    output_file.write((output_file_template % _sub_templates.strip('\n')).strip())
    output_file.close()
    return output_file.name


class ErrorResponse(object):
    """ A custom error notification """
    def __init__(self, error_type, msg):
        self.error_type = str(error_type)
        self.msg = msg

    def to_json(self):
        return {'error_type': self.error_type, 'error_message': self.msg}

    def to_html(self):
        raise NotImplementedError

    def to_response(self):
        return Response(self.to_json())


def validate_walmart_product_xml_against_xsd(product_xml_string):
    current_path = os.path.dirname(os.path.realpath(__file__))
    xmlschema_doc = etree.parse(current_path + "/walmart_suppliers_product_xsd/SupplierProductFeed.xsd")
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xmlparser = etree.XMLParser(schema=xmlschema)
    product_xml_string = product_xml_string.strip()

    if product_xml_string.startswith("<?xml"):
        product_xml_string = product_xml_string[product_xml_string.find("<", 2):]

    proudct_xml_list = re.findall('<SupplierProduct>(.*?)</SupplierProduct>', product_xml_string, re.DOTALL)
    product_xml_version = re.findall('<version>(.*?)</version>', product_xml_string, re.DOTALL)
    if not product_xml_version:
        return 'error - no product xml version found'
    product_xml_version = product_xml_version[0]
    validation_results = OrderedDict()

    for index, product_xml in enumerate(proudct_xml_list):
        try:
            product_xml = "<SupplierProductFeed xmlns='http://walmart.com/suppliers/'>" \
                          "<version>{0}</version>" \
                          "<SupplierProduct>{1}</SupplierProduct>" \
                          "</SupplierProductFeed>".format(product_xml_version, product_xml.strip())
            product_xml.decode("utf-8").encode("utf-8")
            etree.fromstring(product_xml, xmlparser)
            validation_results['product index ' + str(index + 1)] = 'success - this product is validated by Walmart product xsd files.'
        except Exception, e:
            print e
            validation_results['product index ' + str(index + 1)] = 'error - ' + str(e)

    return validation_results

# Create your views here.

class InvokeWalmartApiViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartApiItemsWithXmlFileRequestSerializer
    parser_classes = (FormParser, MultiPartParser,)

    """
    Walmart API credential info
    """

    walmart_consumer_id = "a8bab1e0-c18c-4be7-b47a-0411153b7514"
    walmart_private_key = "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALBpb58mZiP4VHwx6R7fbPd/u7T22eE7vxECjsS6QHulIN/DExLSFIUrKzHgM11hm7ElRh35cKLcBR/XXZw6u/FTzFQbCiRmuDnJyz53PZi/YjhGTD2GY7jIqVILBz30J/3HRnPx9V0nBnWEEeKBeqb3rYJqsr8k1r71Sy45xey9AgMBAAECgYBFDA+PWCU0QPc4YQSge8yXlpwueUvQF2VyT/D3WPryKjCSxDSL8kPr13ihneIc055vmGo4QzBt3fX3f4D5LBfw9YFH0u29At2p9AH4FiyejhEeQ2tWNR4+zOUiMFVxDyM03zlKAsoJcRz1USklr0J1NtRnPBY7RslXU+wnps4RVQJBAPgzIV5Uo8uT4WYrbxc+Yu4Yd8imFqvGuhZpZdeS1EsRObseZc++v360k5Dx/rJzzJqd4JmeQjMJ2Y76V62jcQsCQQC19L4WYn0EYrPuGWMMoswKmOGHlU8eg3JVooZ/ufrvb6YNjVTDHMFLhU5Netw1s2eMo927giLQXF5+7ANg5MZXAkAqBrZau6g0e2jKHQalf+nOeRQnRIBIO9EcpGIbO4B46YTF+2Kv55OTR85I18ERxGvbrmnueQ6qh7tv61HXU/p7AkAqxePBg1l8JG/DsvgTyllIzHOH2dOFisTf2Jrhf6i7jHVujiC01RejVyz3DcCiZxAagZLoN0lTzcLw9y48Ist1AkEA28Opbyzq6BZOZMvXAQ/HEOGW4CVZZ9rHOwp6JByAIHxQcvwQ++TU/118qdA1HriZTZxGE1dZwnDEa2I79ICfrg=="
    walmart_svc_name = "Walmart Marketplace"
    walmart_environment = "Walmart Marketplace"
    walmart_version = "2nd"
    walmart_qos_correlation_id = "123456abcdef"

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def generate_walmart_api_signature(self, walmart_api_end_point, consumer_id, private_key, request_method, file_path):
        cmd = ('java -jar "' + os.path.dirname(os.path.realpath(__file__)) +
               '/DigitalSignatureUtil-1.0.0.jar" DigitalSignatureUtil {0} {1} {2} {3} {4}').format(walmart_api_end_point,
                                                                                                   consumer_id,
                                                                                                   private_key,
                                                                                                   request_method,
                                                                                                   file_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.readlines()

        if not output[0].startswith("WM_SEC.AUTH_SIGNATURE:") or not output[1].startswith("WM_SEC.TIMESTAMP:"):
            return None

        walmart_api_signature = {"signature": output[0][len("WM_SEC.AUTH_SIGNATURE:"):-1], "timestamp": output[1][len("WM_SEC.TIMESTAMP:"):-1]}

        return walmart_api_signature

    def create(self, request):
        try:
            request_data = request.DATA
            request_files = request.FILES
            walmart_api_signature = self.generate_walmart_api_signature(request_data["request_url"],
                                                                        self.walmart_consumer_id,
                                                                        self.walmart_private_key,
                                                                        request_data["request_method"].upper(),
                                                                        "signature.txt")

            if not walmart_api_signature:
                print "Failed in generating walmart api signature."
                return Response({'data': "Failed in generating walmart api signature."})

            with open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "wb") as upload_file:
                xml_data_by_list = request_files["xml_file_to_upload"].read()
                xml_data_by_list = xml_data_by_list.splitlines()

                for xml_row in xml_data_by_list:
                    upload_file.write((xml_row + "\n").encode("utf-8"))

            upload_file = open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "rb")

            response = unirest.post(request_data["request_url"],
                headers={
                    "Accept": "application/json",
                    "WM_CONSUMER.ID": self.walmart_consumer_id,
                    "WM_SVC.NAME": self.walmart_svc_name,
                    "WM_QOS.CORRELATION_ID": self.walmart_qos_correlation_id,
                    "WM_SVC.VERSION": self.walmart_version,
                    "WM_SVC.ENV": self.walmart_environment,
                    "WM_SEC.AUTH_SIGNATURE": walmart_api_signature["signature"],
                    "WM_SEC.TIMESTAMP": int(walmart_api_signature["timestamp"])
                },
                params={
                    "file": upload_file,
                }
            )

            if type(response.body) is dict:
#                return Response(response.body)

                '''''''''''''''''''''''''''''''''''
                Check feed status begin
                '''''''''''''''''''''''''''''''''''

                walmart_api_signature = self.generate_walmart_api_signature('https://marketplace.walmartapis.com/v2/feeds/{0}?includeDetails=true'.format(response.body['feedId']),
                                                                            self.walmart_consumer_id,
                                                                            self.walmart_private_key,
                                                                            "GET",
                                                                            "signature.txt")

                response = unirest.get('https://marketplace.walmartapis.com/v2/feeds/{0}?includeDetails=true'.format(response.body['feedId']),
                    headers={
                        "Accept": "application/json",
                        "WM_CONSUMER.ID": self.walmart_consumer_id,
                        "WM_SVC.NAME": self.walmart_svc_name,
                        "WM_QOS.CORRELATION_ID": self.walmart_qos_correlation_id,
                        "WM_SVC.VERSION": self.walmart_version,
                        "WM_SVC.ENV": self.walmart_environment,
                        "WM_SEC.AUTH_SIGNATURE": walmart_api_signature["signature"],
                        "WM_SEC.TIMESTAMP": int(walmart_api_signature["timestamp"])
                    }
                )
                return Response(response.body)

                '''''''''''''''''''''''''''''''''''
                Check feed status end
                '''''''''''''''''''''''''''''''''''
            else:
                return Response(xmltodict(response.body))
        except Exception, e:
            print e
            return Response({'data': "Failed to invoke Walmart API - invalid request data"})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class ItemsUpdateWithXmlFileByWalmartApiViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    Pay attention to the field names: if you send multiple groups, name them like this:
    <br/>
    <pre>
    {
      "request_url_1": "http://some_url_1", "request_method_1": "POST", "xml_file_to_upload_1": "/path_to_file_1",
      "request_url_2": "http://some_url_2", "request_method_2": "POST", "xml_file_to_upload_2": "/path_to_file_2",
      "request_url_3": "http://some_url_3", "request_method_2": "POST", "xml_file_to_upload_3": "/path_to_file_3",
      ...
    }
    </pre>
    """
    serializer_class = WalmartApiItemsWithXmlFileRequestSerializer
    parser_classes = (FormParser, MultiPartParser,)

    """
    Walmart API credential info
    """

    walmart_consumer_id = "a8bab1e0-c18c-4be7-b47a-0411153b7514"
    walmart_private_key = "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALBpb58mZiP4VHwx6R7fbPd/u7T22eE7vxECjsS6QHulIN/DExLSFIUrKzHgM11hm7ElRh35cKLcBR/XXZw6u/FTzFQbCiRmuDnJyz53PZi/YjhGTD2GY7jIqVILBz30J/3HRnPx9V0nBnWEEeKBeqb3rYJqsr8k1r71Sy45xey9AgMBAAECgYBFDA+PWCU0QPc4YQSge8yXlpwueUvQF2VyT/D3WPryKjCSxDSL8kPr13ihneIc055vmGo4QzBt3fX3f4D5LBfw9YFH0u29At2p9AH4FiyejhEeQ2tWNR4+zOUiMFVxDyM03zlKAsoJcRz1USklr0J1NtRnPBY7RslXU+wnps4RVQJBAPgzIV5Uo8uT4WYrbxc+Yu4Yd8imFqvGuhZpZdeS1EsRObseZc++v360k5Dx/rJzzJqd4JmeQjMJ2Y76V62jcQsCQQC19L4WYn0EYrPuGWMMoswKmOGHlU8eg3JVooZ/ufrvb6YNjVTDHMFLhU5Netw1s2eMo927giLQXF5+7ANg5MZXAkAqBrZau6g0e2jKHQalf+nOeRQnRIBIO9EcpGIbO4B46YTF+2Kv55OTR85I18ERxGvbrmnueQ6qh7tv61HXU/p7AkAqxePBg1l8JG/DsvgTyllIzHOH2dOFisTf2Jrhf6i7jHVujiC01RejVyz3DcCiZxAagZLoN0lTzcLw9y48Ist1AkEA28Opbyzq6BZOZMvXAQ/HEOGW4CVZZ9rHOwp6JByAIHxQcvwQ++TU/118qdA1HriZTZxGE1dZwnDEa2I79ICfrg=="
    walmart_svc_name = "Walmart Marketplace"
    walmart_environment = "Walmart Marketplace"
    walmart_version = "2nd"
    walmart_qos_correlation_id = "123456abcdef"

    def list(self, request):
        if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt"):

            with open(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt", "r") as myfile:
                log_history = myfile.read().splitlines()
        else:
            log_history = None

        return Response({'log': log_history})

    def retrieve(self, request, pk=None):
        if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt"):
            with open(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt", "r") as myfile:
                log_history = myfile.read().splitlines()
        else:
            log_history = None

        return Response({'log': log_history})

    def generate_walmart_api_signature(self, walmart_api_end_point, consumer_id, private_key, request_method, file_path):
        cmd = ('java -jar "' + os.path.dirname(os.path.realpath(__file__)) +
               '/DigitalSignatureUtil-1.0.0.jar" DigitalSignatureUtil {0} {1} {2} {3} {4}').format(walmart_api_end_point,
                                                                                                   consumer_id,
                                                                                                   private_key,
                                                                                                   request_method,
                                                                                                   file_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.readlines()

        if not output[0].startswith("WM_SEC.AUTH_SIGNATURE:") or not output[1].startswith("WM_SEC.TIMESTAMP:"):
            return None

        walmart_api_signature = {"signature": output[0][len("WM_SEC.AUTH_SIGNATURE:"):-1], "timestamp": output[1][len("WM_SEC.TIMESTAMP:"):-1]}

        return walmart_api_signature

    @staticmethod
    def _group_of_files_contain_invalid_xml(*files):
        for file_ in files:
            validation_results = validate_walmart_product_xml_against_xsd(file_.read())
            file_.seek(0)
            if "error" in validation_results:
                return file_.name, validation_results

    def _parse_submit_output(self, request, output, multi_item):
        if not output:
            return
        feed_id = output.get('feedId', None)
        if feed_id:
            item = output['log'][-1]  # TODO: multiple items will return multiple logs?
            i_date, i_upc, i_feed = item.split(',')
            i_date = datetime.datetime.strptime(i_date.strip(), '%Y-%m-%d %H:%M')
            i_upc = i_upc.strip()
            i_feed = i_feed.strip()
            xml_item = stat_xml_item(request.user, 'session', 'successful', multi_item,  # TODO: auth
                                     error_text=None, upc=i_upc, feed_id=i_feed)
            xml_item.when = i_date
            xml_item.save()
        else:
            xml_item = stat_xml_item(request.user, 'session', 'failed', multi_item,
                                     error_text=str(output))
            xml_item.when = datetime.datetime.now()
            xml_item.save()

    def create(self, request):
        request_url_pattern = 'request_url'
        request_method_pattern = 'request_method'
        xml_file_to_upload_pattern = 'xml_file_to_upload'
        # output
        output = {}
        # group the fields we received
        groupped_fields = group_params(request.data, request.FILES,
                                       [request_url_pattern, request_method_pattern, xml_file_to_upload_pattern])
        # check if we need to merge all the uploaded files into one
        if request.POST.get('submit_as_one_xml_file', None):
            # this option ("submit_as_one_xml_file") merges all the selected files of each group into a single file
            groupped_fields = group_params(request.data, request.FILES,
                                           [request_url_pattern, request_method_pattern, xml_file_to_upload_pattern])
            print('Submitting as a single XML file')
            for group_name, group_data in groupped_fields.items():
                sent_file = find_in_list(group_data, xml_file_to_upload_pattern)
                request_url = find_in_list(group_data, request_url_pattern)
                request_method = find_in_list(group_data, request_method_pattern)
                if not any(sent_file) or not any(request_method) or not any(request_url):
                    output[group_name] = {'error': 'one (or more) required params missing'}
                    continue
                request_url = request_url[0]  # this value can only have 1 element
                request_method = request_method[0]  # this value can only have 1 element
                # there may be multiple files being uploaded at the same group - so create new sub_groups if needed
                invalid_files = ItemsUpdateWithXmlFileByWalmartApiViewSet._group_of_files_contain_invalid_xml(*sent_file)
                if invalid_files:
                    output[group_name] = {}
                    output[group_name][invalid_files[0]] = invalid_files[1]
                    self._parse_submit_output(request, output, True)
                    continue

                merged_file = merge_xml_files_into_one(*sent_file)
                print('Merged files into one: %s' % merged_file)
                merged_file = open(merged_file, 'r')
                try:
                    result_for_this_group = self.process_one_set(
                         request=request, sent_file=merged_file,
                         request_url=request_url, request_method=request_method,
                         do_not_validate_xml=True, multi_item=True)
                except Exception, e:
                    db_stat = stat_xml_item(request.user, 'session', 'failed', True, str(e))
        else:
            print('Submitting as a bunch of files')
            for group_name, group_data in groupped_fields.items():
                sent_file = find_in_list(group_data, xml_file_to_upload_pattern)
                request_url = find_in_list(group_data, request_url_pattern)
                request_method = find_in_list(group_data, request_method_pattern)
                if not any(sent_file) or not any(request_method) or not any(request_url):
                    output[group_name] = {'error': 'one (or more) required params missing'}
                    continue
                request_url = request_url[0]  # this value can only have 1 element
                request_method = request_method[0]  # this value can only have 1 element
                # there may be multiple files being uploaded at the same group - so create new sub_groups if needed
                if len(sent_file) > 1:
                    group_name_postfix = '_file_%i'
                    for file_i, _sent_file in enumerate(sent_file):
                        new_group_name = group_name + group_name_postfix % file_i
                        try:
                            result_for_this_group = self.process_one_set(
                                request=request, sent_file=_sent_file,
                                request_url=request_url, request_method=request_method,
                                multi_item=False)
                            output[new_group_name] = result_for_this_group
                        except Exception, e:
                            output[new_group_name] = {'error': str(e)}
                else:
                    try:
                        result_for_this_group = self.process_one_set(
                            request=request, sent_file=sent_file[0],
                            request_url=request_url, request_method=request_method,
                            multi_item=False)
                        output[group_name] = result_for_this_group
                    except Exception, e:
                        output[group_name] = {'error': str(e)}
        return Response(output)

    def process_one_set(self, request, sent_file, request_url, request_method, do_not_validate_xml=False, multi_item=False):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "wb") as upload_file:
            xml_data_by_list = sent_file.read()
            xml_data_by_list = xml_data_by_list.splitlines()

            for xml_row in xml_data_by_list:
                upload_file.write((xml_row + "\n").decode("utf-8").encode("utf-8"))

        upload_file = open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "rb")
        product_xml_text = upload_file.read()

        # create stat report
        stat_xml_i = stat_xml_item(request.user, 'session', 'successful',
                                   multi_item, error_text=None, upc=None, feed_id=None)

        upc = re.findall(r'<productId>(.*)</productId>', product_xml_text)
        if not upc:
            return_msg = {'error': 'could not find <productId> element'}
            stat_xml_i.status = 'failed'
            stat_xml_i.save()
            stat_xml_i.error_text = str(return_msg)
            return return_msg
        upc = upc[0]
        # we don't use validation against XSD because it fails - instead,
        #  we assume we have checked each sub-product already
        validation_results = 'okay'
        if not do_not_validate_xml:
            validation_results = validate_walmart_product_xml_against_xsd(product_xml_text)

        if "error" in validation_results:
            print validation_results
            stat_xml_i.status = 'failed'
            stat_xml_i.save()
            stat_xml_i.metadata = {'upc': upc}
            stat_xml_i.error_text = str(validation_results)
            return validation_results

        walmart_api_signature = self.generate_walmart_api_signature(request_url,
                                                                    self.walmart_consumer_id,
                                                                    self.walmart_private_key,
                                                                    request_method.upper(),
                                                                    "signature.txt")

        if not walmart_api_signature:
            print "Failed in generating walmart api signature."
            return {'data': "Failed in generating walmart api signature."}

        response = unirest.post(request_url,
            headers={
                "Accept": "application/json",
                "WM_CONSUMER.ID": self.walmart_consumer_id,
                "WM_SVC.NAME": self.walmart_svc_name,
                "WM_QOS.CORRELATION_ID": self.walmart_qos_correlation_id,
                "WM_SVC.VERSION": self.walmart_version,
                "WM_SVC.ENV": self.walmart_environment,
                "WM_SEC.AUTH_SIGNATURE": walmart_api_signature["signature"],
                "WM_SEC.TIMESTAMP": int(walmart_api_signature["timestamp"])
            },
            params={
                "file": upload_file,
            }
        )

        if type(response.body) is dict:
            if "feedId" in response.body:
                feed_id = response.body["feedId"]
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                with open(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt", "a") as myfile:
                    myfile.write(current_time + ", " + upc + ", " + feed_id + "\n")

                with open(os.path.dirname(os.path.realpath(__file__)) + "/walmart_api_invoke_log.txt", "r") as myfile:
                    response.body["log"] = myfile.read().splitlines()

                stat_xml_i.metadata = {'upc': upc, 'feed_id': feed_id}

            else:
                stat_xml_i.status = 'failed'
                stat_xml_i.save()
                stat_xml_i.metadata = {'upc': upc}
                stat_xml_i.error_text = str(response.body)

            return response.body
        else:
            stat_xml_i.status = 'failed'
            stat_xml_i.save()
            stat_xml_i.metadata = {'upc': upc}
            stat_xml_i.error_text = str(response.body)
            return xmltodict(response.body)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class ItemsUpdateWithXmlTextByWalmartApiViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartApiItemsWithXmlTextRequestSerializer

    """
    Walmart API credential info
    """

    walmart_consumer_id = "a8bab1e0-c18c-4be7-b47a-0411153b7514"
    walmart_private_key = "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALBpb58mZiP4VHwx6R7fbPd/u7T22eE7vxECjsS6QHulIN/DExLSFIUrKzHgM11hm7ElRh35cKLcBR/XXZw6u/FTzFQbCiRmuDnJyz53PZi/YjhGTD2GY7jIqVILBz30J/3HRnPx9V0nBnWEEeKBeqb3rYJqsr8k1r71Sy45xey9AgMBAAECgYBFDA+PWCU0QPc4YQSge8yXlpwueUvQF2VyT/D3WPryKjCSxDSL8kPr13ihneIc055vmGo4QzBt3fX3f4D5LBfw9YFH0u29At2p9AH4FiyejhEeQ2tWNR4+zOUiMFVxDyM03zlKAsoJcRz1USklr0J1NtRnPBY7RslXU+wnps4RVQJBAPgzIV5Uo8uT4WYrbxc+Yu4Yd8imFqvGuhZpZdeS1EsRObseZc++v360k5Dx/rJzzJqd4JmeQjMJ2Y76V62jcQsCQQC19L4WYn0EYrPuGWMMoswKmOGHlU8eg3JVooZ/ufrvb6YNjVTDHMFLhU5Netw1s2eMo927giLQXF5+7ANg5MZXAkAqBrZau6g0e2jKHQalf+nOeRQnRIBIO9EcpGIbO4B46YTF+2Kv55OTR85I18ERxGvbrmnueQ6qh7tv61HXU/p7AkAqxePBg1l8JG/DsvgTyllIzHOH2dOFisTf2Jrhf6i7jHVujiC01RejVyz3DcCiZxAagZLoN0lTzcLw9y48Ist1AkEA28Opbyzq6BZOZMvXAQ/HEOGW4CVZZ9rHOwp6JByAIHxQcvwQ++TU/118qdA1HriZTZxGE1dZwnDEa2I79ICfrg=="
    walmart_svc_name = "Walmart Marketplace"
    walmart_environment = "Walmart Marketplace"
    walmart_version = "2nd"
    walmart_qos_correlation_id = "123456abcdef"

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def generate_walmart_api_signature(self, walmart_api_end_point, consumer_id, private_key, request_method, file_path):
        cmd = ('java -jar "' + os.path.dirname(os.path.realpath(__file__)) +
               '/DigitalSignatureUtil-1.0.0.jar" DigitalSignatureUtil {0} {1} {2} {3} {4}').format(walmart_api_end_point,
                                                                                                   consumer_id,
                                                                                                   private_key,
                                                                                                   request_method,
                                                                                                   file_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.readlines()

        if not output[0].startswith("WM_SEC.AUTH_SIGNATURE:") or not output[1].startswith("WM_SEC.TIMESTAMP:"):
            return None

        walmart_api_signature = {"signature": output[0][len("WM_SEC.AUTH_SIGNATURE:"):-1], "timestamp": output[1][len("WM_SEC.TIMESTAMP:"):-1]}

        return walmart_api_signature

    def create(self, request):
        try:
            request_data = request.DATA

            validation_results = validate_walmart_product_xml_against_xsd(request_data["xml_content_to_upload"])

            if "error" in validation_results:
                print validation_results
                return Response(validation_results)

            walmart_api_signature = self.generate_walmart_api_signature(request_data["request_url"],
                                                                        self.walmart_consumer_id,
                                                                        self.walmart_private_key,
                                                                        request_data["request_method"].upper(),
                                                                        "signature.txt")

            if not walmart_api_signature:
                print "Failed in generating walmart api signature."
                return Response({'data': "Failed in generating walmart api signature."})

            with open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "wb") as upload_file:
                xml_data_by_list = request_data["xml_content_to_upload"].splitlines()

                for xml_row in xml_data_by_list:
                    upload_file.write((xml_row + "\n").encode("utf-8"))

            upload_file = open(os.path.dirname(os.path.realpath(__file__)) + "/upload_file.xml", "rb")

            response = unirest.post(request_data["request_url"],
                headers={
                    "Accept": "application/json",
                    "WM_CONSUMER.ID": self.walmart_consumer_id,
                    "WM_SVC.NAME": self.walmart_svc_name,
                    "WM_QOS.CORRELATION_ID": self.walmart_qos_correlation_id,
                    "WM_SVC.VERSION": self.walmart_version,
                    "WM_SVC.ENV": self.walmart_environment,
                    "WM_SEC.AUTH_SIGNATURE": walmart_api_signature["signature"],
                    "WM_SEC.TIMESTAMP": int(walmart_api_signature["timestamp"])
                },
                params={
                    "file": upload_file,
                }
            )

            if type(response.body) is dict:
                return Response(response.body)
            else:
                return Response(xmltodict(response.body))
        except Exception, e:
            print e
            return Response({'data': "Failed to invoke Walmart API - invalid request data"})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class CheckFeedStatusByWalmartApiViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    Pay attention to the field names: if you send multiple groups, name them like this:
    <br/>
    <pre>
    {
      "request_url_1": "http://some_url_1", "feed_id_1": "abc123",
      "request_url_2": "http://some_url_2", "feed_id_2": "abc123",
      "request_url_3": "http://some_url_3", "feed_id_3": "abc123",
      ...
    }
    </pre>
    """
    serializer_class = WalmartApiFeedRequestSerializer
    parser_classes = (FormParser, MultiPartParser,)

    """
    Walmart API credential info
    """

    walmart_consumer_id = "a8bab1e0-c18c-4be7-b47a-0411153b7514"
    walmart_private_key = "MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALBpb58mZiP4VHwx6R7fbPd/u7T22eE7vxECjsS6QHulIN/DExLSFIUrKzHgM11hm7ElRh35cKLcBR/XXZw6u/FTzFQbCiRmuDnJyz53PZi/YjhGTD2GY7jIqVILBz30J/3HRnPx9V0nBnWEEeKBeqb3rYJqsr8k1r71Sy45xey9AgMBAAECgYBFDA+PWCU0QPc4YQSge8yXlpwueUvQF2VyT/D3WPryKjCSxDSL8kPr13ihneIc055vmGo4QzBt3fX3f4D5LBfw9YFH0u29At2p9AH4FiyejhEeQ2tWNR4+zOUiMFVxDyM03zlKAsoJcRz1USklr0J1NtRnPBY7RslXU+wnps4RVQJBAPgzIV5Uo8uT4WYrbxc+Yu4Yd8imFqvGuhZpZdeS1EsRObseZc++v360k5Dx/rJzzJqd4JmeQjMJ2Y76V62jcQsCQQC19L4WYn0EYrPuGWMMoswKmOGHlU8eg3JVooZ/ufrvb6YNjVTDHMFLhU5Netw1s2eMo927giLQXF5+7ANg5MZXAkAqBrZau6g0e2jKHQalf+nOeRQnRIBIO9EcpGIbO4B46YTF+2Kv55OTR85I18ERxGvbrmnueQ6qh7tv61HXU/p7AkAqxePBg1l8JG/DsvgTyllIzHOH2dOFisTf2Jrhf6i7jHVujiC01RejVyz3DcCiZxAagZLoN0lTzcLw9y48Ist1AkEA28Opbyzq6BZOZMvXAQ/HEOGW4CVZZ9rHOwp6JByAIHxQcvwQ++TU/118qdA1HriZTZxGE1dZwnDEa2I79ICfrg=="
    walmart_svc_name = "Walmart Marketplace"
    walmart_environment = "Walmart Marketplace"
    walmart_version = "2nd"
    walmart_qos_correlation_id = "123456abcdef"

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def generate_walmart_api_signature(self, walmart_api_end_point, consumer_id, private_key, request_method, file_path):
        cmd = ('java -jar "' + os.path.dirname(os.path.realpath(__file__)) +
               '/DigitalSignatureUtil-1.0.0.jar" DigitalSignatureUtil {0} {1} {2} {3} {4}').format(walmart_api_end_point,
                                                                                                   consumer_id,
                                                                                                   private_key,
                                                                                                   request_method,
                                                                                                   file_path)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.readlines()

        if not output[0].startswith("WM_SEC.AUTH_SIGNATURE:") or not output[1].startswith("WM_SEC.TIMESTAMP:"):
            return None

        walmart_api_signature = {"signature": output[0][len("WM_SEC.AUTH_SIGNATURE:"):-1], "timestamp": output[1][len("WM_SEC.TIMESTAMP:"):-1]}

        return walmart_api_signature

    def create(self, request):
        output = {}
        request_url_pattern = 'request_url'
        request_feed_id_pattern = "feed_id"
        groupped_fields = group_params(request.POST, request.FILES,
                                       [request_url_pattern, request_feed_id_pattern])
        for group_name, group_data in groupped_fields.items():
            request_url = find_in_list(group_data, request_url_pattern)
            request_feed_id = find_in_list(group_data, request_feed_id_pattern)
            if not any(request_url) or not any(request_feed_id):
                output[group_name] = {'error': 'one (or more) required params missing'}
                continue
            request_url = request_url[0]  # this value can only have 1 element
            request_feed_id = request_feed_id[0]  # this value can only have 1 element
            try:
                result_for_group = self.process_one_set(request_url=request_url, request_feed_id=request_feed_id)
            except Exception as e:
                output[group_name] = {'error': str(e)}
                continue
            output[group_name] = result_for_group
        return Response(output)

    def process_one_set(self, request_url, request_feed_id):
        walmart_api_signature = self.generate_walmart_api_signature(
            request_url.format(feedId=request_feed_id),
            self.walmart_consumer_id,
            self.walmart_private_key,
            "GET",
            "signature.txt")

        response = unirest.get(request_url.format(feedId=request_feed_id),
            headers={
                "Accept": "application/json",
                "WM_CONSUMER.ID": self.walmart_consumer_id,
                "WM_SVC.NAME": self.walmart_svc_name,
                "WM_QOS.CORRELATION_ID": self.walmart_qos_correlation_id,
                "WM_SVC.VERSION": self.walmart_version,
                "WM_SVC.ENV": self.walmart_environment,
                "WM_SEC.AUTH_SIGNATURE": walmart_api_signature["signature"],
                "WM_SEC.TIMESTAMP": int(walmart_api_signature["timestamp"])
            }
        )
        return response.body

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class ValidateWalmartProductXmlTextViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartApiValidateXmlTextRequestSerializer

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def create(self, request):
        request_data = request.data

        return Response(validate_walmart_product_xml_against_xsd(request_data["xml_content_to_validate"]))

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class ValidateWalmartProductXmlFileViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartApiValidateXmlFileRequestSerializer
    parser_classes = (FormParser, MultiPartParser,)

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    @staticmethod
    def is_multiple_files_sent(request):
        for f in request.FILES.keys():
            if f.endswith('_0') or f.endswith('_1'):
                return True

    def create(self, request):
        request_data = request.data
        request_files = request.FILES

        # TODO: it does not work if the content-type is application/x-www-form-urlencoded', is this correct?
        results = {}
        for rf_key in request_files.keys():
            rf_values = request.FILES.getlist(rf_key)
            if not rf_values:
                return ErrorResponse(error_type='', msg='file is missing').to_response()
            if len(rf_values) == 1:
                # single-file upload
                rf_content = rf_values[0].read()
                xml_content_to_validate = rf_content.decode("utf-8").encode("utf-8")
                results[rf_values[0].name] = validate_walmart_product_xml_against_xsd(xml_content_to_validate)
            else:
                # multi-file upload
                for i, file_ in enumerate(rf_values):
                    rf_content = file_.read()
                    xml_content_to_validate = rf_content.decode("utf-8").encode("utf-8")
                    results[file_.name] = validate_walmart_product_xml_against_xsd(xml_content_to_validate)

        return Response(results)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class DetectDuplicateContentBySeleniumViewset(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartDetectDuplicateContentRequestSerializer

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def create(self, request):
        output = {}

        sellers_search_only = True

        if not request.POST.get('detect_duplication_in_sellers_only', None):
            sellers_search_only = False

        product_url_pattern = 'product_url'
        groupped_fields = group_params(request.POST, request.FILES, [product_url_pattern])

        driver = webdriver.PhantomJS()
        driver.set_window_size(1440, 900)
        mechanize_browser = mechanize.Browser()
        mechanize_browser = initialize_browser_settings(mechanize_browser)

        for group_name, group_data in groupped_fields.items():
            product_url = find_in_list(group_data, product_url_pattern)

            if not any(product_url):
                output[group_name] = {'error': 'one (or more) required params missing'}
                continue

            product_url = product_url[0]  # this value can only have 1 element

            try:
                product_id = product_url.split("/")[-1]
                product_json = json.loads(mechanize_browser.open("http://www.walmart.com/product/api/{0}".format(product_id)).read())

                description = None

                if "product" in product_json:
                    if "mediumDescription" in product_json["product"]:
                        description = product_json["product"]["mediumDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                    if not description and "longDescription" in product_json["product"]:
                        description = product_json["product"]["longDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                if not description:
                    raise Exception('No description in product')

                if len(description) > 500:
                    description = description[:500]

                    if description.rfind(" ") > 0:
                        description = description[:description.rfind(" ")].strip()

                if sellers_search_only:
                    driver.get("https://www.google.com/shopping?hl=en")
                else:
                    #means broad search
                    driver.get("https://www.google.com/")

                input_search_text = None

                if sellers_search_only:
                    input_search_text = driver.find_element_by_xpath("//input[@title='Search']")
                else:
                    input_search_text = driver.find_element_by_xpath("//input[@title='Google Search']")

                input_search_text.clear()
                input_search_text.send_keys('"' + description + '"')
                input_search_text.send_keys(Keys.ENTER)
                time.sleep(3)

                current_path = os.path.dirname(os.path.realpath(__file__))
                output_file = open(current_path + "/search_page.html", "w")
                output_file.write(unicode(driver.page_source).encode("utf-8"))
                output_file.close()

                google_search_results_page_raw_text = driver.page_source
                google_search_results_page_html_tree = html.fromstring(google_search_results_page_raw_text)

                if google_search_results_page_html_tree.xpath("//form[@action='CaptchaRedirect']"):
                    raise Exception('Google blocks search requests and claim to input captcha.')

                if google_search_results_page_html_tree.xpath("//title") and \
                                "Error 400 (Bad Request)" in google_search_results_page_html_tree.xpath("//title")[0].text_content():
                    raise Exception('Error 400 (Bad Request)')

                if sellers_search_only:
                    seller_block = None

                    for left_block in google_search_results_page_html_tree.xpath("//ul[@class='sr__group']"):
                        if left_block.xpath("./li[@class='sr__title sr__item']/text()")[0].strip().lower() == "seller":
                            seller_block = left_block
                            break

                    seller_name_list = None

                    if seller_block:
                        seller_name_list = seller_block.xpath(".//li[@class='sr__item']//a/text()")
                        seller_name_list = [seller for seller in seller_name_list if seller.lower() != "walmart"]

                    if not seller_name_list:
                        output[product_url] = "Unique content."
                    else:
                        output[product_url] = "Found duplicate content from other sellers: ." + ", ".join(seller_name_list)
                else:
                    duplicate_content_links = google_search_results_page_html_tree.xpath("//div[@id='search']//cite/text()")

                    if duplicate_content_links:
                        duplicate_content_links = [url for url in duplicate_content_links if "walmart.com" not in url.lower()]

                    if not duplicate_content_links:
                        output[product_url] = "Unique content."
                    else:
                        output[product_url] = "Found duplicate content from other links."

            except Exception, e:
                print e
                output[product_url] = str(e)
                continue

        driver.close()
        driver.quit()
        mechanize_browser.close()

        if output:
            return Response(output)

        return None

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class DetectDuplicateContentByMechanizeViewset(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartDetectDuplicateContentRequestSerializer

    def list(self, request):

        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    '''
    def create(self, request):
        output = {}

        sellers_search_only = False
        product_url_pattern = 'product_url'
        groupped_fields = group_params(request.POST, request.FILES, [product_url_pattern])

        for group_name, group_data in groupped_fields.items():
            product_url = find_in_list(group_data, product_url_pattern)

            if not any(product_url):
                output[group_name] = {'error': 'one (or more) required params missing'}
                continue

            product_url = product_url[0]  # this value can only have 1 element

            try:
                product_id = product_url.split("/")[-1]
                product_json = json.loads(requests.get("http://www.walmart.com/product/api/{0}".format(product_id)).text)

                description = None

                if "product" in product_json:
                    if "mediumDescription" in product_json["product"]:
                        description = product_json["product"]["mediumDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                    if not description and "longDescription" in product_json["product"]:
                        description = product_json["product"]["longDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                    if not description and "shortDescription" in product_json["product"]:
                        description = product_json["product"]["shortDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                if not description:
                    raise Exception('No description in product')

                description = description.replace('"', '')

                if len(description) > 500:
                    description = description[:500]

                    if description.rfind(" ") > 0:
                        description = description[:description.rfind(" ")].strip()

                proxy = random.choice(FREE_PROXY_IP_PORT_LIST)

                results = None

                if sellers_search_only:
                    results = json.loads(requests.get('http://{0}/google_search?query="{1}"&sellers_search_only=true'.format(proxy, description)).text)
                else:
                    #means broad search
                    results = json.loads(requests.get('http://{0}/google_search?query="{1}"'.format(proxy, description)).text)

                if results["success"] == 1:
                    output[product_url] = results["message"]
                else:
                    output[product_url] = "Found duplicate content from other links."
#                    raise Exception(results["message"])
            except Exception, e:
                print e
                output[product_url] = str(e)

        if output:
            return Response(output)

        return None
    '''

    def create(self, request):
        output = {}

        sellers_search_only = True

        if not request.POST.get('detect_duplication_in_sellers_only', None):
            sellers_search_only = False

        product_url_pattern = 'product_url'
        groupped_fields = group_params(request.POST, request.FILES, [product_url_pattern])


        search_url = "http://www.google.com/search?oe=utf8&ie=utf8&source=uds&start=0&hl=en&q={0}"
        proxy_host = "proxy.crawlera.com"
        proxy_port = "8010"
        proxy_auth = HTTPProxyAuth("eff4d75f7d3a4d1e89115c0b59fab9b2", "")
        proxies = {"http": "http://{}:{}/".format(proxy_host, proxy_port)}
        retry_number = 3
        word_search_limit = 10

        for group_name, group_data in groupped_fields.items():
            product_url = find_in_list(group_data, product_url_pattern)

            if not any(product_url):
                output[group_name] = {'error': 'one (or more) required params missing'}
                continue

            product_url = product_url[0]  # this value can only have 1 element
            short_description = long_description = ""

            try:
                product_json = json.loads(requests.get("http://52.1.156.214/get_data?url={0}".format(product_url)).text)

                if product_json["product_info"]["description"]:
                    short_description = product_json["product_info"]["description"]

                if product_json["product_info"]["long_description"]:
                    long_description = product_json["product_info"]["long_description"]

                if short_description:
                    short_description = short_description.replace("<", " <")
                    short_description = html.fromstring("<html>" + short_description + "</html>").text_content().strip()
                    short_description = short_description.replace('"', '')
                    cursor = short_description.find(" ", 0)
                    word_count = 0

                    while cursor >= 0:
                        relative_index = cursor + 1

                        if relative_index >= len(short_description):
                            break

                        for index in range(relative_index, len(short_description)):
                            if short_description[relative_index] != " ":
                                break

                        cursor = short_description.find(" ", relative_index)
                        word_count += 1

                        if word_count >= word_search_limit:
                            break

                    if cursor > 0:
                        short_description = short_description[:cursor]

                    short_description = '"' + short_description + '"'

                if long_description:
                    if long_description.startswith("<b>"):
                        long_description = long_description[long_description.find("</b>") + 4:]

                    long_description = long_description.replace("<", " <")
                    long_description = html.fromstring("<html>" + long_description + "</html>").text_content().strip()
                    long_description = long_description.replace('"', '')
                    cursor = long_description.find(" ", 0)
                    word_count = 0

                    while cursor >= 0:
                        relative_index = cursor + 1

                        if relative_index >= len(long_description):
                            break

                        for index in range(relative_index, len(long_description)):
                            if long_description[relative_index] != " ":
                                break

                        cursor = long_description.find(" ", relative_index)
                        word_count += 1

                        if word_count >= word_search_limit:
                            break

                    if cursor > 0:
                        long_description = long_description[:cursor]

                    long_description = '"' + long_description + '"'

                if not short_description and not long_description:
                    raise Exception('No description in product')
            except Exception, e:
                output[product_url] = str(e)
                continue

            description_list = [short_description, long_description]

            is_duplicated = False

            for description in description_list:
                if not description:
                    continue

                for retry_index in range(retry_number):
                    try:
                        input_search_text = None

                        google_search_results_page_raw_text = None
                        '''
                        if sellers_search_only:
                            mechanize_browser.open("https://www.google.com/shopping?hl=en")
                            mechanize_browser.select_form('f')
                            mechanize_browser.form['q'] = '"{0}"'.format(description)
                            mechanize_browser.submit()
                        else:
                            #means broad search
                            mechanize_browser.open("https://www.google.com/")
                            mechanize_browser.select_form('f')
                            mechanize_browser.form['q'] = '"{0}"'.format(description)
                            mechanize_browser.submit()

                        google_search_results_page_raw_text = mechanize_browser.response().read()
                        '''

                        google_search_results_page_raw_text = requests.get(search_url.format(urllib.quote(description.encode("utf-8"))),
                                                                           proxies=proxies,
                                                                           auth=proxy_auth,
                                                                           verify=os.path.dirname(os.path.realpath(__file__)) + "/crawlera-ca.crt").text
                        google_search_results_page_html_tree = html.fromstring(google_search_results_page_raw_text)

                        if google_search_results_page_html_tree.xpath("//form[@action='CaptchaRedirect']"):
                            raise Exception('Google blocks search requests and claim to input captcha.')

                        if google_search_results_page_html_tree.xpath("//title") and \
                                        "Error 400 (Bad Request)" in google_search_results_page_html_tree.xpath("//title")[0].text_content():
                            raise Exception('Error 400 (Bad Request)')

                        if sellers_search_only:
                            seller_block = None

                            for left_block in google_search_results_page_html_tree.xpath("//ul[@class='sr__group']"):
                                if left_block.xpath("./li[@class='sr__title sr__item']/text()")[0].strip().lower() == "seller":
                                    seller_block = left_block
                                    break

                            seller_name_list = None

                            if seller_block:
                                seller_name_list = seller_block.xpath(".//li[@class='sr__item']//a/text()")
                                seller_name_list = [seller for seller in seller_name_list if seller.lower() != "walmart"]

                            if not seller_name_list:
                                output[product_url] = "Unique content."
                            else:
                                output[product_url] = "Found duplicate content from other sellers: ." + ", ".join(seller_name_list)
                        else:
                            duplicate_content_links = google_search_results_page_html_tree.xpath("//div[@id='search']//cite/text()")

                            if "No results found for {0}".format(description) in google_search_results_page_html_tree.text_content():
                                duplicate_content_links = None

                            if duplicate_content_links:
                                duplicate_content_links = [url for url in duplicate_content_links if "walmart.com" not in url.lower()]

                            if duplicate_content_links:
                                is_duplicated = True
                                break
                        break
                    except Exception, e:
                        print e
                        continue

                if is_duplicated:
                    break

            if is_duplicated:
                output[product_url] = "Found duplicate content from other links."
            else:
                output[product_url] = "Unique content."

        if output:
            return Response(output)

        return None


    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class DetectDuplicateContentFromCsvFilesByMechanizeViewset(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartDetectDuplicateContentFromCsvFileRequestSerializer

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def create(self, request):
        product_url_list = None

        try:
            request_data = request.DATA
            request_files = request.FILES
            product_url_list = request_files["csv_file_to_check"].read().splitlines()
        except Exception, e:
            print e
            return Response({'data': "Invalid csv format."})

        output = {}

        sellers_search_only = True

        if not request.POST.get('detect_duplication_in_sellers_only', None):
            sellers_search_only = False

        product_url_pattern = 'product_url'
        groupped_fields = group_params(request.POST, request.FILES, [product_url_pattern])

        mechanize_browser = mechanize.Browser()
        mechanize_browser = initialize_browser_settings(mechanize_browser)

        #mechanize_browser.add_password(url, "test", "test1234")

        for product_url in product_url_list:
            retry_number = 0

            while True:
                try:
                    retry_number += 1
                    mechanize_browser.set_proxies(random.choice(FREE_PROXY_IP_PORT_LIST))

                    #mechanize_browser.set_proxies({"http": "107.151.152.218:80"})

                    product_id = product_url.split("/")[-1]
                    product_json = json.loads(mechanize_browser.open("http://www.walmart.com/product/api/{0}".format(product_id), timeout=3.0).read())

                    description = None

                    if "product" in product_json:
                        if "mediumDescription" in product_json["product"]:
                            description = product_json["product"]["mediumDescription"]
                            description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                        if not description and "longDescription" in product_json["product"]:
                            description = product_json["product"]["longDescription"]
                            description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                    if not description:
                        raise Exception('No description in product')

                    if len(description) > 500:
                        description = description[:500]

                        if description.rfind(" ") > 0:
                            description = description[:description.rfind(" ")].strip()

                    input_search_text = None

                    google_search_results_page_raw_text = None

                    mechanize_browser.set_proxies(random.choice(FREE_PROXY_IP_PORT_LIST))

                    if sellers_search_only:
                        mechanize_browser.open("https://www.google.com/shopping?hl=en", timeout=3.0)
                        mechanize_browser.select_form('f')
                        mechanize_browser.form['q'] = '"{0}"'.format(description)
                        mechanize_browser.submit()
                    else:
                        #means broad search
                        mechanize_browser.open("https://www.google.com/", timeout=3.0)
                        mechanize_browser.select_form('f')
                        mechanize_browser.form['q'] = '"{0}"'.format(description)
                        mechanize_browser.submit()

                    google_search_results_page_raw_text = mechanize_browser.response().read()

                    current_path = os.path.dirname(os.path.realpath(__file__))
                    output_file = open(current_path + "/search_page.html", "w")
                    output_file.write(google_search_results_page_raw_text.decode("utf-8").encode("utf-8"))
                    output_file.close()

                    google_search_results_page_html_tree = html.fromstring(google_search_results_page_raw_text)

                    if google_search_results_page_html_tree.xpath("//form[@action='CaptchaRedirect']"):
                        raise Exception('Google blocks search requests and claim to input captcha.')

                    if google_search_results_page_html_tree.xpath("//title") and \
                                    "Error 400 (Bad Request)" in google_search_results_page_html_tree.xpath("//title")[0].text_content():
                        raise Exception('Error 400 (Bad Request)')

                    if sellers_search_only:
                        seller_block = None

                        for left_block in google_search_results_page_html_tree.xpath("//ul[@class='sr__group']"):
                            if left_block.xpath("./li[@class='sr__title sr__item']/text()")[0].strip().lower() == "seller":
                                seller_block = left_block
                                break

                        seller_name_list = None

                        if seller_block:
                            seller_name_list = seller_block.xpath(".//li[@class='sr__item']//a/text()")
                            seller_name_list = [seller for seller in seller_name_list if seller.lower() != "walmart"]

                        if not seller_name_list:
                            output[product_url] = "Unique content."
                        else:
                            output[product_url] = "Found duplicate content from other sellers: ." + ", ".join(seller_name_list)
                    else:
                        duplicate_content_links = google_search_results_page_html_tree.xpath("//div[@id='search']//cite/text()")

                        if duplicate_content_links:
                            duplicate_content_links = [url for url in duplicate_content_links if "walmart.com" not in url.lower()]

                        if not duplicate_content_links:
                            output[product_url] = "Unique content."
                        else:
                            output[product_url] = "Found duplicate content from other links."

                    break
                except Exception, e:
                    print e
                    output[product_url] = str(e)

                    current_path = os.path.dirname(os.path.realpath(__file__))
                    output_file = open(current_path + "/search_page.html", "a")
                    output_file.write(str(e))
                    output_file.close()

                    if retry_number > 10:
                        break

                    continue

        mechanize_browser.close()

        if output:
            return Response(output)

        return None

    '''
    def create(self, request):
        output = {}

        sellers_search_only = True

        if not request.POST.get('detect_duplication_in_sellers_only', None):
            sellers_search_only = False

        product_url_pattern = 'product_url'
        groupped_fields = group_params(request.POST, request.FILES, [product_url_pattern])

        mechanize_browser = mechanize.Browser()
        mechanize_browser = initialize_browser_settings(mechanize_browser)

        for group_name, group_data in groupped_fields.items():
            product_url = find_in_list(group_data, product_url_pattern)

            if not any(product_url):
                output[group_name] = {'error': 'one (or more) required params missing'}
                continue

            product_url = product_url[0]  # this value can only have 1 element

            try:
                product_id = product_url.split("/")[-1]
                product_json = json.loads(mechanize_browser.open("http://www.walmart.com/product/api/{0}".format(product_id)).read())

                description = None

                if "product" in product_json:
                    if "mediumDescription" in product_json["product"]:
                        description = product_json["product"]["mediumDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                    if not description and "longDescription" in product_json["product"]:
                        description = product_json["product"]["longDescription"]
                        description = html.fromstring("<html>" + description + "</html>").text_content().strip()

                if not description:
                    raise Exception('No description in product')

                if len(description) > 500:
                    description = description[:500]

                    if description.rfind(" ") > 0:
                        description = description[:description.rfind(" ")].strip()

                input_search_text = None

                google_search_results_page_raw_text = None

                if sellers_search_only:
                    mechanize_browser.open("https://www.google.com/shopping?hl=en")
                    mechanize_browser.select_form('f')
                    mechanize_browser.form['q'] = '"{0}"'.format(description)
                    mechanize_browser.submit()
                else:
                    #means broad search
                    mechanize_browser.open("https://www.google.com/")
                    mechanize_browser.select_form('f')
                    mechanize_browser.form['q'] = '"{0}"'.format(description)
                    mechanize_browser.submit()

                google_search_results_page_raw_text = mechanize_browser.response().read()

                current_path = os.path.dirname(os.path.realpath(__file__))
                output_file = open(current_path + "/search_page.html", "w")
                output_file.write(google_search_results_page_raw_text.decode("utf-8").encode("utf-8"))
                output_file.close()

                google_search_results_page_html_tree = html.fromstring(google_search_results_page_raw_text)

                if google_search_results_page_html_tree.xpath("//form[@action='CaptchaRedirect']"):
                    raise Exception('Google blocks search requests and claim to input captcha.')

                if google_search_results_page_html_tree.xpath("//title") and \
                                "Error 400 (Bad Request)" in google_search_results_page_html_tree.xpath("//title")[0].text_content():
                    raise Exception('Error 400 (Bad Request)')

                if sellers_search_only:
                    seller_block = None

                    for left_block in google_search_results_page_html_tree.xpath("//ul[@class='sr__group']"):
                        if left_block.xpath("./li[@class='sr__title sr__item']/text()")[0].strip().lower() == "seller":
                            seller_block = left_block
                            break

                    seller_name_list = None

                    if seller_block:
                        seller_name_list = seller_block.xpath(".//li[@class='sr__item']//a/text()")
                        seller_name_list = [seller for seller in seller_name_list if seller.lower() != "walmart"]

                    if not seller_name_list:
                        output[product_url] = "Unique content."
                    else:
                        output[product_url] = "Found duplicate content from other sellers: ." + ", ".join(seller_name_list)
                else:
                    duplicate_content_links = google_search_results_page_html_tree.xpath("//div[@id='search']//cite/text()")

                    if duplicate_content_links:
                        duplicate_content_links = [url for url in duplicate_content_links if "walmart.com" not in url.lower()]

                    if not duplicate_content_links:
                        output[product_url] = "Unique content."
                    else:
                        output[product_url] = "Found duplicate content from other links."

            except Exception, e:
                print e
                output[product_url] = str(e)
                continue

        mechanize_browser.close()

        if output:
            return Response(output)

        return None
    '''

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class FeedIDRedirectView(DjangoView):
    def get(self, request, *args, **kwargs):
        context = {'feed_id': kwargs.get('feed_id', None)}
        context.update(csrf(request))
        return render_to_response(template_name='redirect_to_feed_check.html', context=context)
