import cookielib

from scrapy.spider import Spider
from scrapy.log import INFO
from scrapy.http import Request
from mechanize import Browser

# Browser Config
start_url = 'https://vendorcentral.amazon.com/gp/vendor/sign-in'
headers = [
    ("User-Agent",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
     " Chrome/50.0.2661.94 Safari/537.36")
]
cj = cookielib.LWPCookieJar()

#TODO and this Xpath if needed to parse status of image
#//td[contains(@class, "x-grid3-td-columnStatus")] Container for status in review_status page


class VendorCentral(Spider):
    name = 'vendor_central'
    allowed_domains = ['vendorcentral.amazon.com']
    start_urls = ['https://vendorcentral.amazon.com/gp/vendor/sign-in']

    def __init__(self, username=None, password=None, zip_file=None):
        super(VendorCentral, self).__init__()
        self.username = username
        self.password = password
        self.zip_file = zip_file

    def parse(self, response):
        br = Browser()
        br.set_cookiejar(cj)
        br.addheaders = headers

        #Passing robots.txt error
        br.set_handle_robots(False)

        br.open(start_url)
        self.log('Get to ' + start_url, INFO)
        br.select_form(nr=0)
        br['username'] = self.username
        br['password'] = self.password
        br.submit()
        self.log('Passed Login form', INFO)
        req = br.click_link(text="Add images")
        br.open(req)
        self.log('Ready to upload Files', INFO)
        br.select_form(nr=0)
        br.set_all_readonly(False)

        br.form.add_file(open(self.zip_file, 'rb'))
        resp = br.submit()
        self.log('Images where uploaded successfully!')

        """
        Uncomment if need to parse status from status page
        
        review_request = br.click_link(text="Review the status").get_full_url()
        yield Request(review_request, callback = self.parse_status)
        
        """
