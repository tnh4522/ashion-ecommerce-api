from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions

from api.models import Category, Product
from api.category.categorie_serializers import *
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from api.product.product_serializers import ProductSerializer

# Category Management
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]
    model_name = 'Category'
    action = 'add'


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    # Update Category
    def get_queryset(self):
        queryset = Category.objects.all()
        sort_by = self.request.query_params.get('sort_by', 'name')
        if sort_by == 'sort_order':
            queryset = queryset.order_by('sort_order')
        else:
            queryset = queryset.order_by('name')
        return queryset


class CategoryActiveUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CategoryActiveUpdateSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data['ids']
            is_active = serializer.validated_data['is_active']
            categories = Category.objects.filter(id__in=ids)
            categories.update(is_active=is_active)
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

# Delete Category
class CategoryDeleteView(APIView):
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CategoryDeleteSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data['ids']
            categories = Category.objects.filter(id__in=ids)
            categories.delete()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryUpdateView(APIView):
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]
    def put(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductByCategoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id, *args, **kwargs):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
