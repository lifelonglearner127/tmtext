import re

import json
from pprint import pprint

import lxml.html
import requests

class TargetVariants(object):

    def setupSC(self, response, zip_code='94117', item_info=None, selected_tcin=None, debug=False):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)
        self.item_info = item_info
        self.selected_tcin = selected_tcin
        self.zip_code = zip_code
        self.debug = debug

    def setupCH(self, tree_html, zip_code='94117', item_info=None, selected_tcin=None, debug=False):
        """ Call it from CH spiders """
        self.tree_html = tree_html
        self.item_info = item_info
        self.selected_tcin = selected_tcin
        self.debug = debug

        self.zip_code = zip_code
        self.location_id = None

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
        if self.item_info:
            swatches = []

            for child in self.item_info['item']['child_items']:
                s = {
                    'hero_image': [],
                }

                for attribute in child['variation']:
                    s[attribute] = child['variation'][attribute]

                images = child['enrichment']['images'][0]

                if images.get('swatch'):
                    s['hero_image'] = [images['base_url'] + images['swatch']]

                s['hero'] = len(s['hero_image'])

                swatches.append(s)

            if swatches:
                return swatches

            return None

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
            color = sv['Attributes'].get('preselect', {}).get('var1', '')
            size = sv['Attributes'].get('preselect', {}).get('var2', '')
            var3 = sv['Attributes'].get('preselect', {}).get('var3', '')  # wtf is var3?
            if color:
                if color+'|'+size+'|'+var3 not in used_part_id_color_pairs:
                    used_part_id_color_pairs[color+'|'+size+'|'+var3] = []
                used_part_id_color_pairs[color+'|'+size+'|'+var3].append((i, part_id))
        if self.debug:
            print '/'*20, used_part_id_color_pairs
        # and now when we have possible duplications - filter the data
        for indx, (color, parts) in enumerate(used_part_id_color_pairs.items()):
            if len(parts) > 1:
                stockstatus_for_variation_combinations = \
                    swap_variants(stockstatus_for_variation_combinations, used_part_id_color_pairs, indx)

        return stockstatus_for_variation_combinations

    def _availability_info(self, variants):

        url = 'https://api.target.com/available_to_promise_aggregator/v1?key=adaptive-pdp&request_type=availability'

        payload = { 'products': [] }

        for item in variants:
            payload['products'].append(
                {
                    'request_line_id': 1,
                    'product': {
                        'product_id': str(item['partNumber']),
                        'multichannel_option': 'none',
                        'location_ids': str(self.location_id),
                        'inventory_type': 'stores',
                        'requested_quantity': '1',
                        'field_groups': 'location_summary'
                  }
                }
            )

        if not payload['products']:
            return

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'en-US,en;q=0.8,ja;q=0.6,vi;q=0.4,es;q=0.2,fr;q=0.2,zh-CN;q=0.2,zh;q=0.2,pt;q=0.2',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'api.target.com',
            'Origin': 'http://www.target.com',
            'Pragma': 'no-cache',
            'Referer': self.item_info['dynamicKitURL'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'
        }
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            # TODO: url http://www.target.com/p/mid-rise-straight-leg-jeans-curvy-fit-black-mossimo/-/A-15545812 fails

            return response.json()['products']
        except:
            print 'ERROR getting avilability info! '# + response.text

    def _extract_location_id(self, product_id):
        " extract location id to use it in stock status checking "

        url = 'https://api.target.com/available_to_promise/v2/%s/search?nearby=%s&requested_quantity=1&inventory_type=stores&radius=100&multichannel_option=none&field_groups=location_summary&key=q0jGNkIyuqUTYIlzZKoCfK6ugaNGSP8h' % (product_id, self.zip_code)

        headers = {
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'en-US,en;q=0.8,ja;q=0.6,vi;q=0.4,es;q=0.2,fr;q=0.2,zh-CN;q=0.2,zh;q=0.2,pt;q=0.2',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.target.com',
            'Origin': 'http://www.target.com',
            'Pragma': 'no-cache',
            'Referer': self.item_info['dynamicKitURL'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        try:
            return response.json()['products'][0]['locations'][0]['location_id']
        except Exception as e:
            print str(e)
            return ''

    def _variants(self):
        if self.item_info:
            variants = []

            '''
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'
            }
            page_raw_text = requests.get(self.item_info['dynamicKitURL'], headers=headers).content
            # decides if users can see "get it in 4-7 business days"
            refresh_items = {}
            match = re.search(r'refreshItems = (.*?)\s*</script>', page_raw_text)
            if match:
                data = json.loads(match.group(1).strip())
                for item in data:
                    refresh_items[item['Attributes']['partNumber']] = item['Attributes']['callToActionDetail']['shipToStoreEligible']

            if not getattr(self, 'location_id', None):
                if self.item_info['SKUs']:
                    self.location_id = self._extract_location_id(self.item_info['SKUs'][0]['partNumber'])
                else:
                    self.location_id = None

            availability_info = {}
            items = self._availability_info(self.item_info['SKUs'])
            for item in items if items else []:
                product_id = item['products'][0]['product_id']

                try:
                    availability_info[product_id] = [refresh_items[product_id]]  # TODO: this fails sometimes, wrapped in exception but not sure it's what we need
                except KeyError:
                    continue

                if 'locations' in item['products'][0]:
                    status = False
                    try:
                        status = True if item['products'][0]['locations'][0][
                                             'availability_status'] == 'IN_STOCK' else False
                        availability_info[product_id].append(status)
                    except (KeyError, IndexError):
                        availability_info[product_id] = [status]
            '''

            for child in self.item_info['item']['child_items']:
                v = {
                    'in_stock' : False,
                    'price': child['price']['offerPrice']['price'],
                    'properties' : {},
                    'image_url' : None,
                    'selected' : child['tcin'] == self.selected_tcin,
                    'upc': child['upc'],
                    'dpci': child['dpci'],
                    'tcin': child['tcin'],
                }

                v['in_stock'] = child['available_to_promise_network']['availability_status'] != 'OUT_OF_STOCK'

                for attribute in child['variation']:
                    v['properties'][attribute] = child['variation'][attribute]

                images = child['enrichment']['images'][0]
                v['image_url'] = images['base_url'] + images['primary']

                variants.append(v)

            if variants:
                return variants

            return None

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

            # this is for [future] debugging! don't remove
            if self.debug:
                print '-'*20, 'Allowed IDs:', possible_variant_ids
                for sv in stockstatus_for_variation_combinations:
                    print '*'*20, sv['catentry_id'], '-', sv['Attributes']['partNumber'], ':', \
                        sv['Attributes']["price"]["formattedOfferPrice"], '-->', \
                        sv['Attributes'].get('preselect', {}).get('var1'), \
                        sv['Attributes'].get('preselect', {}).get('var2'), \
                        sv['Attributes'].get('preselect', {}).get('var3')

            stockstatus_for_variation_combinations = self._swap_data_for_colors(
                possible_variant_ids, stockstatus_for_variation_combinations)

            # this is for [future] debugging! don't remove
            if self.debug:
                for sv in stockstatus_for_variation_combinations:
                    print '#'*20, sv['catentry_id'], '-', sv['Attributes']['partNumber'], ':', \
                        sv['Attributes']["price"]["formattedOfferPrice"], '-->', \
                        sv['Attributes'].get('preselect', {}).get('var1'), \
                        sv['Attributes'].get('preselect', {}).get('var2'), \
                        sv['Attributes'].get('preselect', {}).get('var2')

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
                    if hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["price"]["formattedOfferPrice"] == "Too low to display":
                        stockstatus_for_variants["price"] = None
                    else:
                        stockstatus_for_variants["price"] = float(hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["price"]["formattedOfferPrice"][1:])
                except:
                    continue

                stockstatus_for_variants["image_url"] = hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["primary_image"]

                if self.debug:
                    print '----- STOCK STATUS:', hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["inventory"]
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
