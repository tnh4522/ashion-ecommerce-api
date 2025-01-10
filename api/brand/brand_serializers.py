from rest_framework import serializers
from api.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class BrandLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand_logo']