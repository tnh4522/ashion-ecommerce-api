from api.address.address_serializers import AddressSerializer
from api.models import Customer, Address
import re
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'pronouns', 'address', 'phone_number', 'email', 'date_of_birth',
            'identification_number', 'social_links', 'points', 'is_active'
        ]

    def validate_phone_number(self, value):
        phone_regex = re.compile(r'^\+?1?\d{10,15}$')
        if not phone_regex.match(value):
            raise serializers.ValidationError("Invalid phone number. Please re-enter.")
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already in use.")
        return value

    def validate_identification_number(self, value):
        id_regex = re.compile(r'^\d{9}(\d{3})?$')
        if not id_regex.match(value):
            raise serializers.ValidationError("Invalid customer identification number. Please re-enter.")
        if Customer.objects.filter(identification_number=value).exists():
            raise serializers.ValidationError("The customer identification number already exists.")
        return value

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
