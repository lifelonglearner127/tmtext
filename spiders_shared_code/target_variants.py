import json

import lxml.html


class TargetVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        try:
            variation_combinations_values = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])

            if self.tree_html.xpath("//script[@type='text/blzscript' and contains(text(), 'Target.globals.refreshItems =')]/text()"):
                stockstatus_for_variation_combinations = self.tree_html.xpath("//script[@type='text/blzscript' and contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
                start_index = stockstatus_for_variation_combinations.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
                stockstatus_for_variation_combinations = stockstatus_for_variation_combinations[start_index:]
                stockstatus_for_variation_combinations = json.loads(stockstatus_for_variation_combinations)
            else:
                return None

            hash_catentryid_to_stockstatus = {}

            for stockstatus in stockstatus_for_variation_combinations:
                hash_catentryid_to_stockstatus[stockstatus["catentry_id"]] = stockstatus["Attributes"]

            stockstatus_for_variants_list = []

            for variant_item in variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}

                attributes = variant_item["Attributes"]

                for key in attributes:
                    if key.startswith("size:"):
                        properties["size"] = key[5:]

                    if key.startswith("color:"):
                        properties["color"] = key[6:]

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["selected"] = None
                stockstatus_for_variants["price"] = float(hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["price"]["formattedOfferPrice"][1:])
                stockstatus_for_variants["image_url"] = hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["primary_image"]

                if hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["inventory"]["status"] == "in stock":
                    stockstatus_for_variants["in_stock"] = True
                else:
                    stockstatus_for_variants["in_stock"] = False

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None