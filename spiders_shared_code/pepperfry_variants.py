import re
import json
import lxml.html


class PepperfryVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        js_block = self.tree_html.cssselect('.vip_size_meta script')
        if len(js_block) != 1:
            return None
        js_block = js_block[0].text
        re_expr = re.search(r'=\s?(\{.*\})', js_block)
        if not re_expr:
            return None
        js_str = re_expr.group(1)
        js_dict = json.loads(js_str)
        if not js_dict:
            return None
        orig_price = self.tree_html.cssselect(
            '[itemprop=price] > [itemprop=price]')
        orig_price = float(orig_price[0].attrib['content'])
        variants = []
        for key, item in js_dict.iteritems():
            variant_price = orig_price + item.get('super_attribute_price', 0)
            variant = {
                'price': variant_price,
                'selected': orig_price == variant_price,
                'properties': {
                    'size': key
                }
            }
            variants.append(variant)
        return variants