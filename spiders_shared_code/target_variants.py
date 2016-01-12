import json
from pprint import pprint

import lxml.html


class TargetVariants(object):

    def setupSC(self, response, debug=False):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)
        self.debug = debug

    def setupCH(self, tree_html, debug=False):
        """ Call it from CH spiders """
        self.tree_html = tree_html
        self.debug = debug

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

    def _find_between(self, s, first, last, offset=0):
        try:
            start = s.index(first, offset) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def _swatches(self):
        javascript_block = self.tree_html.xpath("//script[contains(text(), 'Target.globals.AltImagesJson')]/text()")[0]
        alt_image_json = json.loads(self._find_between(javascript_block, "Target.globals.AltImagesJson =", "\n"))
        alt_name_list = [alt_name.keys()[0] for alt_name in alt_image_json[0][alt_image_json[0].keys()[0]]["items"]]

        for index, alt in enumerate(alt_name_list):
            if index == 0:
                alt_name_list[index] = ""
            else:
                alt_name_list[index] = "_" + alt_name_list[index]

        color_name_list = self.tree_html.xpath("//*[@class='swatchtool']/img/@title")
        color_image_list = self.tree_html.xpath("//*[@class='swatchtool']/img/@src")

        color_swatches = []

        for index, color in enumerate(color_name_list):
            swatch_info = {}
            swatch_info["swatch_name"] = "color"
            swatch_info["color"] = color
            swatch_info["hero"] = len(alt_name_list)
            swatch_info["thumb"] = len(alt_name_list)
            original_image_url = color_image_list[index][:color_image_list[index].rfind("_Swatch")]
            swatch_info["hero_image"] = [original_image_url + alt + "?scl=1" for alt in alt_name_list]
            swatch_info["thumb_image"] = [original_image_url + alt + "?wid=60&hei=60&qlt=85" for alt in alt_name_list]
            color_swatches.append(swatch_info)

        if color_swatches:
            return color_swatches

        return None

    def _swap_data_for_colors(self, possible_variant_ids, stockstatus_for_variation_combinations):
        """ swap data for colors if one is missing """

        def swap_variants(data, used_part_id_color_pairs, used_part_id_color_pairs_indx):
            # find indexes to swap
            index1 = None
            index2 = None
            for _index, (_color, _part_ids) in enumerate(used_part_id_color_pairs.items()):
                if _index == used_part_id_color_pairs_indx:
                    index1 = _part_ids[0][0]
                    index2 = _part_ids[1][0]
            sv1 = data[index1]
            sv2 = data[index2]
            sv1['Attributes']['partNumber'], sv2['Attributes']['partNumber'] \
                = sv2['Attributes']['partNumber'], sv1['Attributes']['partNumber']
            sv1['catentry_id'], sv2['catentry_id'] = sv2['catentry_id'], sv1['catentry_id']
            sv1["Attributes"]["price"], sv2["Attributes"]["price"] \
                = sv2["Attributes"]["price"], sv1["Attributes"]["price"]
            # remove 1st variant which does not exist on the page
            data.remove(sv1)
            return data

        #used_combinations = []
        used_part_id_color_pairs = {}
        for i, sv in enumerate(stockstatus_for_variation_combinations):
            #combination = sv['Attributes'].get('preselect', {})
            part_id = sv['Attributes']['partNumber']
            color = sv['Attributes'].get('preselect', {}).get('var1', None)
            if color:
                if color not in used_part_id_color_pairs:
                    used_part_id_color_pairs[color] = []
                used_part_id_color_pairs[color].append((i, part_id))
        if self.debug:
            print '/'*20, used_part_id_color_pairs
        # and now when we have possible duplications - filter the data
        for indx, (color, parts) in enumerate(used_part_id_color_pairs.items()):
            if len(parts) > 1:
                stockstatus_for_variation_combinations = \
                    swap_variants(stockstatus_for_variation_combinations, used_part_id_color_pairs, indx)

        return stockstatus_for_variation_combinations

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

            stockstatus_for_variation_combinations = self._swap_data_for_colors(
                possible_variant_ids, stockstatus_for_variation_combinations)

            # this is for [future] debugging! don't remove
            if self.debug:
                print '-'*20, 'Allowed IDs:', possible_variant_ids
                for sv in stockstatus_for_variation_combinations:
                    print '*'*20, sv['catentry_id'], '-', sv['Attributes']['partNumber'], ':', \
                        sv['Attributes']["price"]["formattedOfferPrice"], '-->', \
                        sv['Attributes'].get('preselect', {}).get('var1')

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

            """
            if possible_variant_urls and not duplicated_colors_filtered:
                # variants with duplicated colors often use wrong partNumbers,
                # so we don't filter this if there were duplicated colors
                for i, _variant in enumerate(stockstatus_for_variants_list):
                    _url = _variant.get('image_url')
                    if _url and self._get_variant_id_from_image_url(_url) not in possible_variant_ids:
                        del stockstatus_for_variants_list[i]
            """

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except Exception as e:
            print str(e)
            return None