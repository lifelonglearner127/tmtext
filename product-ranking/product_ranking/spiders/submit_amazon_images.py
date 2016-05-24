import time
import sys
import os
import argparse
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pyvirtualdisplay import Display


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..'))


try:
    from captcha_solver import CaptchaBreakerWrapper, CaptchaBreaker
except ImportError as e:
    import sys
    print(
        "### Failed to import CaptchaBreaker.",
        "Will continue without solving captchas:",
    )

    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            print("No CaptchaBreaker to solve: %s" % url)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker


#Configuration
FTP_path = '/home/ubuntu/FTP/Images/'
Script_path = '/home/ubuntu/Script/'
start_url = 'https://vendorcentral.amazon.com/gp/vendor/sign-in'
headers = "Mozilla/5.0 (Windows NT 6.1; WOW64)" \
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"


def solve_captcha(local_captcha_file_or_url):
    captcha_text = None
    try:
        cb = CaptchaBreaker(os.path.join(CWD, '..', '..', '..', 'search', 'train_captchas_data'))
        print("Training captcha classifier...")
        captcha_text = cb.test_captcha(local_captcha_file_or_url)
    except Exception, e:
        print(str(e))
    return captcha_text


def logging_info(msg):
    print msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required = True, help="Enter your email")
    parser.add_argument('-p', '--password', type=str, required = True, help = "Enter your password")
    parser.add_argument('--zip_file', type=str, required = True, help="Only zip file name from FTP dir") #TODO Change?
    parser.add_argument('--logging_file', type=str, required = True, help="filename for output logging")

    namespace = parser.parse_args()
    logging.basicConfig(filename=namespace.logging_file,level=logging.DEBUG)
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", headers)

    #Set up headless version of Firefox
    display = Display(visible=1, size=(1024, 768))
    display.start()

    br = webdriver.Firefox(profile)

    br.get(start_url)
    time.sleep(2)
    logging.info('Get to '+start_url)
    login = br.find_element_by_name("username")
    pwd = br.find_element_by_name("password")
    login.send_keys(namespace.username)
    pwd.send_keys(namespace.password)
    form = br.find_element_by_id("loginForm")
    form.submit()
    time.sleep(100)
    if br.current_url == u'https://vendorcentral.amazon.com/st/vendor/members/dashboard':
        logging_info('Passed login form')
    br.find_element_by_link_text("Add images").click()
    time.sleep(3)
    upload = br.find_element_by_name('Content')
    upload.clear()
    upload.send_keys(FTP_path+namespace.zip_file)    #TODO change for argv
    form = br.find_element_by_name("ImageUploadForm")
    form.submit()
    time.sleep(7)
    if br.current_url.split('&')[0].split('?')[1] == 'status=ok':
        logging_info('Images where uploaded successfully')
    else:
        logging_info('Failed to upload images')


if __name__ == '__main__':
    print solve_captcha('/tmp/cap.jpg')
    main()