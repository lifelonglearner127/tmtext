import json
import re
import lxml.html
import itertools


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
            	"jet\.\_\_variants\s+\=\s+(.*)",
            	self.tree_html.body.text_content()
            ))

            variants = json.loads(variants)

            analytics = is_empty(re.findall(
            	"jet\.core\.analytics\.raw\s+\=\s+(.*)",
            	self.tree_html.body.text_content().replace("jet.init();", "")
            ))

            try:
            	analytics = json.loads(analytics)
            except (TypeError, ValueError):
            	analytics = {}
            default = analytics.get("variants", {}).get("values") or None

            final_variants = []

            # Calculate all variants given product propierties like size, color, etc...
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

            # variants['Maps'] only have the information for the variants in_stock
            for variant in variants.get("map"):
                vr = {}
                variant_sku = variant.get("sku",None)
                if variant_sku:
                    vr['skuId'] = variant_sku
                    vr['image_url'] = is_empty(self.response.xpath('//*[@rel="%s"]//@data-zoom-image' % variant_sku).extract())
                
                vr["properties"]  = {}
                properties_as_pair_of_set = []
                for k, v in variant["variants"].items():
                    properties_as_pair_of_set.append((k,v))
                    vr["selected"] = False
                    vr["in_stock"] = True
                    if default == {k: v}:
                        vr["selected"] = True

                    vr["properties"][k.lower()] = v
                # Remove this set of propierties from the list of propierties 
                complete_list_of_propierties.remove(set(properties_as_pair_of_set))
                final_variants.append(vr)

            # The propierties left in complete_list_of_propierties are not in stock and also not in variants['Maps']
            for elem in complete_list_of_propierties:
                vr = {}
                vr["in_stock"] = False
                vr["selected"] = False
                vr["properties"]  = {}
                for propierty in list(elem):
                    vr["properties"][propierty[0].lower()] = propierty[1]
                final_variants.append(vr)


            return final_variants or None

        except:
            return None