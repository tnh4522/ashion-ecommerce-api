from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Permission(models.Model):
    model_name = models.CharField(max_length=50)
    action = models.CharField(
        max_length=10,
        choices=[('view', 'View'), ('add', 'Add'), ('change', 'Change'), ('delete', 'Delete')],
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('model_name', 'action')

    def __str__(self):
        return f"{self.action.capitalize()} {self.model_name}"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, related_name='permissions', on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, related_name='roles', on_delete=models.CASCADE)
    allowed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        status = "Granted" if self.allowed else "Denied"
        return f"{status} {self.permission} to {self.role}"


class User(AbstractUser):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )
    role = models.ForeignKey(Role, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    individual_permissions = models.ManyToManyField(
        Permission, through='UserPermission', related_name='users_with_permissions', blank=True
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    preferences = models.JSONField(blank=True, null=True)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    def has_permission(self, model_name, action):
        if UserPermission.objects.filter(
            user=self, permission__model_name=model_name, permission__action=action, allowed=True
        ).exists():
            return True

        if self.role and RolePermission.objects.filter(
            role=self.role, permission__model_name=model_name, permission__action=action, allowed=True
        ).exists():
            return True

        return False


class UserPermission(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_specific_permissions',
        on_delete=models.CASCADE
    )
    permission = models.ForeignKey(
        Permission,
        related_name='user_permissions',
        on_delete=models.CASCADE
    )
    allowed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'permission')

    def __str__(self):
        status = "Granted" if self.allowed else "Denied"
        return f"{status} {self.permission} to {self.user.username}"


# Address model with additional fields
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('SHIPPING', 'Shipping'),
        ('BILLING', 'Billing'),
    )
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey('Customer', related_name='addresses', on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Vietnam')
    default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='SHIPPING')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name}, {self.street_address}"


# Category model with additional fields
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', related_name='subcategories', on_delete=models.CASCADE, blank=True, null=True
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# Tag model for product tagging
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# Product model with additional fields
class Product(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DRAFT', 'Draft'),
    )
    user = models.ForeignKey(
        User,
        related_name='products',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    material = models.CharField(max_length=255, blank=True)
    care_instructions = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.SET_NULL, null=True
    )
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_sale_date = models.DateTimeField(null=True, blank=True)
    end_sale_date = models.DateTimeField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    sizes = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated sizes, e.g., S,M,L,XL"
    )
    colors = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated colors, e.g., Red,Blue,Green"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    num_reviews = models.PositiveIntegerField(default=0)
    quantity_sold = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # For SEO purposes
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# ProductImage model with additional fields
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image of {self.product.name}"


