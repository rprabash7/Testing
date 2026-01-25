from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from .models import *
    

# ✅ Customize Admin Site (SECURE)
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', "Manovastra Secure Admin")
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', "Manovastra Admin Portal")
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', "Welcome to Manovastra Admin")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'product_count_display')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    def product_count_display(self, obj):
        """Show product count for category with color"""
        count = obj.get_product_count()
        color = '#10b981' if count > 0 else '#ef4444'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px;">{} product{}</span>',
            color,
            count,
            's' if count != 1 else ''
        )
    product_count_display.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'brand', 
        'display_prices',
        'display_rating', 
        'rating_count',
        'in_stock', 
        'is_bestseller', 
        'is_active'
    )
    list_filter = (
        'category', 
        'is_active', 
        'is_bestseller', 
        'in_stock', 
        'badge_type', 
        'primary_color'
    )
    search_fields = ('name', 'brand', 'fabric', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('discount_percent', 'display_rating_detail', 'discount_amount_display')
    list_editable = ('is_active', 'is_bestseller')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'category', 
                'name', 
                'slug', 
                'brand', 
                'description', 
                'primary_color'
            )
        }),
        ('Pricing & Discount', {
            'fields': (
                ('original_price', 'current_price'),
                ('discount_percent', 'discount_amount_display'),
            ),
            'description': '💡 Discount percentage is auto-calculated based on prices'
        }),
        ('Rating & Reviews', {
            'fields': (
                ('rating', 'rating_count', 'review_count'),
                'display_rating_detail',
            )
        }),
        ('Badge & Labels', {
            'fields': (
                'badge_type',
                'is_bestseller',
            )
        }),
        ('Product Details', {
            'fields': (
                'fabric', 
                'length', 
                'blouse_piece', 
                'weave_type', 
                'work_details', 
                'occasion'
            )
        }),
        ('Stock Status', {
            'fields': (
                'in_stock', 
                'is_active'
            )
        }),
    )
    
    def display_prices(self, obj):
        """Display prices with discount percentage"""
        current = float(obj.current_price)
        original = float(obj.original_price)
        discount = int(obj.discount_percent)
        
        if discount > 0:
            return format_html(
                '<div style="line-height: 1.8;">'
                '<strong style="color: #10b981; font-size: 15px;">₹{}</strong><br>'
                '<span style="text-decoration: line-through; color: #999; font-size: 12px;">₹{}</span> '
                '<span style="background: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}% OFF</span>'
                '</div>',
                current,
                original,
                discount
            )
        return format_html(
            '<strong style="color: #10b981; font-size: 15px;">₹{}</strong>',
            current
        )
    display_prices.short_description = '💰 Price & Discount'
    
    def display_rating(self, obj):
        """Display rating as stars in admin list"""
        full_stars = int(obj.rating)
        half_star = 1 if (float(obj.rating) - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars_html = '★' * full_stars
        if half_star:
            stars_html += '⯨'
        stars_html += '☆' * empty_stars
        
        # Color based on rating
        rating_val = float(obj.rating)
        if rating_val >= 4.5:
            color = '#10b981'
        elif rating_val >= 4.0:
            color = '#fbbf24'
        elif rating_val >= 3.0:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        rating_text = '{:.1f}'.format(rating_val)
        
        return format_html(
            '<div style="color: {}; font-size: 18px; letter-spacing: 2px; line-height: 1.5;">'
            '{} <span style="color: #666; font-size: 12px; font-weight: bold;">({})</span>'
            '</div>',
            color,
            stars_html,
            rating_text
        )
    display_rating.short_description = '⭐ Rating'
    
    def display_rating_detail(self, obj):
        """Display detailed rating breakdown in product detail"""
        full_stars = int(obj.rating)
        half_star = 1 if (float(obj.rating) - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars_html = '<span style="color: #fbbf24; font-size: 28px; letter-spacing: 3px;">'
        stars_html += '★' * full_stars
        if half_star:
            stars_html += '⯨'
        stars_html += '</span>'
        stars_html += '<span style="color: #d1d5db; font-size: 28px; letter-spacing: 3px;">'
        stars_html += '☆' * empty_stars
        stars_html += '</span>'
        
        rating_val = float(obj.rating)
        rating_text = '{:.1f}'.format(rating_val)
        count = int(obj.rating_count)
        plural = 's' if count != 1 else ''
        
        return format_html(
            '<div style="padding: 20px; background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%); '
            'border-radius: 12px; border: 2px solid #e5e7eb; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">'
            '<div style="margin-bottom: 15px; text-align: center;">{}</div>'
            '<div style="font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 8px; text-align: center;">'
            '{} out of 5</div>'
            '<div style="color: #6b7280; text-align: center; margin-bottom: 20px;">'
            'Based on <strong>{}</strong> review{}</div>'
            '<div style="margin-top: 15px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e5e7eb;">'
            '<strong style="font-size: 14px; color: #374151; display: block; margin-bottom: 12px;">📊 Rating Distribution:</strong>'
            '<div style="line-height: 2;">'
            '<div>5★: <span style="color: #10b981; font-size: 18px;">●●●●●</span> <span style="color: #10b981; font-weight: bold;">Excellent</span></div>'
            '<div>4★: <span style="color: #84cc16; font-size: 18px;">●●●●○</span> <span style="color: #84cc16; font-weight: bold;">Very Good</span></div>'
            '<div>3★: <span style="color: #f59e0b; font-size: 18px;">●●●○○</span> <span style="color: #f59e0b; font-weight: bold;">Good</span></div>'
            '<div>2★: <span style="color: #f97316; font-size: 18px;">●●○○○</span> <span style="color: #f97316; font-weight: bold;">Fair</span></div>'
            '<div>1★: <span style="color: #ef4444; font-size: 18px;">●○○○○</span> <span style="color: #ef4444; font-weight: bold;">Poor</span></div>'
            '</div></div></div>',
            stars_html,
            rating_text,
            count,
            plural
        )
    display_rating_detail.short_description = '⭐ Rating Overview'
    
    def discount_amount_display(self, obj):
        """Show discount amount in rupees"""
        if obj.discount_percent > 0:
            amount = float(obj.original_price) - float(obj.current_price)
            return format_html(
                '<div style="background: linear-gradient(135deg, #10b981, #059669); color: white; '
                'padding: 8px 15px; border-radius: 8px; display: inline-block; font-weight: bold; '
                'font-size: 14px; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);">'
                '💰 ₹{} saved'
                '</div>',
                int(amount)
            )
        return format_html('<span style="color: #9ca3af; font-style: italic;">{}</span>', 'No discount')
    discount_amount_display.short_description = '💸 You Save'
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure discount calculation"""
        super().save_model(request, obj, form, change)
    
    # Custom Bulk Actions
    actions = [
        'mark_as_bestseller', 
        'mark_as_not_bestseller', 
        'mark_in_stock', 
        'mark_out_of_stock', 
        'activate_products', 
        'deactivate_products'
    ]
    
    def mark_as_bestseller(self, request, queryset):
        updated = queryset.update(is_bestseller=True)
        self.message_user(request, f'{updated} product(s) marked as Bestseller.')
    mark_as_bestseller.short_description = "⭐ Mark selected as Bestseller"
    
    def mark_as_not_bestseller(self, request, queryset):
        updated = queryset.update(is_bestseller=False)
        self.message_user(request, f'{updated} product(s) removed from Bestseller.')
    mark_as_not_bestseller.short_description = "❌ Remove Bestseller status"
    
    def mark_in_stock(self, request, queryset):
        updated = queryset.update(in_stock=True)
        self.message_user(request, f'{updated} product(s) marked as In Stock.')
    mark_in_stock.short_description = "✅ Mark as In Stock"
    
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(in_stock=False)
        self.message_user(request, f'{updated} product(s) marked as Out of Stock.')
    mark_out_of_stock.short_description = "⛔ Mark as Out of Stock"
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} product(s) activated.')
    activate_products.short_description = "🟢 Activate selected products"
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} product(s) deactivated.')
    deactivate_products.short_description = "🔴 Deactivate selected products"


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'color_preview', 'image_count')
    list_filter = ('name',)
    search_fields = ('product__name',)
    readonly_fields = ('gradient', 'color_preview')
    
    def color_preview(self, obj):
        """Show color gradient preview"""
        return format_html(
            '<div style="width: 100px; height: 30px; background: {}; border-radius: 6px; border: 1px solid #ddd;"></div>',
            obj.gradient
        )
    color_preview.short_description = 'Color Preview'
    
    def image_count(self, obj):
        """Show number of images"""
        count = obj.images.count()
        return format_html(
            '<span style="background: #3b82f6; color: white; padding: 3px 10px; border-radius: 10px; font-size: 12px;">{} image{}</span>',
            count,
            's' if count != 1 else ''
        )
    image_count.short_description = 'Images'


@admin.register(ColorImage)
class ColorImageAdmin(admin.ModelAdmin):
    list_display = ('color', 'order', 'image_preview')
    list_filter = ('color__product',)
    ordering = ('color', 'order')
    
    def image_preview(self, obj):
        """Show image thumbnail"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 6px; border: 2px solid #e5e7eb;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(Pincode)
class PincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'city', 'state', 'is_serviceable', 'cod_available', 'express_delivery_charge')
    list_filter = ('is_serviceable', 'cod_available', 'state')
    search_fields = ('pincode', 'city', 'state')
    list_editable = ('is_serviceable', 'cod_available')
    ordering = ('pincode',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'color', 'quantity', 'price', 'get_total')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'customer_email', 'status', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'payment_method', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount', 'delivery_charge', 'total_amount')
        }),
        ('Delivery', {
            'fields': ('delivery_type', 'expected_delivery_date')
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'razorpay_order_id', 'razorpay_payment_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'order__order_id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'is_verified', 'is_expired')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('logo', 'site_name', 'tagline', 'about_text')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'whatsapp', 'address', 'working_hours')
        }),
        ('Social Media', {
            'fields': ('instagram_url', 'youtube_url', 'whatsapp_url', 'facebook_url', 'twitter_url')
        }),
        ('Navigation Links - Company', {
            'fields': ('about_us_link', 'our_story_link', 'blog_link', 'careers_link', 'press_link')
        }),
        ('Navigation Links - Support', {
            'fields': ('contact_us_link', 'track_order_link', 'returns_link', 'shipping_link', 'size_guide_link')
        }),
        ('Navigation Links - Legal', {
            'fields': ('privacy_policy_link', 'terms_link', 'refund_policy_link')
        }),
        ('Settings', {
            'fields': ('enable_cod', 'free_shipping_above', 'copyright_text')
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle')
    list_editable = ('order', 'is_active')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Buttons', {
            'fields': ('button_text_1', 'button_link_1', 'button_text_2', 'button_link_2')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(FestivalBanner)
class FestivalBannerAdmin(admin.ModelAdmin):
    list_display = ('festival_name', 'coupon_code', 'start_date', 'end_date', 'is_active', 'is_valid')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('festival_name', 'coupon_code')
    list_editable = ('is_active',)
    ordering = ('-start_date',)
    
    fieldsets = (
        ('Festival Information', {
            'fields': ('festival_name', 'festival_tag', 'title', 'description')
        }),
        ('Offer Details', {
            'fields': ('offer_text_1', 'offer_percentage', 'offer_text_2', 'coupon_code')
        }),
        ('Banner Design', {
            'fields': ('banner_image', 'bg_color_1', 'bg_color_2', 'button_text', 'button_link')
        }),
        ('Validity', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
    )
