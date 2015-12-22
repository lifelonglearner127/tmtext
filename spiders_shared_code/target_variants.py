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

    def _scrape_possible_variant_urls(self):
        """ Returns possible variants (URLs) as scraped from HTML blocks (see #3930) """
        result = []
        for li in self.tree_html.cssselect('ul.swatches li'):
            img_url = li.xpath('.//input[contains(@src, ".")]/@src')
            if img_url:
                result.append(img_url[0])
        return result

    @staticmethod
    def _get_variant_id_from_image_url(url):
        # like http://scene7.targetimg1.com/is/image/Target/10027805?wid=480&hei=480
        url = url.rsplit('/', 1)[1]
        url = url.split('?')[0]
        return url

    def _swatches(self):
        return None

    def _variants(self):
        try:
            variation_combinations_values = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])

            possible_variant_urls = self._scrape_possible_variant_urls()
            possible_variant_ids = [self._get_variant_id_from_image_url(url) for url in possible_variant_urls]

            if self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()"):
                stockstatus_for_variation_combinations = self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
                start_index = stockstatus_for_variation_combinations.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
                stockstatus_for_variation_combinations = stockstatus_for_variation_combinations[start_index:]
                stockstatus_for_variation_combinations = json.loads(stockstatus_for_variation_combinations)
            else:
                return None

            # filter out duplicated combinations
            used_combinations = []
            duplicated_combinations_filtered = False  # this flag will be used later
            for sv in stockstatus_for_variation_combinations:
                combination = sv['Attributes'].get('preselect', {})
                if combination and combination not in used_combinations:
                    used_combinations.append(combination)
                else:
                    stockstatus_for_variation_combinations.remove(sv)
                    duplicated_colors_filtered = True

            # this is for [future] debugging! don't remove
            #for sv in stockstatus_for_variation_combinations:
            #    print '*'*20, sv['catentry_id'], '-', sv['Attributes']['partNumber'], ':', \
            #        sv['Attributes']["price"]["formattedOfferPrice"], '-->', \
            #        sv['Attributes'].get('preselect', {}).get('var1')

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
                try:
                    stockstatus_for_variants["price"] = float(hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["price"]["formattedOfferPrice"][1:])
                except:
                    continue

                stockstatus_for_variants["image_url"] = hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["primary_image"]

                if hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["inventory"]["status"] == "in stock":
                    stockstatus_for_variants["in_stock"] = True
                else:
                    stockstatus_for_variants["in_stock"] = False

                stockstatus_for_variants_list.append(stockstatus_for_variants)


            if possible_variant_urls and not duplicated_colors_filtered:
                # variants with duplicated colors often use wrong partNumbers,
                # so we don't filter this if there were duplicated colors
                for i, _variant in enumerate(stockstatus_for_variants_list):
                    _url = _variant.get('image_url')
                    if _url and self._get_variant_id_from_image_url(_url) not in possible_variant_ids:
                        del stockstatus_for_variants_list[i]

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None