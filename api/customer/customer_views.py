from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework import generics, permissions
from rest_framework.response import Response

from api.address.address_serializers import AddressSerializer
from api.customer.customer_serializers import CustomerSerializer
from api.models import Customer


class CustomerManagerView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Customer'
    # action = 'view'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['email', 'phone_number', 'first_name', 'last_name', 'is_active']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    ordering_fields = ['email', 'created_at', 'first_name', 'last_name']

    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         self.permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    #         self.action = 'add'
    #     return super(CustomerManagerView, self).get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'customer': serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_data = self.get_serializer(instance).data

        if instance.address:
            customer_data['address'] = AddressSerializer(instance.address).data

        return Response(customer_data)
