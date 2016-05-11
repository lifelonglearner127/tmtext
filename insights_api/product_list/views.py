from django.db import connection
from rest_framework import viewsets, filters, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from product_list.models import ProductList, Sites, SearchTerms, \
    ProductListResultsSummary, GroupsSites, Date, Brands, SearchTermsGroups

from product_list.serializers import ProductListSerializer, DatesSerializer, \
    SearchTermsSerializer, SitesSerializer, BrandsSerializer, \
    SearchTermsGroupsSerializer


# ViewSets define the view behavior.
class ProductListViewSet(viewsets.ModelViewSet):
    queryset = ProductList.objects.all()
    serializer_class = ProductListSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'user_id', 'name', 'crawl', 'created_at', 'is_public',
                     'with_price', 'urgent', 'is_custom_filter',
                     'crawl_frequency', 'type', 'ignore_variant_data')


class SearchTermsViewSet(viewsets.ModelViewSet):
    queryset = SearchTerms.objects.all()
    serializer_class = SearchTermsSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'title', 'group_id')


class SearchTermsGroupsViewSet(viewsets.ModelViewSet):
    queryset = SearchTermsGroups.objects.all()
    serializer_class = SearchTermsGroupsSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'name', 'created_at', 'enabled')


# ViewSets define the view behavior.
class SitesViewSet(viewsets.ModelViewSet):
    serializer_class = SitesSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'name', 'url', 'image_url', 'site_type', 'results_per_page',
                     'zip_code', 'traffic_upload', 'crawler_name', 'location',
                     'user_agent')

    def get_queryset(self):
        request = self.request
        product_list_id = request.query_params.get('product_list_id', None)
        search_term_id = request.query_params.get('search_term_id', None)
        search_term_group_id = request.query_params.get('search_term_group_id', None)

        if product_list_id:
            sites_ids = ProductListResultsSummary.objects.values_list(
                'site', flat=True).filter(product_list=product_list_id).distinct()
            site_type = request.query_params.get('site_type', 1)
            return Sites.objects.filter(
                id__in=sites_ids, site_type=site_type).all()

        elif search_term_id or search_term_group_id:
            group_id = search_term_group_id or SearchTerms.objects.values_list(
                'group_id', flat=True).filter(pk=search_term_id)

            sites_ids = GroupsSites.objects.values_list(
                'site_id', flat=True).filter(group_id=group_id).distinct()
            return Sites.objects.filter(id__in=sites_ids, site_type=1)

        return Sites.objects.all()


class BrandsViewSet(viewsets.ModelViewSet):
    serializer_class = BrandsSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'name', 'created', 'company_id', 'brand_type', 'parent_id')

    def get_queryset(self):
        request = self.request
        product_list_id = request.query_params.get('product_list_id', None)
        search_term_id = request.query_params.get('search_term_id', None)
        site_id = request.query_params.get('site_id', None)

        sql_query = ""

        if product_list_id and site_id:
            sql_query = """
                    select distinct rb.* from ranking_brands rb
                    join product_list_results_summary plrs on plrs.brand_id = rb.id
                    where plrs.product_list_id = {product_list_id} and plrs.site_id = {site_id};
                    """.format(product_list_id=product_list_id,
                               site_id=site_id)

        elif search_term_id and site_id:
            sql_query = """
                    select distinct rb.* from ranking_brands rb
                    join search_terms_brands_relation stbr on stbr.brand_id = rb.id
                    join ranking_search_results_items_summary rsris on rsris.search_items_brands_relation_id = stbr.id
                    where stbr.search_term_id = {search_term_id} and rsris.site_id = {site_id};
                    """.format(search_term_id=search_term_id,
                               site_id=site_id)

        if sql_query:
            return list(Brands.objects.raw(sql_query))

        return Brands.objects.all()


class DateViewSet(viewsets.ViewSet):
    serializer_class = DatesSerializer
    http_method_names = ['get']

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('date')


    def get_queryset(self):
        request = self.request
        product_list_id = request.query_params.get('product_list_id', None)
        search_term_id = request.query_params.get('search_term_id', None)
        brand_id = request.query_params.get('brand_id', None)
        site_id = request.query_params.get('site_id', None)
        sql_query = ""
        if product_list_id and brand_id and site_id:
            sql_query = """
                    select plrs.date as date from product_list_results_summary plrs
                    where product_list_id = {product_list_id} and
                        plrs.site_id = {site_id} and plrs.brand_id = {brand_id};
                    """.format(product_list_id=product_list_id,
                               brand_id=brand_id,
                               site_id=site_id)

        elif search_term_id and brand_id and site_id:
            sql_query = """
                    select rsris.date_of_upload as date from ranking_search_results_items_summary rsris
                    join search_terms_brands_relation stbr on stbr.brand_id = rsris.search_items_brands_relation_id
                    where stbr.search_term_id = {search_term_id} and rsris.site_id = {site_id} and stbr.brand_id = {brand_id};
                    """.format(search_term_id=search_term_id,
                               brand_id=brand_id,
                               site_id=site_id)

        if sql_query:
            cursor = connection.cursor()
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


    def list(self, request):
        query_set = self.get_queryset()
        if query_set is not None:
            serializer = DatesSerializer(query_set, many=True)
            return Response(serializer.data)

        return Response({"detail": "Obligatory param is missing. "
                         "Please, make sure that you are including the followings"
                         " params: brand_id, site_id and, product_list_id or "
                         "search_term_id"}, status=400)
