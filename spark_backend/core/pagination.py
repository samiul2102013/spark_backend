from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100


class LargePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 200
