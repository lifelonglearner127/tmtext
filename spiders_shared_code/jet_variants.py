import json
import re

import lxml.html

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
            for variant in variants.get("map"):
            	vr = {}
            	for k, v in variant["variants"].items():
            		vr["selected"] = False
            		if default == {k: v}:
            			vr["selected"] = True
            		vr["properties"] = {k.lower(): v}
            		final_variants.append(vr)
            for variant in final_variants:
            	for attr in analytics.get("attributes"):
            		if attr.get("name") == "Color":
            			variant["color"] = attr.get("value")

            if not final_variants:
            	dc = {"properties": {}}
            	for attr in analytics.get("attributes"):
            		dc["properties"][attr.get("name", "").lower()] = \
            			attr.get("value")
            	if dc.get("properties"):
            		dc["selected"] = True
            		final_variants.append(dc)

            return final_variants or None

        except:
           return None