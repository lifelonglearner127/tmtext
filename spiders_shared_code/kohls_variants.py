import re
import json

import lxml.html

is_empty = lambda x, y="": x[0] if x else y

class KohlsVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        variants_text = is_empty(re.findall(
            "\"variants\"\s+\:\s+([^\]]*)", self.response.body), ""
        ).strip("\n").strip("\t")
        variants_text = variants_text.strip().rstrip(",") + "]"

        try:
            variants_json = json.loads(variants_text)
        except TypeError:
            variants_json = []

        variants = []

        for item in variants_json:
            color = item.get("color", "").split("_")
            size = item.get("size2", "").split("_")
            skuId = item.get("skuId")
            upc = item.get("skuUpcCode")
            price = item.get("SkuSalePrice") or item.get("SkuRegularPrice")
            if price:
                price = price.replace("$", "")
            inStock = item.get("inventoryStatus")
            if inStock == 'true':
                inStock = True
            else:
                inStock = False
            obj = {
                "color": color[len(color)-1],
                "size": size[1],
                "skuId": skuId,
                "upc": upc,
                "price": price,
                "inStock": inStock,
            }
            variants.append(obj)
        if variants:
            return variants
        return None