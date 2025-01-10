from django_filters import CharFilter, DateFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, permissions, status
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Order
from api.order.order_helper import handlePayment
from api.order.order_serializers import OrderSerializer, OrderSerializerForView
from api.utils import raise_event
from api.views import StandardResultsSetPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5  # số đơn hàng mỗi trang mặc định
    page_size_query_param = 'page_size'
    max_page_size = 50


class OrderFilter(FilterSet):
    status = CharFilter(field_name='status', lookup_expr='iexact')
    date = DateFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Order
        fields = ['status', 'date']


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


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            payment = None
            if request.data.get('payment_method') != 'COD':
                payment = handlePayment(request, serializer.data)
            response_data = serializer.data.copy()
            if payment:
                response_data['payment'] = payment
            headers = self.get_success_headers(serializer.data)

            response = Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

            user = request.user
            status_event = 'success'
            action = 'create_order'
            model_name = 'Order'
            context = f'Order ID: {serializer.data.get("id")}'
            data = {'order_details': serializer.data}

            raise_event(user, status_event, action, model_name, context, data, request)

            return response
        except Exception as e:
            user = request.user
            status_event = 'failed'
            action = 'create_order'
            model_name = 'Order'
            context = 'Creating a new order'
            data = {'error': str(e)}

            raise_event(user, status_event, action, model_name, context, data, request)

            return Response({'detail': 'An error occurred while creating the order.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailForView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializerForView
    permission_classes = [permissions.IsAuthenticated]


# Order Detail, Update, Delete
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None


class OrderByUserView(generics.ListAPIView):
    serializer_class = OrderSerializerForView
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class GetOrdersByCustomerID(ListAPIView):
    serializer_class = OrderSerializerForView
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Order.objects.filter(customer_id=customer_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data, status=status.HTTP_200_OK)

            user = request.user
            status_event = 'success'
            action = 'get_orders_by_customer_id'
            model_name = 'Order'
            context = f'Customer ID: {kwargs["customer_id"]}'
            data = {'order_count': queryset.count()}

            raise_event(user, status_event, action, model_name, context, data, request)

            return response
        except Exception as e:
            user = request.user
            status_event = 'failed'
            action = 'get_orders_by_customer_id'
            model_name = 'Order'
            context = f'Customer ID: {kwargs["customer_id"]}'
            data = {'error': str(e)}

            raise_event(user, status_event, action, model_name, context, data, request)

            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
