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

        # scrape JSON variants
        variants_text = is_empty(re.findall(
            "\"variants\"\s+\:\s+([^\]]*)", self.response.body), ""
        ).strip("\n").strip("\t")
        variants_text = variants_text.strip().rstrip(",") + "]"

        try:
            variants_json = json.loads(variants_text)
        except TypeError:
            variants_json = []

        variants = []

        active_c = is_empty(self.tree_html.xpath(
            "//div[contains(@class, 'swatch active')]/@id"), "").split("_")
        if active_c:
            active_c = active_c[len(active_c)-1]

        for item in variants_json:
            color = item.get("color", "").split("_")
            selected = False
            if color[len(color)-1].strip() == active_c.strip():
                selected = True
            size = item.get("size2", "").split("_")
            skuId = item.get("skuId")
            upc = item.get("skuUpcCode")
            price = item.get("SkuSalePrice") or item.get("SkuRegularPrice") or 0
            if price:
                price = price.replace("$", "")
            inStock = item.get("inventoryStatus")
            if inStock == 'true':
                inStock = True
            else:
                inStock = False
            obj = {
                "skuId": skuId,
                "upc": upc,
                "price": float(price),
                "in_stock": inStock,
                "properties": {
                    "color": color[len(color)-1],
                    "size": size[1],
                },
                "selected": selected,
            }
            variants.append(obj)

        # scrape HTML variants (to get images)
        for var in self.tree_html.xpath(
                '//div[contains(@itemtype, "roduct")]'):
            sku = var.xpath('.//meta[contains(@itemprop, "sku")]/@content')
            if not sku:
                continue
            sku = sku[0].strip()
            img = var.xpath('.//meta[contains(@itemprop, "imageUrl")]/@content')
            if not img:
                continue
            img = img[0].strip()
            # find the appropriate JSON variant by matching SKUs
            for json_var in variants:
                if sku == json_var.get('skuId', ''):
                    json_var['image_url'] = img

        if variants:
            return variants

        return None