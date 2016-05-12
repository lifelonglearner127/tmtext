import re

from django.db import connection
from rest_framework import viewsets, filters
from rest_framework.response import Response

from product_list.models import ProductList, Sites, SearchTerms, ProductListResultsSummary, SearchTermsBrandsRelation, RankingSearchResultsItemsSummary, GroupsSites, Date, Brands, SearchTermsGroups
from product_list.serializers import ProductListSerializer, DatesSerializer, SearchTermsSerializer, SitesSerializer, BrandsSerializer, SearchTermsGroupsSerializer
from product_list.exceptions import ParamsCombinationError, FormatParseError, ParamNotSupportedError


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
        date = request.query_params.get('date', None)
        waiting = request.query_params.get('waiting', None)

        # Check if date format is "YYYY-MM-DD"
        if date and not re.match('^\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|1\d|2\d|3[0-1])$', date):
            raise FormatParseError()

        # Check if more than 1 param from the this have been set
        if len(filter(None, [product_list_id, search_term_id, search_term_group_id])) > 1:
            raise ParamsCombinationError()

        sql_query = None

        if product_list_id:
            # Product List ID and Date
            if date:
                sql_query = """
                            select distinct s.* from sites s
                            join product_list_results_summary plrs on plrs.site_id = s.id
                            where s.site_type = 1 and plrs.product_list_id = PROD_LIST_ID and plrs.date = DATE
                            """.format(product_list_id=product_list_id, date=date)

                raise ParamNotSupportedError('Date filter for Search Term '
                                             'Id is not implemented yet')
            # Product List ID
            else:
                sql_query = """
                        select distinct s.* from sites s
                        join product_list_results_summary plrs on plrs.site_id = s.id
                        where s.site_type = 1 and plrs.product_list_id = {product_list_id};
                        """.format(product_list_id=product_list_id)

        if search_term_id:
            # Search Term ID and Date
            if date:
                raise ParamNotSupportedError('Date filter for Search Term '
                                             'Id is not implemented yet')

            # Search Term ID
            else:
                sql_query = """
                            select s.* from sites s
                            join groups_sites gs on gs.site_id = s.id
                            join search_terms st on st.group_id = gs.group_id
                            where s.site_type = 1 and st.id = {search_term_id};
                            """.format(search_term_id=search_term_id)

        if search_term_group_id:
            # Search Term Group ID and Date
            if waiting:
                # For a given search term group, tell which sites are currently set to be crawled
                sql_query = """
                    select s.* from sites s
                    join groups_sites gs on gs.site_id = s.id
                    where s.site_type = 1 and gs.group_id = {search_term_group_id};
                    """.format(search_term_group_id=search_term_group_id)

            elif date:
                # For a given search term group, tell which sites were crawled on a given date
                sql_query = """
                            select distinct s.* from sites s
                            join ranking_search_results_items_summary rsris on rsris.site_id = s.id
                            join search_terms_brands_relation stbr on stbr.id = rsris.search_items_brands_relation_id
                            join search_terms st on st.id = stbr.search_term_id
                            where st.group_id = {search_term_group_id} and rsris.date_of_upload = {date};
                            """.format(search_term_group_id=search_term_group_id, date=date)
            else:
                # Search Term Group ID
                sql_query = """
                            select distinct s.* from sites s
                            join ranking_search_results_items_summary rsris on rsris.site_id = s.id
                            join search_terms_brands_relation stbr on stbr.id = rsris.search_items_brands_relation_id
                            join search_terms st on st.id = stbr.search_term_id
                            where st.group_id = {search_term_group_id};
                            """.format(search_term_group_id=search_term_group_id)

        if sql_query:
            sites_ids = [x.id for x in Sites.objects.raw(sql_query)]
            return Sites.objects.filter(id__in=sites_ids)

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

        # Check if more than 1 param from the this have been set
        if len(filter(None, [product_list_id, search_term_id])) > 1:
            raise ParamsCombinationError()

        sql_query = None

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
            brand_ids = [x.id for x in Brands.objects.raw(sql_query)]
            return Brands.objects.filter(id__in=brand_ids)

        return Brands.objects.all()


class DateViewSet(viewsets.ModelViewSet):
    serializer_class = DatesSerializer
    http_method_names = ['get']

    def get_queryset(self):
        request = self.request
        product_list_id = request.query_params.get('product_list_id', None)
        search_term_id = request.query_params.get('search_term_id', None)
        search_term_group_id = request.query_params.get('search_term_group_id', None)
        brand_id = request.query_params.get('brand_id', None)
        site_id = request.query_params.get('site_id', None)
        last_time = 'last_time' in request.query_params

        sql_query = ""

        # Check if more than 1 param from the this have been set
        if len(filter(None, [product_list_id, search_term_id, search_term_group_id])) > 1:
            raise ParamsCombinationError()

        if product_list_id:
            if last_time:
                sql_query = """
                            select max(plrs.date) as date from product_list_results_summary plrs
                            where plrs.product_list_id = {product_list_id};
                            """.format(product_list_id=product_list_id)

            elif brand_id and site_id:
                sql_query = """
                        select plrs.date as date from product_list_results_summary plrs
                        where product_list_id = {product_list_id} and
                        plrs.site_id = {site_id} and plrs.brand_id = {brand_id};
                        """.format(product_list_id=product_list_id,
                                   brand_id=brand_id,
                                   site_id=site_id)

            else:
                sql_query = """
                            select distinct plrs.date as date from product_list_results_summary plrs
                            where plrs.product_list_id = {product_list_id} order by date desc;
                            """.format(product_list_id=product_list_id)

        if search_term_group_id:
            if last_time:
                sql_query = """
                            select max(rsris.date_of_upload) as date from ranking_search_results_items_summary rsris
                            join search_terms_brands_relation stbr on stbr.id = rsris.search_items_brands_relation_id
                            join search_terms st on st.id = stbr.search_term_id
                            where st.group_id = {search_term_group_id};
                            """.format(search_term_group_id=search_term_group_id)
            else:
                sql_query = """
                            select distinct rsris.date_of_upload as date from ranking_search_results_items_summary rsris
                            join search_terms_brands_relation stbr on stbr.id = rsris.search_items_brands_relation_id
                            join search_terms st on st.id = stbr.search_term_id
                            where st.group_id = {search_term_group_id} order by date desc;
                            """.format(search_term_group_id=search_term_group_id)

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
