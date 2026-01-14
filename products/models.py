from django.db import models

class Category(models.Model):
    CATEGORY_IMAGES = {
        'Silk Sarees': 'linear-gradient(135deg, #C41E3A 0%, #8B0000 100%)',
        'Designer Kurtis': 'linear-gradient(135deg, #4B0082 0%, #8B008B 100%)',
        'Bridal Lehengas': 'linear-gradient(135deg, #D4AF37 0%, #FFD700 100%)',
        'Ethnic Sets': 'linear-gradient(135deg, #2E8B57 0%, #3CB371 100%)',
    }
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    gradient = models.CharField(max_length=200, editable=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
    
    def save(self, *args, **kwargs):
        self.gradient = self.CATEGORY_IMAGES.get(self.name, 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    BADGE_CHOICES = [
        ('discount', 'Discount'),
        ('bestseller', 'Bestseller'),
        ('new', 'New'),
    ]
    
    PRIMARY_COLOR_CHOICES = [
        ('Red', 'Red'),
        ('Gold', 'Gold'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Purple', 'Purple'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Maroon', 'Maroon'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=100, default='Manovastra')
    description = models.TextField(blank=True)
    primary_color = models.CharField(max_length=50, choices=PRIMARY_COLOR_CHOICES, default='Red')
    
    # Pricing
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    
    # Rating
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    rating_count = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)
    
    # Badge
    badge_type = models.CharField(max_length=20, choices=BADGE_CHOICES, default='discount')
    
    # Product Details
    fabric = models.CharField(max_length=100, default='Pure Silk')
    length = models.CharField(max_length=50, default='5.5 meters')
    blouse_piece = models.CharField(max_length=100, default='Included (0.8 meters)')
    weave_type = models.CharField(max_length=100, default='Handloom')
    work_details = models.CharField(max_length=200, default='Zari Work')
    occasion = models.CharField(max_length=200, default='Wedding, Festival')
    
    # Stock & Display
    in_stock = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_badge_text(self):
        if self.badge_type == 'bestseller':
            return 'Bestseller'
        elif self.badge_type == 'new':
            return 'New'
        else:
            return f'{self.discount_percent}% OFF'
    
    def get_occasions_list(self):
        return [o.strip() for o in self.occasion.split(',')]


class ProductColor(models.Model):
    COLOR_CHOICES = [
        ('Royal Red', 'Royal Red'),
        ('Golden Yellow', 'Golden Yellow'),
        ('Royal Purple', 'Royal Purple'),
        ('Emerald Green', 'Emerald Green'),
        ('Royal Blue', 'Royal Blue'),
        ('Pink Blush', 'Pink Blush'),
        ('Maroon', 'Maroon'),
        ('Navy Blue', 'Navy Blue'),
        ('Orange', 'Orange'),
        ('Black', 'Black'),
    ]
    
    COLOR_GRADIENTS = {
        'Royal Red': 'linear-gradient(135deg, #C41E3A 0%, #8B0000 100%)',
        'Golden Yellow': 'linear-gradient(135deg, #D4AF37 0%, #FFD700 100%)',
        'Royal Purple': 'linear-gradient(135deg, #4B0082 0%, #8B008B 100%)',
        'Emerald Green': 'linear-gradient(135deg, #2E8B57 0%, #3CB371 100%)',
        'Royal Blue': 'linear-gradient(135deg, #00008B 0%, #4169E1 100%)',
        'Pink Blush': 'linear-gradient(135deg, #FF69B4 0%, #FFB6C1 100%)',
        'Maroon': 'linear-gradient(135deg, #800000 0%, #B22222 100%)',
        'Navy Blue': 'linear-gradient(135deg, #000080 0%, #1E90FF 100%)',
        'Orange': 'linear-gradient(135deg, #FF8C00 0%, #FFA500 100%)',
        'Black': 'linear-gradient(135deg, #000000 0%, #434343 100%)',
    }
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=50, choices=COLOR_CHOICES)
    gradient = models.CharField(max_length=200, editable=False)
    
    def save(self, *args, **kwargs):
        self.gradient = self.COLOR_GRADIENTS.get(self.name, 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product.name} - {self.name}'


class ColorImage(models.Model):
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.color.name} - Image {self.order}'


