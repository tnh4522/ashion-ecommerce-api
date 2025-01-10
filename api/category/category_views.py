from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions
from api.models import Category, Product
from api.category.categorie_serializers import *
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from api.product.product_serializers import ProductSerializer
import json
from rest_framework.generics import CreateAPIView

class CategoryCreateView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name')

        if Category.objects.filter(name=name).exists():
            return Response(
                {"error": "Name already exists. Please use a different one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Category.objects.all()

        without_parent = self.request.query_params.get('without_parent', None)
        if without_parent == 'true':
            queryset = queryset.filter(parent__isnull=True)

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
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id, *args, **kwargs):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        subcategories = category.subcategories.all()

        if subcategories:
            products = Product.objects.filter(
                category__in=[category] + list(subcategories),
                status='ACTIVE'
            ).distinct()
        else:
            products = Product.objects.filter(
                category=category,
                status='ACTIVE'
            ).distinct()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubCategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        subcategories = category.subcategories.all().select_related('parent').order_by('name')
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class SubCategoryCreateView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def post(self, request, category_id):
        try:
            parent_category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Parent category not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['parent'] = parent_category.id
        
        sub_category_name = data.get('name', '').strip()

        if Category.objects.filter(name__iexact=sub_category_name).exists():
            return Response(
                {'error': f"Category with name '{sub_category_name}' already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ImportCategoriesView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = json.loads(request.data.get('data'))

        categories = []
        for item in data:
            parent_id = item.get('parent')
            parent = None
            if parent_id:
                parent = Category.objects.filter(id=parent_id).first()
                if not parent:
                    parent = None

            name = item.get('name')
            slug = item.get('slug')
            is_active = item.get('is_active', 'false')
            meta_title = item.get('meta_title', '')
            meta_description = item.get('meta_description', '')
            description = item.get('description', '')
            sort_order = item.get('sort_order', 0)

            category = Category(
                name=name,
                slug=slug,
                is_active=is_active,
                parent=parent,
                meta_title=meta_title,
                meta_description=meta_description,
                description=description,
                sort_order=sort_order
            )
            categories.append(category)

        Category.objects.bulk_create(categories)

        return Response({"message": "Categories imported successfully!"}, status=201)
    
class ExportSelectedCategoriesView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "No IDs provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categories = Category.objects.filter(id__in=ids)

        if not categories.exists():
            return Response(
                {"error": "No categories found with the given IDs"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CheckCategoryNameView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        name = request.query_params.get('name', '').strip()
        if not name:
            return Response(
                {'error': 'Name parameter is required.', 'available': False},
                status=status.HTTP_400_BAD_REQUEST
            )

        exists = Category.objects.filter(name__iexact=name).exists()
        return Response({'exists': exists, 'available': not exists}, status=status.HTTP_200_OK)
    
class GetCategoryIdBySlugView(APIView):
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny] 

    def get(self, request, slug, *args, **kwargs):
        try:
            category = Category.objects.only('id').get(slug=slug)
            return Response({"id": category.id}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
class LeafCategoriesWithParentView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        is_active = request.query_params.get('is_active', None)

        categories = Category.objects.filter(parent__isnull=False)

        if is_active is not None:
            is_active = bool(int(is_active))
            categories = categories.filter(is_active=is_active)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