# Cart and CartItem models with additional fields
class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    # For anonymous users
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_saved_for_later = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# Wishlist and WishlistItem models
class Wishlist(models.Model):
    user = models.OneToOneField(User, related_name='wishlist', on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist of {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"


# Order and OrderItem models with additional fields
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
        ('PAYPAL', 'PayPal'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED', 'Canceled'),
        ('RETURNED', 'Returned'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    )
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    subtotal_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_orders', on_delete=models.SET_NULL, null=True
    )
    billing_address = models.ForeignKey(
        Address, related_name='billing_orders', on_delete=models.SET_NULL, null=True
    )
    shipping_method = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    coupon = models.ForeignKey(
        'Coupon', related_name='orders', on_delete=models.SET_NULL, null=True, blank=True
    )
    loyalty_points_used = models.PositiveIntegerField(default=0)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For multi-vendor scenarios, remove 'seller' from Order

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super(Order, self).save(*args, **kwargs)

    def generate_order_number(self):
        return timezone.now().strftime('%Y%m%d%H%M%S') + str(self.user.id)


class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED', 'Canceled'),
        ('RETURNED', 'Returned'),
    )
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User,
        related_name='order_items',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'SELLER'},
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# Review and ReviewImage models with additional fields
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.SET_NULL, null=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField()
    images = models.ManyToManyField('ReviewImage', related_name='reviews', blank=True)
    video_url = models.URLField(blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    reported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Removed seller field as it can be accessed via product

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"


class ReviewImage(models.Model):
    image = models.ImageField(upload_to='review_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


# Coupon model with additional fields
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
        ('FREE_SHIPPING', 'Free Shipping'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=0, help_text='0 for unlimited')
    per_user_limit = models.PositiveIntegerField(default=0, help_text='0 for unlimited')
    used_count = models.PositiveIntegerField(default=0)
    applicable_categories = models.ManyToManyField(Category, related_name='coupons', blank=True)
    applicable_products = models.ManyToManyField(Product, related_name='coupons', blank=True)
    applicable_users = models.ManyToManyField(User, related_name='coupons', blank=True)
    is_free_shipping = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self, user=None):
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        if user and self.per_user_limit:
            user_usage = Order.objects.filter(user=user, coupon=self).count()
            if user_usage >= self.per_user_limit:
                return False
        return True


# LoyaltyPoint model with additional fields
class LoyaltyPoint(models.Model):
    user = models.OneToOneField(User, related_name='loyalty_points', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    total_earned = models.PositiveIntegerField(default=0)
    total_spent = models.PositiveIntegerField(default=0)
    level = models.CharField(max_length=50, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"


# Transaction model with additional fields
class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
        ('REFUNDED', 'Refunded'),
    )
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway_response = models.JSONField(blank=True, null=True)
    currency = models.CharField(max_length=10, default='VND')
    description = models.TextField(blank=True)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"


# Message and MessageThread models with additional fields
class MessageThread(models.Model):
    participants = models.ManyToManyField(User, related_name='message_threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participant_usernames = ', '.join([user.username for user in self.participants.all()])
        return f"Thread between {participant_usernames}"


class Message(models.Model):
    thread = models.ForeignKey(
        MessageThread, related_name='messages', on_delete=models.CASCADE, blank=True, null=True
    )
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User, related_name='received_messages', on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, related_name='messages', on_delete=models.CASCADE, blank=True, null=True
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


# Promotion model with additional fields
class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
        ('FREE_SHIPPING', 'Free Shipping'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='promotion_images/', blank=True, null=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    products = models.ManyToManyField(Product, related_name='promotions', blank=True)
    applicable_categories = models.ManyToManyField(
        Category, related_name='promotions', blank=True
    )
    coupon_code = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# Notification model with additional fields
class Notification(models.Model):
    SENT_VIA_CHOICES = (
        ('APP', 'In-App'),
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
    )
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    link = models.URLField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    sent_via = models.CharField(max_length=20, choices=SENT_VIA_CHOICES, default='APP')
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


# ReturnRequest model for handling returns and refunds
class ReturnRequest(models.Model):
    RETURN_REASON_CHOICES = (
        ('DAMAGED', 'Damaged Product'),
        ('NOT_AS_DESCRIBED', 'Not as Described'),
        ('WRONG_ITEM', 'Wrong Item Sent'),
        ('OTHER', 'Other'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
        ('COMPLETED', 'Completed'),
    )
    user = models.ForeignKey(User, related_name='return_requests', on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        OrderItem, related_name='return_requests', on_delete=models.CASCADE
    )
    reason = models.CharField(max_length=50, choices=RETURN_REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Return request by {self.user.username} for {self.order_item.product.name}"


# ShippingMethod model
class ShippingMethod(models.Model):
    name = models.CharField(max_length=255)
    carrier = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_delivery_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# PaymentMethod model for storing user's payment methods
class PaymentMethod(models.Model):
    user = models.ForeignKey(User, related_name='payment_methods', on_delete=models.CASCADE)
    METHOD_TYPE_CHOICES = (
        ('CREDIT_CARD', 'Credit Card'),
        ('BANK_ACCOUNT', 'Bank Account'),
        ('PAYPAL', 'PayPal'),
    )
    method_type = models.CharField(max_length=50, choices=METHOD_TYPE_CHOICES)
    provider = models.CharField(max_length=50)
    account_number = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        masked_account = '*' * (len(self.account_number) - 4) + self.account_number[-4:]
        return f"{self.method_type} ending with {masked_account} for {self.user.username}"


# SellerProfile model with additional fields
class SellerProfile(models.Model):
    user = models.OneToOneField(
        User,
        related_name='seller_profile',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'SELLER'},
    )
    store_name = models.CharField(max_length=255)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sales = models.PositiveIntegerField(default=0)
    joined_date = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    address = models.ForeignKey(
        Address, related_name='seller_profiles', on_delete=models.SET_NULL, null=True, blank=True
    )
    policies = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    shipping_policy = models.TextField(blank=True)
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.store_name


# ActivityLog model for tracking user activities
class ActivityLog(models.Model):
    user = models.ForeignKey(User, related_name='activity_logs', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    model = models.CharField(max_length=50)
    context = models.TextField(blank=True)
    data = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.created_at}"


class Stock(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    location = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StockProduct(models.Model):
    stock = models.ForeignKey(Stock, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='stocks', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stock of {self.product.name} - {self.quantity} items"


# Store Model
class Store(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='stores')
    store_name = models.CharField(max_length=255)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sales = models.PositiveIntegerField(default=0)
    joined_date = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    policies = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    shipping_policy = models.TextField(blank=True)
    seller_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)  # Store social media links as JSON
    business_hours = models.JSONField(blank=True, null=True)  # Store business hours as JSON
    store_tags = models.CharField(max_length=255, blank=True)  # Tags to classify the store
    location_coordinates = models.CharField(max_length=100, blank=True, null=True)  # Geolocation coordinates
    total_reviews = models.PositiveIntegerField(default=0)  # Number of reviews

    def __str__(self):
        return self.store_name


# Brand Model
class Brand(models.Model):
    brand_name = models.CharField(max_length=255)
    brand_description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    brand_logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.brand_name


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
    address = models.ForeignKey(Address, related_name='customers', on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, help_text="YYYY-MM-DD")
    identification_number = models.CharField(max_length=20, blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    points = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer with email {self.email}"