class Pincode(models.Model):
    pincode = models.CharField(max_length=6, unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    standard_delivery_days = models.IntegerField(default=5)
    express_delivery_days = models.IntegerField(default=2)
    express_delivery_charge = models.DecimalField(max_digits=6, decimal_places=2, default=99)
    cod_available = models.BooleanField(default=True)
    is_serviceable = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.pincode} - {self.city}, {self.state}"
    
    class Meta:
        ordering = ['pincode']


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Address
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery
    delivery_type = models.CharField(max_length=20, default='standard')
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            import string
            self.order_id = 'MAN' + ''.join(random.choices(string.digits, k=10))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self):
        return self.price * self.quantity


# ... Keep all existing models ...

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']


# ... Keep all existing models ...

class UserOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.email} - {self.otp}"
    
    def is_expired(self):
        from django.utils import timezone
        from django.conf import settings
        expiry_time = timezone.now() - timezone.timedelta(minutes=settings.OTP_EXPIRY_TIME)
        return self.created_at < expiry_time
    
    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=200)  # Hashed password
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    class Meta:
        ordering = ['-created_at']


# ... Keep all existing models ...

class SiteSetting(models.Model):
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    site_name = models.CharField(max_length=100, default='Manovastra')
    tagline = models.CharField(max_length=200, default='Elegance Redefined')
    email = models.EmailField(default='info@manovastra.com')
    phone = models.CharField(max_length=15, default='+91 98765 43210')
    address = models.TextField(default='Bangalore, Karnataka, India')
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Settings
    enable_cod = models.BooleanField(default=True)
    free_shipping_above = models.DecimalField(max_digits=10, decimal_places=2, default=999)
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'


# ... Keep all existing models ...

class HeroBanner(models.Model):
    title = models.CharField(max_length=200, help_text="Main title")
    subtitle = models.CharField(max_length=200, help_text="Top subtitle text")
    description = models.TextField(help_text="Banner description")
    image = models.ImageField(upload_to='banners/', help_text="Banner image (1920x600px recommended)")
    button_text_1 = models.CharField(max_length=50, default="Shop Now")
    button_link_1 = models.CharField(max_length=200, help_text="First button link (e.g., /category/sarees/)")
    button_text_2 = models.CharField(max_length=50, default="Explore", blank=True)
    button_link_2 = models.CharField(max_length=200, blank=True, help_text="Second button link (optional)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Hero Banner'
        verbose_name_plural = 'Hero Banners'



# ... Keep all existing models ...

class FestivalBanner(models.Model):
    festival_name = models.CharField(max_length=200, help_text="Festival name (e.g., Makar Sankranti)")
    festival_tag = models.CharField(max_length=100, help_text="Tag line with emoji (e.g., 🪔 Festival Special)")
    title = models.CharField(max_length=200, help_text="Main title")
    description = models.TextField(help_text="Short description")
    
    # Offer Details
    offer_text_1 = models.CharField(max_length=50, default="UPTO", help_text="First offer text")
    offer_percentage = models.CharField(max_length=10, default="50%", help_text="Discount percentage")
    offer_text_2 = models.CharField(max_length=50, default="OFF", help_text="Second offer text")
    coupon_code = models.CharField(max_length=50, help_text="Coupon code (e.g., SANKRANTI50)")
    
    # Image & Link
    banner_image = models.ImageField(upload_to='festival_banners/', help_text="Festival banner image (800x600px)")
    button_text = models.CharField(max_length=100, default="Shop Festival Collection")
    button_link = models.CharField(max_length=200, default="/offers/", help_text="Button link URL")
    
    # Background Colors
    bg_color_1 = models.CharField(max_length=7, default="#FF6B6B", help_text="Background gradient color 1 (hex)")
    bg_color_2 = models.CharField(max_length=7, default="#FFE66D", help_text="Background gradient color 2 (hex)")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Show on homepage")
    start_date = models.DateField(help_text="Festival start date")
    end_date = models.DateField(help_text="Festival end date")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.festival_name
    
    def is_valid(self):
        """Check if festival is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Festival Banner'
        verbose_name_plural = 'Festival Banners'
