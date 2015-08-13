# ~~coding=utf-8~~

from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX


is_empty = lambda x, y=None: x[0] if x else y


class AmazonBaseClass(BaseProductsSpider):

    # String from html body that means there's no results ( "no results.", for example)
    total_matches_str = 'did not match any products.'
    # Regexp for total matches to parse a number from html body ( "of ([\d,]+)", for example)
    total_matches_re = 'of ([\d,]+)'

    def _scrape_total_matches(self, response):
        """
        Overrides BaseProductsSpider method to scrape total result matches
        :param response:
        :return: Number of total matches (int)
        """

        if unicode(self.total_matches_str) in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//h2[@id="s-result-count"]/text()').re(self.total_matches_re)

            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1].replace(
                    ' ', '').replace(u'\xa0', '').replace(',', ''))
            else:
                total_matches = None

        if not total_matches:
            total_matches = int(is_empty(response.xpath(
                '//h2[@id="s-result-count"]/text()'
            ).re(FLOATING_POINT_RGEX), 0))

        return total_matches