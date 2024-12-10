from django.urls import path
from .category_views import *
from django.http import HttpResponse


urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('create/', CategoryCreateView.as_view(), name='category-create'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('update-active/', CategoryActiveUpdateView.as_view(), name='category-update-active'),
    path('<int:category_id>/products/', ProductByCategoryView.as_view(), name='product-by-category'),
    path('<int:category_id>/sub-categories/', SubCategoryListView.as_view(), name='subcategory-list'),
    path('<int:category_id>/sub-categories/create/', SubCategoryCreateView.as_view(), name='subcategory-create'),
    path('import/', ImportCategoriesView.as_view(), name='import-categories'),
    path('export-selected/', ExportSelectedCategoriesView.as_view(), name='export-selected-categories'),
    path('check-name/', CheckCategoryNameView.as_view(), name='check-category-name'),
]

