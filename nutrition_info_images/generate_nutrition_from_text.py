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

with quitting(webdriver.Firefox()) as driver:
    driver.implicitly_wait(5)
    driver.get('http://www.walmart.com/ip/16564851')
    driver.save_screenshot('/tmp/nutrition_full.png')
    nutrition_element = driver.find_element_by_xpath("//div[@class='NutFactsSIPT']")
    (x,y) = nutrition_element.location.values()
    (h,w) = nutrition_element.size.values()

    full = Image.open('/tmp/nutrition_full.png')
    cropped = full.crop((y, x, y+h, x+w))
    cropped.save('/tmp/nutrition_cropped.png')
