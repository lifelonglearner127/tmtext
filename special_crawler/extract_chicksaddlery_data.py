from lxml import html, etree

from extract_data import Scraper

class ChicksaddleryScraper(Scraper):
    """Implements methods that each extract an individual piece of data for chicksaddlery.com
    """

    # ! may throw exception if not found
    def _product_name(self):
        """Extracts product name from heading tag on product page
        Returns:
            string containing product name
        """
        return self.tree_html.xpath("//h1/text()")[0].strip()

    # ! may throw exception if not found
    def _page_title(self):
        """Extracts page title
        Returns:
            string containing page title
        """

        return self.tree_html.xpath("//title/text()")[0].strip()

    # ! may throw exception if not found
    def _model(self):
        """Extracts product model (or "product code" as this site calls it)
        Returns:
            string containing model
        """

        return self.tree_html.xpath("""//td[@id='main-content']
            /div[starts-with(@class, 'product-details')]/div[@class='product-code']/span
            /text()""")[0].strip()

    # TODO: test on more examples
    def _features(self):
        """Extracts product features
        Returns:
            string containing product features (separated by newlines)
            or None if not found
        """

        features = "".join(self.tree_html.xpath("//h2[text()='Features']/following-sibling::li/text()"))
        if features:
            return features
        else:
            return None

    def _feature_count(self):
        """Extracts number of features
        Returns:
            int representing number of features
        """

        return len(self.tree_html.xpath("//h2[text()='Features']/following-sibling::li"))

    def _description(self):
        """Extracts product description text
        Returns:
            string containing product description
            or None if description not found or empty
        """

        # TODO: This aims to only extract the first part of the description.
        #       Does it do it correctly for many examples?
        description_node = self.tree_html.xpath(\
            "//div[@class='product-description']/text()[normalize-space()!=''] | " + \
            "//div[@class='product-description']/h4//text()[normalize-space()!='']"
            )

        description_text = "".join(description_node).strip()

        if description_text:
            return description_text
        else:
            return None

    def _long_description(self):
        """Extracts product long description text
        Returns:
            string containing product long description
            or None if description not found or empty
        """

        description_node = self.tree_html.xpath(\
            "//div[@class='product-description']/p/text()[normalize-space()!='']" \
            )

        description_text = "".join(description_node).strip()

        if description_text:
            return description_text
        else:
            return None

    DATA_TYPES = {
        "product_name" : _product_name, \
        "product_title" : _product_name, \
        "title_seo" : _page_title, \
        "model" : _model, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
    }