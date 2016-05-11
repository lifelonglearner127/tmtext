import product_list.models as models
from rest_framework import serializers


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductList
        fields = ('id', 'user_id', 'name', 'crawl', 'created_at', 'is_public',
                  'with_price', 'urgent', 'is_custom_filter',
                  'crawl_frequency', 'type', 'ignore_variant_data')


class DatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Date
        fields = ('date',)


class SearchTermsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SearchTerms
        fields = ('id', 'title', 'group_id')


class SearchTermsGroupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SearchTermsGroups
        fields = ('id', 'name', 'created_at', 'enabled')


class SitesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Sites
        fields = ('id', 'name', 'url', 'image_url', 'site_type', 'results_per_page',
                  'zip_code', 'traffic_upload', 'crawler_name', 'location',
                  'user_agent')


class BrandsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Brands
        fields = ('id', 'name', 'created', 'company_id', 'brand_type', 'parent_id')
        depth = 1