from rest_framework import serializers

from api.address.address_serializers import AddressSerializer
from api.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'pronouns', 'address', 'phone_number', 'email', 'date_of_birth',
            'identification_number', 'social_links', 'points', 'is_active'
        ]