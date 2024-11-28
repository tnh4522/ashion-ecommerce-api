from rest_framework import generics, permissions

from api.address.address_serializers import AddressSerializer
from api.models import Address


class AddressCreateView(generics.CreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Address'
    # action = 'add'


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Address'
    # action = 'add'


# Address list view
class AddressListView(generics.ListAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.AllowAny]
    

# class AddressListView(generics.ListAPIView):
#     serializer_class = AddressSerializer
#     permission_classes = [permissions.AllowAny]
    
#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         return Address.objects.filter(user_id=user_id)
