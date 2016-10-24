import json
import re
import lxml.html
import itertools
import unicodedata

is_empty = lambda x,y=None: x[0] if x else y


class JetVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        try:
            variants = is_empty(re.findall(
                "jet\.\_\_variants\s+\=\s+(.*);",
                self.tree_html.body.text_content()
            ))

            variants = json.loads(variants)

            analytics = is_empty(re.findall(
                "jet\.core\.analytics\.raw\s+\=\s+(.*);",
                self.tree_html.body.text_content().replace("jet.init();", "")
            ))

            try:
                analytics = json.loads(analytics)

            except (TypeError, ValueError):
                analytics = {}
            default = analytics.get("variants", {}).get("values") or None

            final_variants = []

            # Calculate all variants given product propierties like size, color
            complete_list_of_propierties = []
            values = []
            for x in variants.get("values"):
                values_of_this_type = []
                value_name = x['name']
                for y in x['values']:
                    values_of_this_type.append((value_name, y))
                values.append(values_of_this_type)

            for element in itertools.product(*values):
                complete_list_of_propierties.append(set(element))

            # Product without variants
            if complete_list_of_propierties == [set([])]:
                return None

            variants_dict = {}
            # variants['Maps'] only have the info about the variants in_stock
            for variant in variants.get("map"):
                vr = {}
                variant_sku = variant.get("sku", None)
                is_selected = variant_sku and variant_sku in self.response.url
                vr["selected"] = True if is_selected else False

                if variant_sku:
                    vr['skuId'] = variant_sku
                    vr['image_url'] = is_empty(self.response.xpath(
                        '//*[@rel="%s"]//@data-zoom-image' % variant_sku
                    ).extract())

                vr["properties"] = {}
                properties_as_pair_of_set = []
                for k, v in variant["variants"].items():
                    properties_as_pair_of_set.append((k, v))
                    vr["in_stock"] = True
                    if default == {k: v}:
                        vr["selected"] = True

                    vr["properties"][k.lower()] = v
                # Remove this set of propierties from the list of propierties

                variants_by_property = variants_dict.get(
                    str(set(properties_as_pair_of_set)), [])
                variants_by_property.append(vr)
                variants_dict[
                    str(set(properties_as_pair_of_set))] = variants_by_property

                try:
                    complete_list_of_propierties.remove(
                        set(properties_as_pair_of_set))
                except:
                    pass

            # There is a bug on the webpage, if 2 products has the same variant
            # Only the one pre-selected is displayed
            for _property in variants_dict.keys():
                variants_by_property = variants_dict[_property]
                if len(variants_by_property) > 1:
                    variants_by_property = filter((lambda x: x['selected']),
                                                  variants_by_property)
                final_variants.append(variants_by_property[0])

            # The propierties left in complete_list_of_propierties are not in
            # stock and also not in variants['Maps']
            for elem in complete_list_of_propierties:
                vr = {}
                vr["in_stock"] = False
                vr["selected"] = False
                vr["properties"] = {}
                for propierty in list(elem):
                    vr["properties"][propierty[0].lower()] = propierty[1]
                final_variants.append(vr)

            return final_variants or None

        except:
            return None

    def _variants_v2(self):
        # New layout
        try:
            data = json.loads(self.response.body)
        except:
            return None
        variants = []
        prod_data = data.get('result')

        other_variants = prod_data.get('productVariations', [])
        if other_variants:
            # Default variant is added only if there are other variants
            other_variants.append(prod_data)
        for variant in other_variants:
            sku = variant.get('retailSkuId')
            prod_name = variant.get('title')
            prod_slug = self.slugify(prod_name)
            url = "https://jet.com/product/{}/{}".format(prod_slug, sku)

            props = {}
            attributes = variant.get('attributes', [])
            for attribute in attributes:
                props[attribute.get("name")] = attribute.get("value")

            image_url = variant.get('images')
            image_url = image_url[0].get('raw') if image_url else None

            # Only default variant have price
            # additional requests needed to fill other variants prices
            price = variant.get('productPrice', {}).get("referencePrice")
            selected = True if price else False

            variants.append({
                "sku": variant.get("retailSkuId"),
                "selected": selected,
                "upc": variant.get("upc"),
                "title": prod_name,
                "url": url,
                "properties": props,
                "price": price,
                "image_url": image_url
            })
        return variants

    @staticmethod
    def slugify(value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        # Removed .lower() for this website
        value = re.sub('[^\w\s-]', '', value).strip()
        return re.sub('[-\s]+', '-', value)
