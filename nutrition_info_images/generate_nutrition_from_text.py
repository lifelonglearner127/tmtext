#!/usr/bin/python
# Crawls walmart pages and makes a screenshot of the nutrition element
# if it's found as text, generating a nutrition image
import selenium.webdriver as webdriver
from PIL import Image
import sys
import contextlib

@contextlib.contextmanager
def quitting(thing):
    yield thing
    thing.quit()

def screenshot_element(urls, element_xpaths, image_name="nutrition"):
    with quitting(webdriver.Firefox()) as driver:
        for url in urls:
            driver.implicitly_wait(5)
            driver.get(url)
            # need to scroll down to nutrition section to be able to load element
            driver.execute_script("scroll(0,1500)")
            driver.wait(5)
            
            ok = False
            try:
                nutrition_element = driver.find_element_by_xpath(element_xpaths[0])
                ok = True
                print "found"
            except Exception, e:
                print "not found", e
                try:
                    driver.execute_script("scroll(0,1500)")
                    driver.wait(5)
                    nutrition_element = driver.find_element_by_xpath(element_xpaths[0])
                    ok = True
                    print "found"
                except Exception, e:
                    print "not found", e
                    ok = False
                    try:
                        nutrition_element = driver.find_element_by_xpath(element_xpaths[1])
                        ok = True
                    except Exception, e:
                        print "not found", e
                        ok = False
                        try:
                            driver.execute_script("scroll(0,1500)")
                            driver.wait(5)
                            nutrition_element = driver.find_element_by_xpath(element_xpaths[1])
                            ok = True
                        except Exception, e:
                            print "not found", e
                            ok = False
            if ok:
                driver.save_screenshot('/tmp/' + image_name + '_full.png')

                (x,y) = nutrition_element.location.values()
                (h,w) = nutrition_element.size.values()

                full = Image.open('/tmp/' + image_name + '_full.png')
                cropped = full.crop((y, x, y+h, x+w))

                from random import random
                idx = int(random() * 1000)
                cropped.save('/tmp/' + image_name + '_cropped%d.png' % idx)

if __name__=='__main__':
    screenshot_element([sys.argv[1]], ("//div[@class='nutrition-section']", "//div[@class='NutFactsSIPT']"))