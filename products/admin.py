from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductColor, ColorImage, Pincode, Order, OrderItem, Payment, UserOTP, UserProfile, SiteSetting, HeroBanner, FestivalBanner


class ColorImageInline(admin.TabularInline):
    model = ColorImage
    extra = 3
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;"/>', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Preview'


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 2
    fields = ['name', 'gradient_preview']
    readonly_fields = ['gradient_preview']
    
    def gradient_preview(self, obj):
        if obj.gradient:
            return format_html('<div style="width: 80px; height: 40px; background: {}; border-radius: 6px;"></div>', obj.gradient)
        return '-'
    gradient_preview.short_description = 'Color Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gradient_preview', 'product_count', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def gradient_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 8px;"/>', obj.image.url)
        return format_html('<div style="width: 100px; height: 60px; background: {}; border-radius: 8px;"></div>', obj.gradient)
    gradient_preview.short_description = 'Preview'
    
    def product_count(self, obj):
        count = obj.get_product_count()
        return format_html('<strong style="color: #48bb78;">{} products</strong>', count)
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'primary_color', 'current_price', 'discount_percent', 'rating', 'is_bestseller', 'in_stock']
    list_editable = ['is_bestseller', 'in_stock']
    list_filter = ['category', 'primary_color', 'badge_type', 'is_bestseller', 'is_active', 'in_stock']
    search_fields = ['name', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductColorInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'brand', 'description', 'primary_color')
        }),
        ('Pricing', {
            'fields': ('current_price', 'original_price', 'discount_percent', 'badge_type')
        }),
        ('Rating', {
            'fields': ('rating', 'rating_count', 'review_count')
        }),
        ('Product Details', {
            'fields': ('fabric', 'length', 'blouse_piece', 'weave_type', 'work_details', 'occasion')
        }),
        ('Display Settings', {
            'fields': ('in_stock', 'is_bestseller', 'is_active')
        }),
    )


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'gradient_preview', 'image_count']
    list_filter = ['name', 'product']
    search_fields = ['product__name', 'name']
    inlines = [ColorImageInline]
    
    def gradient_preview(self, obj):
        return format_html('<div style="width: 100px; height: 50px; background: {}; border-radius: 8px;"></div>', obj.gradient)
    gradient_preview.short_description = 'Color'
    
    def image_count(self, obj):
        count = obj.images.count()
        return format_html('<strong style="color: #48bb78;">{} images</strong>', count)
    image_count.short_description = 'Images'


@admin.register(ColorImage)
class ColorImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'color', 'order']
    list_editable = ['order']
    list_filter = ['color__product', 'color__name']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;"/>', obj.image.url)
        return 'No image'
    image_preview.short_description = 'Image'


