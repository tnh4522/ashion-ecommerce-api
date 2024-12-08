from rest_framework import serializers

from api.address.address_serializers import AddressSerializer
from api.models import Customer, Address


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'pronouns', 'address', 'phone_number', 'email', 'date_of_birth',
            'identification_number', 'social_links', 'points', 'is_active'
        ]

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        customer = Customer.objects.create(**validated_data)

        if address_data:
            address = Address.objects.create(**address_data)
            customer.address = address
            customer.save()

        return customer

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if address_data:
            address = instance.address
            for attr, value in address_data.items():
                setattr(address, attr, value)
            address.save()

        instance.save()

        return instance
