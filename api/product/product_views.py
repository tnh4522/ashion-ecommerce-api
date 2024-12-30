# product_views.py
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from rest_framework import filters as drf_filters, status, permissions
from rest_framework.response import Response
from rest_framework import generics
from api.models import Product, OrderItem
from api.product.product_serializers import ProductSerializer
from api.views import StandardResultsSetPagination
from .recommendation_serializer import ProductRecommendationSerializer
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView


class ProductRecommendationView(generics.ListAPIView):
    serializer_class = ProductRecommendationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)

        queryset = Product.objects.filter(
            Q(sale_price__isnull=True),
            Q(status='ACTIVE'),
        )

        queryset = queryset.exclude(
            id__in=OrderItem.objects.filter(
                order__created_at__gte=one_day_ago
            ).values_list('product_id', flat=True)
        )

        # queryset = queryset.filter(
        #     Q(created_at__lte=one_week_ago) &
        #     Q(updated_at__lte=one_week_ago)
        # )

        return queryset

class ProductFilter(FilterSet):
    price__gte = NumberFilter(field_name="price", lookup_expr='gte')
    price__lte = NumberFilter(field_name="price", lookup_expr='lte')
    category__name = CharFilter(field_name='category__name', lookup_expr='icontains')
    status = CharFilter(field_name='status', lookup_expr='exact')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    name_exact = CharFilter(field_name='name', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['category__name', 'price', 'status', 'name', 'name_exact']

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name']
    ordering_fields = ['price', 'name', 'stock', 'status', 'category__name']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        category_names = request.query_params.getlist('category__name', [])
        name_exact = request.query_params.get('name_exact', None)
        search = request.query_params.get('search', None)

        if category_names:
            queryset = queryset.filter(category__name__in=category_names).distinct()

        if name_exact:
            queryset = queryset.filter(name__iexact=name_exact)
        elif search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'INACTIVE'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class GenerateProductImageView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Chỉ admin mới được phép

    def generate_unique_slug(self, name):
        base_slug = slugify(name)
        slug = base_slug
        num = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        return slug

    def post(self, request, format=None):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"detail": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_featured=True)  # Kiểm tra is_featured=True
        except Product.DoesNotExist:
            return Response({"detail": "Featured product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Tạo prompt từ dữ liệu sản phẩm
        prompt = f"{product.name}. {product.description}"

        # Đường dẫn đến ảnh nền mặc định
        default_background_path = os.path.join(settings.MEDIA_ROOT, 'backgrounds', 'default_bg.png')
        if not os.path.exists(default_background_path):
            return Response({"detail": "Default background image not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Tạo ảnh
        generated_image_path = generate_product_image(prompt, default_background_path)
        if not generated_image_path:
            return Response({"detail": "Image generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Lưu ảnh đã tạo vào sản phẩm mới
        try:
            with open(generated_image_path, 'rb') as img_file:
                django_file = File(img_file)
                unique_slug = self.generate_unique_slug(product.name)
                new_product = Product.objects.create(
                    user=request.user,
                    name=product.name,
                    slug=unique_slug,
                    sku=product.sku,  # Đảm bảo SKU là duy nhất nếu cần
                    barcode=product.barcode,
                    brand=product.brand,
                    description=product.description,
                    material=product.material,
                    care_instructions=product.care_instructions,
                    category=product.category,
                    price=product.price,
                    sale_price=product.sale_price,
                    start_sale_date=product.start_sale_date,
                    end_sale_date=product.end_sale_date,
                    stock=product.stock,
                    weight=product.weight,
                    dimensions=product.dimensions,
                    sizes=product.sizes,
                    colors=product.colors,
                    status='DRAFT',  # Mặc định là DRAFT
                    is_featured=product.is_featured,
                    is_new_arrival=product.is_new_arrival,
                    is_on_sale=product.is_on_sale,
                    video_url=product.video_url,
                    meta_title=product.meta_title,
                    meta_description=product.meta_description,
                )
                # Sao chép các tag
                new_product.tags.set(product.tags.all())

                # Lưu ảnh chính
                new_product.main_image.save(
                    f'generated_{os.path.basename(generated_image_path)}',
                    ContentFile(django_file.read()),
                    save=True
                )
        except Exception as e:
            print(f"Error saving generated image: {e}")
            return Response({"detail": "Failed to save generated image."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Xóa ảnh tạm thời
        try:
            os.remove(generated_image_path)
        except:
            pass

        serializer = ProductSerializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)