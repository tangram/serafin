from rest_framework.filters import SearchFilter


class VariableSearchFilter(SearchFilter):

    search_param = "query"
