import json

import lxml.html


class WalmartVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        try:
            if getattr(self, 'response', None):
                # SC spiders sometimes fail to perform correct conversion
                # response.body -> lxml.html tree -> tostring
                page_raw_text = self.response.body
            else:
                page_raw_text = lxml.html.tostring(self.tree_html)

            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)

            variation_key_values_by_attributes = {}

            for variation_attribute in json_body:
                variation_key_values = {}
                variation_attribute_id = variation_attribute["id"]

                if "variants" in variation_attribute:
                    for variation in variation_attribute["variants"]:
                        variation_key_values[variation["id"]] = variation["name"]

                variation_key_values_by_attributes[variation_attribute_id] = variation_key_values

            selected_variants = {}

            for item in json_body:
                if "variants" in item:
                    selected_variants[item["id"]] = item["selectedValue"]

            startIndex = page_raw_text.find('"variantProducts":') + len('"variantProducts":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"primaryProductId":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]

            color_size_stockstatus_json_body = json.loads(json_text)
            stockstatus_for_variants_list = []

            original_product_canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

            if not original_product_canonical_link.startswith("http://www.walmart.com"):
                original_product_canonical_link = "http://www.walmart.com" + original_product_canonical_link

            for item in color_size_stockstatus_json_body:
                variants = item["variants"]
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True

                for key in variants:
                    if key in variation_key_values_by_attributes:
                        if key == "actual_color":
                            properties["color"] = variation_key_values_by_attributes[key][variants[key]["id"]]
                        else:
                            properties[key] = variation_key_values_by_attributes[key][variants[key]["id"]]

                        if selected_variants[key] != variation_key_values_by_attributes[key][variants[key]["id"]]:
                            isSelected = False

                variant_product_id = item['buyingOptions']['usItemId']
                variant_product_url = original_product_canonical_link[:original_product_canonical_link.rfind("/") + 1] + str(variant_product_id)
                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = item['buyingOptions']['available']
                stockstatus_for_variants["url"] = variant_product_url
                stockstatus_for_variants["price"] = None
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None
