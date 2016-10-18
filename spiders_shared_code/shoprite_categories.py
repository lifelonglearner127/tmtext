import re
import json
import requests


class ShopriteCategoryParser:

    CATEGORIES_URL = "https://shop.shoprite.com/api/product/v5/categories/store/{store}?userId={user_id}"
    CATEGORY_URL = "https://shop.shoprite.com/api/product/v5/category/{category_id}/store/{store}/categories?userId={user_id}"

    def setupSC(self, categories, headers, store, user_id):
        """ Call it from SC spiders """
        self.categories_names = []
        self.headers = headers
        self.store = store
        self.user_id = user_id
        self._categories = categories
        self.categories = {}

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def parse_categories(self, url):
        if url:
            r = requests.get(url, headers=self.headers).content
            categories_json = json.loads(r)
            for category in categories_json:
                category_id = str(category.get('Id'))
                if category_id in self._categories:
                    category_name = category.get('Name')
                    subcategory_url = category.get('Links')[0].get('Uri') if len(category.get('Links')) > 1 else None
                    self.categories[category_id] = {'name': category_name,
                                                    'id': category_id,
                                                    'url': subcategory_url}

                    self.categories_names.append(category_name)

    def main(self):
        url = self.CATEGORIES_URL.format(store=self.store,
                                         user_id=self.user_id)
        self.parse_categories(url)
        for category in self._categories:
            url = self.categories.get(category).get('url')
            self.parse_categories(url)
        return self.categories_names
