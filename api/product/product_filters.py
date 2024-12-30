# products/filters.py

import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name_exact = django_filters.CharFilter(field_name='name', lookup_expr='exact')
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = {
            'name_exact': ['exact'],
            'search': ['icontains'],
            'categories__name': ['in'],
            'status': ['exact'],
            'price__gte': ['exact', 'gte'],
            'price__lte': ['exact', 'lte'],
        }
