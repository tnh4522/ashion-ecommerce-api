from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import Cart, CartItem, Product
from .cart_serializers import CartSerializer, CartItemSerializer, CartItemSaveSerializer


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.headers.get('X-Session-Key')
            if not session_key:
                return Response({"detail": "Session key required for guest users."}, status=status.HTTP_400_BAD_REQUEST)
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        serializer = CartSerializer(cart, context={'request': request})  # Truyền context
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.headers.get('X-Session-Key')
            if not session_key:
                return Response({"detail": "Session key required for guest users."}, status=status.HTTP_400_BAD_REQUEST)
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        data = request.data
        try:
            product = Product.objects.get(id=data['product'])
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': data.get('quantity', 1), 'size': data.get('size'), 'color': data.get('color')}
        )

        if not created:
            cart_item.quantity += int(data.get('quantity', 1))
            cart_item.save()

        serializer = CartItemSerializer(cart_item, context={'request': request})  # Truyền context
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemUpdateDeleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.delete()
            return Response({"detail": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)


class CartSaveView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.headers.get('X-Session-Key')
            if not session_key:
                return Response({"detail": "Session key required for guest users."}, status=status.HTTP_400_BAD_REQUEST)
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        # Kiểm tra payload có phải là danh sách hay không
        if not isinstance(request.data, list):
            return Response({"detail": "Payload must be a list of cart items."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartItemSaveSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_items_data = serializer.validated_data

        # Tạo một tập hợp các product IDs từ payload để dễ dàng kiểm tra
        product_ids = [item['product'].id for item in cart_items_data]

        # Xóa tất cả các CartItem hiện tại không nằm trong payload
        CartItem.objects.filter(cart=cart).exclude(product__id__in=product_ids).delete()

        for item_data in cart_items_data:
            item_id = item_data.get('id', None)
            product = item_data['product']
            quantity = item_data['quantity']
            size = item_data.get('size', None)
            color = item_data.get('color', None)

            if item_id:
                try:
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    cart_item.quantity = quantity
                    cart_item.size = size
                    cart_item.color = color
                    cart_item.save()
                except CartItem.DoesNotExist:
                    # Nếu CartItem với ID này không tồn tại, tạo mới
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity,
                        size=size,
                        color=color
                    )
            else:
                # Tạo mới CartItem nếu không có ID
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    size=size,
                    color=color
                )

        # Lấy lại giỏ hàng sau khi cập nhật
        cart = Cart.objects.get(id=cart.id)
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
