# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from __future__ import division, absolute_import, unicode_literals


class AddCalculatedFields(object):

    @staticmethod
    def process_item(product, spider):
        search_term = product['search_term'].lower()
        title = product['title'].lower()

        product['search_term_in_title_exactly'] = search_term in title

        product['search_term_in_title_partial'] = any(
            word in title for word in search_term.split())

        return product
