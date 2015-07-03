#!/usr/bin/python
# Crawls walmart pages and makes a screenshot of the nutrition element
# if it's found as text, generating a nutrition image
import selenium.webdriver as webdriver
from PIL import Image

import contextlib

@contextlib.contextmanager
def quitting(thing):
    yield thing
    thing.quit()

def screenshot_element(urls, element_xpath, image_name="nutrition"):
    with quitting(webdriver.Firefox()) as driver:
        for url in urls:
            driver.implicitly_wait(5)
            driver.get(url)
            driver.save_screenshot('/tmp/' + image_name + '_full.png')
            try:
                nutrition_element = driver.find_element_by_xpath(element_xpath)
                (x,y) = nutrition_element.location.values()
                (h,w) = nutrition_element.size.values()

                full = Image.open('/tmp/' + image_name + '_full.png')
                cropped = full.crop((y, x, y+h, x+w))

                from random import random
                idx = int(random() * 1000)
                cropped.save('/tmp/' + image_name + '_cropped%d.png' % idx)
            except Exception:
                pass