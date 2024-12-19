from rest_framework import generics, permissions
from ..models import StockVariant
from .variant_serializers import StockVariantSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .variant_serializers import StockVariantUpdateSerializer
from django.db import transaction

class StockVariantUpdateView(generics.UpdateAPIView):
    queryset = StockVariant.objects.all()
    serializer_class = StockVariantSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] 

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        response = super().update(request, *args, **kwargs)
        return response
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class StockVariantDestroyView(generics.DestroyAPIView):
    queryset = StockVariant.objects.all()
    serializer_class = StockVariantSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UpdateStockVariantsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def put(self, request, format=None):

        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Invalid data format. Expected a list of objects."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = StockVariantUpdateSerializer(data=data, many=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    for item in serializer.validated_data:
                        variant = StockVariant.objects.get(id=item['id'])
                        variant.quantity = item['quantity']
                        variant.save()
                return Response({"detail": "StockVariants updated successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
