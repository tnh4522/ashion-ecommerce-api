from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework import generics

from api.models import Order
from api.order.order_serializers import OrderSerializer
from api.views import StandardResultsSetPagination

# List all orders
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'total_price']
    search_fields = ['order_number', 'user__username']
    ordering_fields = ['created_at', 'total_price']
    pagination_class = StandardResultsSetPagination

# Create Order
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
# Order Detail, Update, Delete
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None