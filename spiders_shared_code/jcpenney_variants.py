import json

import lxml.html
import itertools
import re
from lxml import html, etree

is_empty = lambda x, y=None: x[0] if x else y

class JcpenneyVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def generate_image_url(self, image_id):
        main_part = "http://s7d2.scene7.com/is/image/JCPenney/{id}?wid={wid}&"\
            "hei={hei}&fmt={fmt}"
        wid = 350
        hei = 350
        fmt = "jpg"
        return main_part.format(id=image_id, wid=wid, hei=hei, fmt=fmt)

    def _variants(self):
        try:
            canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]
            product_id = re.search('prod\.jump\?ppId=(.+?)$', canonical_link).group(1)
            variation_key_list = []
            variation_values_list = []
            stockstatus_list_by_variation = []
            stockstatus_for_variants_list = []

            images_list = []
            for img in self.tree_html.xpath(
                    "//ul[contains(@class, 'small_swatches')]/li"):
                prev_list = {}
                prev_list["img"] = is_empty(img.xpath(
                    "a/@onclick"), "")
                prev_list["img"] = is_empty(re.findall(
                    "\'([^\']*)\'\)", prev_list["img"]))
                if len(prev_list["img"]) < 10 or \
                        re.search("pp\d+", prev_list["img"]):
                    prev_list["img"] = is_empty(
                        re.findall(
                            "imageName\s+\=\s+\"([^\"]*)", 
                            html.tostring(self.tree_html)
                        ),
                        ""
                    )
                    prev_list["img"] = is_empty(prev_list["img"].split(","))
                prev_list["img"] = self.generate_image_url(prev_list["img"])
                prev_list["color"] = is_empty(img.xpath(
                    "div[1]/p/text() |"
                    "a/img/@alt"
                ))
                if prev_list:
                    images_list.append(prev_list)
            
            #lot attribute
            lot_list = self.tree_html.xpath("//ul[@id='" + product_id + "Lot']//li[not(@class='displayNone')]/a/@title")
            lot_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "Lot']//li[not(@class='displayNone')]")

            if lot_li_list:
                stockstatus_list = []

                for lot_li in lot_li_list:
                    if "class" in lot_li.attrib:
                        stockstatus_list.append(lot_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("lot")
                variation_values_list.append(lot_list)
                stockstatus_list_by_variation.append(dict(zip(lot_list, stockstatus_list)))

            #size attribute
            size_list = self.tree_html.xpath("//ul[@id='" + product_id + "SIZE']//li[@id='size']/a/@title")
            size_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "SIZE']//li[@id='size']")

            if size_list:
                stockstatus_list = []

                for size_li in size_li_list:
                    if "class" in size_li.attrib:
                        stockstatus_list.append(size_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("size")
                variation_values_list.append(size_list)
                stockstatus_list_by_variation.append(dict(zip(size_list, stockstatus_list)))

            #length attribute
            length_list = self.tree_html.xpath("//ul[@id='" + product_id + "LENGTH']//li[@id='length']/a/@title")
            length_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "LENGTH']//li[@id='length']")

            if length_list:
                stockstatus_list = []

                for length_li in length_li_list:
                    if "class" in length_li.attrib:
                        stockstatus_list.append(length_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("length")
                variation_values_list.append(length_list)
                stockstatus_list_by_variation.append(dict(zip(length_list, stockstatus_list)))

            #chest attribute
            chest_list = self.tree_html.xpath("//ul[@id='" + product_id + "CHEST']//li[@id='chest']/a/@title")
            chest_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "CHEST']//li[@id='chest']")

            if chest_list:
                stockstatus_list = []

                for chest_li in chest_li_list:
                    if "class" in chest_li.attrib:
                        stockstatus_list.append(chest_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("chest")
                variation_values_list.append(chest_list)
                stockstatus_list_by_variation.append(dict(zip(chest_list, stockstatus_list)))

            #waist attribute
            waist_list = self.tree_html.xpath("//ul[@id='" + product_id + "WAIST']//li[@id='waist']/a/@title")
            waist_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "WAIST']//li[@id='waist']")

            if waist_list:
                stockstatus_list = []

                for waist_li in waist_li_list:
                    if "class" in waist_li:
                        stockstatus_list.append(waist_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("waist")
                variation_values_list.append(waist_list)
                stockstatus_list_by_variation.append(dict(zip(waist_list, stockstatus_list)))

            #inseam attribute
            inseam_list = self.tree_html.xpath("//ul[@id='" + product_id + "INSEAM']//li[@id='inseam']/a/@title")
            inseam_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "INSEAM']//li[@id='inseam']")

            if inseam_list:
                stockstatus_list = []

                for inseam_li in inseam_li_list:
                    if "class" in inseam_li:
                        stockstatus_list.append(inseam_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("inseam")
                variation_values_list.append(inseam_list)
                stockstatus_list_by_variation.append(dict(zip(inseam_list, stockstatus_list)))

            #neck attribute
            neck_list = self.tree_html.xpath("//ul[@id='" + product_id + "NECK_SIZE']//li[@id='neck size']/a/@title")
            neck_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "NECK_SIZE']//li[@id='neck size']")

            if neck_list:
                stockstatus_list = []

                for neck_li in neck_li_list:
                    if "class" in neck_li:
                        stockstatus_list.append(neck_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("neck")
                variation_values_list.append(neck_list)
                stockstatus_list_by_variation.append(dict(zip(neck_list, stockstatus_list)))

            #sleeve attribute
            sleeve_list = self.tree_html.xpath("//ul[@id='" + product_id + "SLEEVE']//li[@id='sleeve']/a/@title")
            sleeve_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "SLEEVE']//li[@id='sleeve']")

            if sleeve_list:
                stockstatus_list = []

                for sleeve_li in sleeve_li_list:
                    if "class" in sleeve_li:
                        stockstatus_list.append(sleeve_li.attrib["class"])
                    else:
                        stockstatus_list.append("")

                variation_key_list.append("sleeve")
                variation_values_list.append(sleeve_list)
                stockstatus_list_by_variation.append(dict(zip(sleeve_list, stockstatus_list)))

            #color attribute
            product_id = re.search('prod\.jump\?ppId=(.+?)$', self.tree_html.xpath("//link[@rel='canonical']/@href")[0]).group(1)
            color_list = self.tree_html.xpath("//ul[@id='" + product_id + "COLOR']//li[contains(@id, '" + product_id + "')]/a/img/@alt")
            visible_color_list = []
            color_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "COLOR']//li[contains(@id, '" + product_id + "')]")

            if color_list:
                stockstatus_list = []

                for index, color_li in enumerate(color_li_list):
                    if "showColor('{0}','{1}',".format(product_id, color_list[index]) in html.tostring(self.tree_html):
                        visible_color_list.append(color_list[index])
                        if "class" in color_li:
                            stockstatus_list.append(color_li.attrib["class"])
                        else:
                            stockstatus_list.append("")

                variation_key_list.append("color")
                variation_values_list.append(visible_color_list)
                stockstatus_list_by_variation.append(dict(zip(visible_color_list, stockstatus_list)))

            variation_combinations_values = list(itertools.product(*variation_values_list))

            variation_combinations_values = map(list, variation_combinations_values)

            price_json= re.search('var jcpPPJSON = (.+?);\njcpDLjcp\.productPresentation = jcpPPJSON;', html.tostring(self.tree_html)).group(1)
            self.price_json = json.loads(price_json)
            price = self.price_json["price"]

            if float(price).is_integer():
                price = int(price)

            for variation_combination in variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                stockstatus = True

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[index]

                    if stockstatus is True and stockstatus_list_by_variation[index][variation_combination[index]] in ["sku_not_available", "sku_illegal"]:
                        stockstatus = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = None

                if len(variation_combinations_values) == 1:
                    stockstatus_for_variants["selected"] = True
                else:
                    stockstatus_for_variants["selected"] = False

                stockstatus_for_variants["price"] = price

                color = stockstatus_for_variants.get(
                    "properties", {}).get("color")
                for img in images_list:
                    if color == img.get("color"):
                        stockstatus_for_variants["image_url"] = img.get("img")

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except Exception, e:
            return None
