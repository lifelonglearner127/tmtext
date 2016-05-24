import time
import sys
import os
import argparse
import logging
import tempfile
import apt


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pyvirtualdisplay import Display


CWD = os.path.dirname(os.path.abspath(__file__))


#Configuration
start_url = 'https://vendorcentral.amazon.com/gp/vendor/sign-in'
headers = "Mozilla/5.0 (Windows NT 6.1; WOW64)" \
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"


def check_system():
    cache = apt.Cache()
    if not cache['tesseract-ocr'].is_installed:
        print('Tesseract is not installed')
        return False
    if not cache['wget'].is_installed:
        print('Wget is not installed')
        return False
    return True


def logging_info(msg):
    print msg


def captcha_images(br):
    return br.find_elements_by_xpath(
        '//img[contains(@alt, "isual CAPTCHA")]'
        '[contains(@src, "amazonaws.com")]')


def solve_login_captcha(br, username, password):
    for i in xrange(15):  # 10 attempts max
        if captcha_images(br):
            captcha_img = captcha_images(br)[0].get_attribute('src')
            # save to a temp file
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            tmp_file.close()
            tmp_file = tmp_file.name
            os.system('wget "{captcha_img}" -O "{tmp_file}"'.format(
                captcha_img=captcha_img, tmp_file=tmp_file))
            # don't forget to install tesseract!
            os.system('tesseract {tmp_file} {recognized_file}'.format(
                tmp_file=tmp_file, recognized_file=tmp_file))
            with open(tmp_file+'.txt', 'r') as fh:
                captcha_text = fh.read().strip()
            if captcha_text:
                password_input = br.find_element_by_name('password')
                password_input.clear()
                password_input.send_keys(password)
                captcha_input = br.find_element_by_id('auth-captcha-guess')
                captcha_input.clear()
                captcha_input.send_keys(captcha_text + '\n')
                time.sleep(5)
                if br.current_url == u'https://vendorcentral.amazon.com/st/vendor/members/dashboard':
                    time.sleep(5)
                    if not captcha_images(br):
                        os.unlink(tmp_file)
                        if os.path.exists(tmp_file + '.txt'):
                            os.unlink(tmp_file + '.txt')
                        return True


def login(br, username, password):
    """ Reliably log into the site, solving captcha if needed """
    br.get(start_url)
    time.sleep(2)
    logging.info('Get to '+start_url)
    login = br.find_element_by_name("username")
    pwd = br.find_element_by_name("password")
    login.send_keys(username)
    pwd.send_keys(password)
    form = br.find_element_by_id("loginForm")
    form.submit()
    time.sleep(3)
    if captcha_images(br):
        solve_login_captcha(br, username, password)  # reliably solve captcha
    if br.current_url == u'https://vendorcentral.amazon.com/st/vendor/members/dashboard':
        logging_info('Passed login form')
        return True


def upload_file(br, file):
    br.find_element_by_link_text("Add images").click()
    time.sleep(3)
    upload = br.find_element_by_name('Content')
    upload.clear()
    upload.send_keys(file)
    br.find_element_by_id('btn_submit').click()
    #form = br.find_element_by_name("ImageUploadForm")
    #form.submit()
    for i in xrange(30):  # wait till there's submission status message
        if br.find_elements_by_partial_link_text('Review the status'):
            break
    time.sleep(5)
    if br.current_url.split('&') and len(br.current_url.split('&')[0].split('?')) > 1 \
            and br.current_url.split('&')[0].split('?')[1] == 'status=ok':
        logging_info('Images were uploaded successfully')
        return True
    else:
        logging_info('Failed to upload images')
        return False


def main():
    if not check_system():
        print('Not all required packages are installed')
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required = True, help="Enter your email")
    parser.add_argument('-p', '--password', type=str, required = True, help = "Enter your password")
    parser.add_argument('--zip_file', type=str, required = True, help="Only zip file name from FTP dir") #TODO Change?
    parser.add_argument('--logging_file', type=str, required = True, help="filename for output logging")

    namespace = parser.parse_args()
    logging.basicConfig(filename=namespace.logging_file, level=logging.DEBUG)
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", headers)

    #Set up headless version of Firefox
    display = Display(visible=1, size=(1280, 1024))
    display.start()

    br = webdriver.Firefox(profile)
    br.set_window_size(1280, 1024)

    if not login(br, namespace.username, namespace.password):
        print("Could not log in! Exit...")
        sys.exit(1)

    if not upload_file(br, namespace.zip_file):
        print("Could not upload the file! Exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()