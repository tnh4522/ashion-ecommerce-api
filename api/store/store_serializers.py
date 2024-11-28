from rest_framework import serializers

from api.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            'id', 'user', 'store_name', 'store_description', 'store_logo', 'rating', 'total_sales', 'joined_date',
            'is_verified', 'address', 'policies', 'return_policy', 'shipping_policy', 'seller_rating', 'phone_number',
            'email', 'social_links', 'business_hours', 'store_tags', 'location_coordinates', 'total_reviews'
        ]
        read_only_fields = ['user', 'joined_date', 'rating', 'total_sales', 'seller_rating', 'total_reviews']