@admin.register(Pincode)
class PincodeAdmin(admin.ModelAdmin):
    list_display = ['pincode', 'city', 'state', 'standard_delivery_days', 'express_delivery_days', 'express_delivery_charge', 'cod_available', 'is_serviceable']
    list_editable = ['standard_delivery_days', 'express_delivery_days', 'express_delivery_charge', 'cod_available', 'is_serviceable']
    list_filter = ['state', 'cod_available', 'is_serviceable']
    search_fields = ['pincode', 'city', 'state']
    
    fieldsets = (
        ('Location Details', {
            'fields': ('pincode', 'city', 'state')
        }),
        ('Delivery Settings', {
            'fields': ('standard_delivery_days', 'express_delivery_days', 'express_delivery_charge')
        }),
        ('Service Options', {
            'fields': ('cod_available', 'is_serviceable')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'color', 'quantity', 'price', 'get_total']
    can_delete = False
    
    def get_total(self, obj):
        return f'₹{obj.get_total()}'
    get_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'customer_phone', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')
        }),
        ('Price Details', {
            'fields': ('subtotal', 'discount', 'delivery_charge', 'total_amount')
        }),
        ('Delivery Details', {
            'fields': ('delivery_type', 'expected_delivery_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'color', 'quantity', 'price', 'get_total']
    list_filter = ['order__created_at']
    search_fields = ['order__order_id', 'product__name']
    
    def get_total(self, obj):
        return f'₹{obj.get_total()}'
    get_total.short_description = 'Total'


# ... Keep all existing admin code ...

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['razorpay_order_id', 'order', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['razorpay_order_id', 'razorpay_payment_id', 'order__order_id']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'amount', 'status', 'payment_method')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ... Keep all existing admin code ...

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['password', 'created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Security', {
            'fields': ('password',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'is_verified', 'is_expired_display', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email', 'otp']
    readonly_fields = ['created_at']
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">⚠ Expired</span>')
        return format_html('<span style="color: green;">✓ Valid</span>')
    is_expired_display.short_description = 'Status'



# ... Keep all existing admin code ...

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'tagline', 'email', 'phone']
    
    fieldsets = (
        ('Brand Identity', {
            'fields': ('logo', 'site_name', 'tagline')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url')
        }),
        ('Store Settings', {
            'fields': ('enable_cod', 'free_shipping_above')
        }),
    )
    
    def has_add_permission(self, request):
        # Allow only 1 instance
        if SiteSetting.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False


# ... Keep all existing admin code ...

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'order', 'is_active', 'banner_preview', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('image', 'title', 'subtitle', 'description')
        }),
        ('Call to Action Buttons', {
            'fields': ('button_text_1', 'button_link_1', 'button_text_2', 'button_link_2')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at']
    
    def banner_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: 50px; object-fit: cover; border-radius: 5px;"/>',
                obj.image.url
            )
        return "No Image"
    banner_preview.short_description = 'Preview'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# ... Keep all existing admin code ...
@admin.register(FestivalBanner)
class FestivalBannerAdmin(admin.ModelAdmin):
    list_display = ['festival_name', 'coupon_code', 'offer_percentage', 'date_range', 'is_active', 'status_display', 'image_preview']
    list_editable = ['is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['festival_name', 'coupon_code', 'title']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Festival Details', {
            'fields': ('festival_name', 'festival_tag', 'title', 'description'),
            'description': 'Basic festival information and display text'
        }),
        ('Offer Information', {
            'fields': ('offer_text_1', 'offer_percentage', 'offer_text_2', 'coupon_code'),
            'description': 'Discount details and coupon code'
        }),
        ('Visual Design', {
            'fields': ('banner_image', 'bg_color_1', 'bg_color_2'),
            'description': 'Upload image and set gradient background colors'
        }),
        ('Call to Action', {
            'fields': ('button_text', 'button_link'),
            'description': 'Button text and destination URL'
        }),
        ('Schedule & Status', {
            'fields': ('start_date', 'end_date', 'is_active'),
            'description': 'Set festival duration and active status'
        }),
    )
    
    readonly_fields = ['created_at']
    
    def date_range(self, obj):
        """Display date range"""
        return "{} - {}".format(
            obj.start_date.strftime('%d %b'),
            obj.end_date.strftime('%d %b %Y')
        )
    date_range.short_description = 'Festival Dates'
    
    def status_display(self, obj):
        """Display current status"""
        if obj.is_valid():
            return format_html(
                '<span style="background: #28a745; color: white; padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
                '● LIVE'
            )
        elif obj.is_active:
            from django.utils import timezone
            today = timezone.now().date()
            
            if obj.start_date > today:
                return format_html(
                    '<span style="background: #ffc107; color: #000; padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
                    '⏱ UPCOMING'
                )
            else:
                return format_html(
                    '<span style="background: #6c757d; color: white; padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
                    '⏱ EXPIRED'
                )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 5px 12px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
                '✕ INACTIVE'
            )
    status_display.short_description = 'Status'
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.banner_image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 70px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 2px solid #f0f0f0;"/>',
                obj.banner_image.url
            )
        return format_html('<span style="color: #999;">{}</span>', 'No Image')
    image_preview.short_description = 'Preview'
    
    def save_model(self, request, obj, form, change):
        """Custom save with validation"""
        super().save_model(request, obj, form, change)
        
        # Show message if dates are in past
        from django.utils import timezone
        from django.contrib import messages
        
        today = timezone.now().date()
        if obj.end_date < today:
            messages.warning(request, 'Festival "{}" end date is in the past. Banner will not display.'.format(obj.festival_name))
        elif obj.start_date > today:
            days_remaining = (obj.start_date - today).days
            messages.success(request, 'Festival "{}" will go live in {} days.'.format(obj.festival_name, days_remaining))
        elif obj.is_valid():
            messages.success(request, 'Festival "{}" is now LIVE on the website!'.format(obj.festival_name))
