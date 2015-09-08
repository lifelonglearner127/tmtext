import re
import json

import lxml.html
import requests
import json

from lxml import html, etree

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
        page_raw_text = html.tostring(self.tree_html)
        # scrape JSON variants
        variants_text = is_empty(re.findall(
            "\"variants\"\s+\:\s+([^\]]*)", page_raw_text), ""
        ).strip("\n").strip("\t")
        variants_text = variants_text.strip().rstrip(",") + "]"

        variants_count = is_empty(
            re.findall(
                r'availablevariantsCount_product\s*=\s*\'(\d+)\'',
                page_raw_text
            ), 0
        )

        try:
            variants_count = int(variants_count)
        except ValueError:
            variants_count = 0

        if variants_count == 0:
            return []

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
            if not ("". join(color)).strip():
                color = ["not supported"]
            selected = False
            if color[len(color)-1].strip() == active_c.strip():
                selected = True
            size = item.get("size2", "").split("_")
            if not ("". join(size)).strip():
                size = ["not supported", "not supported"]
            skuId = item.get("skuId")
            upc = item.get("skuUpcCode")
            price = item.get("SkuSalePrice") or item.get("SkuRegularPrice") or 0
            if price:
                try:
                    price_amount = float(re.findall(r"[-+]?\d*\.\d+|\d+", price.replace("$", ""))[0])
                except:
                    price_amount = None
            inStock = item.get("inventoryStatus")
            if inStock == 'true':
                inStock = True
            else:
                inStock = False
            obj = {
                "skuId": skuId,
                "upc": upc,
                "price": price_amount,
                "in_stock": inStock,
                "properties": {
                    "color": color[len(color)-1],
                    "size": size[1],
                },
                'unavailable': False,
                "selected": selected,
            }
            variants.append(obj)

        color_value_list = []
        size_value_list = []
        instock_variant_combination_list = []

        for variant in variants:
            color_value_list.append(variant["properties"]["color"])
            size_value_list.append(variant["properties"]["size"])
            instock_variant_combination_list.append([variant["properties"]["color"], variant["properties"]["size"]])

        color_value_list = list(set(color_value_list))
        size_value_list = list(set(size_value_list))

        all_combinations = []

        for color in color_value_list:
            for size in size_value_list:
                all_combinations.append([color, size])

                if [color, size] in instock_variant_combination_list:
                    continue

                obj = {
                    "skuId": None,
                    "upc": None,
                    "price": None,
                    "in_stock": False,
                    "properties": {
                        "color": color,
                        "size": size,
                    },
                    'unavailable': True,
                    "selected": False,
                }

                variants.append(obj)

        for index, variant in enumerate(variants):
            if [variant["properties"]["color"], variant["properties"]["size"]] in all_combinations:
                all_combinations.remove([variant["properties"]["color"], variant["properties"]["size"]])
                if variant["properties"]["color"] == "not supported":
                    del variant["properties"]["color"]
                if variant["properties"]["size"] == "not supported":
                    del variant["properties"]["size"]
            else:
                variants[index]["properties"] = None

        temp = []

        for variant in variants:
            if variant["properties"]:
                temp.append(variant)

        variants = temp

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