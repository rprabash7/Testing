from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q  # ✅ Add this import
from datetime import datetime, timedelta
from .models import Category, Product, ProductColor, ColorImage, Pincode, Order, OrderItem, Payment, UserOTP, UserProfile, HeroBanner, FestivalBanner
import json
import razorpay
import hmac
import hashlib

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home(request):
    from django.utils import timezone
    
    # Get active banners
    banners = HeroBanner.objects.filter(is_active=True).order_by('order')[:4]
    
    # Get active festival banner
    today = timezone.now().date()
    festival_banner = FestivalBanner.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).first()
    
    bestsellers = Product.objects.filter(is_bestseller=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'banners': banners,
        'festival_banner': festival_banner,  # ✅ Add festival banner
        'bestsellers': bestsellers,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)


def category_collection(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    all_fabrics = products.values_list('fabric', flat=True).distinct()
    all_colors = products.values_list('primary_color', flat=True).distinct()
    
    all_occasions = set()
    for p in products:
        all_occasions.update(p.get_occasions_list())
    all_occasions = sorted(list(all_occasions))
    
    fabric_counts = {}
    for fabric in all_fabrics:
        fabric_counts[fabric] = products.filter(fabric=fabric).count()
    
    occasion_counts = {}
    for occasion in all_occasions:
        occasion_counts[occasion] = products.filter(occasion__icontains=occasion).count()
    
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price-low':
        products = products.order_by('current_price')
    elif sort_by == 'price-high':
        products = products.order_by('-current_price')
    elif sort_by == 'new':
        products = products.order_by('-created_at')
    elif sort_by == 'bestseller':
        products = products.filter(is_bestseller=True)
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'discount':
        products = products.order_by('-discount_percent')
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'total_products': products.count(),
        'all_fabrics': all_fabrics,
        'fabric_counts': fabric_counts,
        'all_colors': all_colors,
        'all_occasions': all_occasions,
        'occasion_counts': occasion_counts,
        'current_sort': sort_by,
    }
    return render(request, 'products/collection.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    colors = product.colors.all()
    
    selected_color = colors.first()
    
    images_by_color = {}
    for color in colors:
        color_images = []
        for img in color.images.all():
            color_images.append({
                'url': img.image.url,
                'order': img.order
            })
        images_by_color[color.id] = color_images
    
    images_json = json.dumps(images_by_color)
    
    context = {
        'product': product,
        'colors': colors,
        'selected_color': selected_color,
        'images_by_color_json': images_json,
    }
    return render(request, 'products/product_detail.html', context)

@require_POST
def check_pincode(request):
    pincode = request.POST.get('pincode', '').strip()
    
    if not pincode or len(pincode) != 6:
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid 6-digit pincode'
        })
    
    try:
        pincode_obj = Pincode.objects.get(pincode=pincode, is_serviceable=True)
        
        standard_date = datetime.now() + timedelta(days=pincode_obj.standard_delivery_days)
        express_date = datetime.now() + timedelta(days=pincode_obj.express_delivery_days)
        
        return JsonResponse({
            'success': True,
            'serviceable': True,
            'city': pincode_obj.city,
            'state': pincode_obj.state,
            'standard_delivery': {
                'days': pincode_obj.standard_delivery_days,
                'date': standard_date.strftime('%d %b, %A'),
                'charge': 0
            },
            'express_delivery': {
                'days': pincode_obj.express_delivery_days,
                'date': express_date.strftime('%d %b, %A'),
                'charge': float(pincode_obj.express_delivery_charge)
            },
            'cod_available': pincode_obj.cod_available
        })
    
    except Pincode.DoesNotExist:
        return JsonResponse({
            'success': True,
            'serviceable': False,
            'message': 'Sorry, we do not deliver to this pincode yet.'
        })

def buy_now(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    quantity = int(request.POST.get('quantity', 1))
    color = request.POST.get('color', product.colors.first().name if product.colors.first() else 'Default')
    
    request.session['buy_now_item'] = {
        'product_id': product.id,
        'product_name': product.name,
        'product_slug': product.slug,
        'color': color,
        'quantity': quantity,
        'price': float(product.current_price),
        'original_price': float(product.original_price),
        'discount': float(product.original_price - product.current_price),
        'image': product.colors.first().images.first().image.url if product.colors.first() and product.colors.first().images.first() else None,
        'fabric': product.fabric,
    }
    
    return redirect('order_summary')

def order_summary(request):
    item = request.session.get('buy_now_item')
    
    if not item:
        return redirect('home')
    
    item_total = item['price'] * item['quantity']
    total_mrp = item['original_price'] * item['quantity']
    discount_amount = item['discount'] * item['quantity']
    delivery_charge = 0
    total_amount = item_total + delivery_charge
    savings = discount_amount
    
    context = {
        'item': item,
        'item_total': item_total,
        'total_mrp': total_mrp,
        'discount_amount': discount_amount,
        'delivery_charge': delivery_charge,
        'total_amount': total_amount,
        'savings': savings,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    
    return render(request, 'products/order_summary.html', context)

@require_POST
def create_razorpay_order(request):
    """Create Razorpay order"""
    try:
        item = request.session.get('buy_now_item')
        
        if not item:
            return JsonResponse({'success': False, 'message': 'No items in cart'})
        
        # Calculate amount
        amount = int(item['price'] * item['quantity'] * 100)  # Amount in paise
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })
        
        # Store order details in session
        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['order_amount'] = amount
        
        return JsonResponse({
            'success': True,
            'order_id': razorpay_order['id'],
            'amount': amount,
            'key_id': settings.RAZORPAY_KEY_ID,
            'currency': 'INR'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def verify_payment(request):
    """Verify Razorpay payment and create order"""
    try:
        # Get payment details from frontend
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{order_id}|{payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != signature:
            return JsonResponse({'success': False, 'message': 'Invalid payment signature'})
        
        # Payment verified - Create Order
        item = request.session.get('buy_now_item')
        
        if not item:
            return JsonResponse({'success': False, 'message': 'Session expired'})
        
        # Create Order
        product = Product.objects.get(id=item['product_id'])
        
        order = Order.objects.create(
            customer_name='Test Customer',  # Replace with actual data from form
            customer_email='test@example.com',
            customer_phone='9876543210',
            address_line1='Test Address',
            city='Bangalore',
            state='Karnataka',
            pincode='560001',
            status='confirmed',
            payment_method='online',
            subtotal=item['price'] * item['quantity'],
            discount=item['discount'] * item['quantity'],
            delivery_charge=0,
            total_amount=item['price'] * item['quantity'],
            delivery_type='standard',
        )
        
        # Create Order Item
        OrderItem.objects.create(
            order=order,
            product=product,
            color=item['color'],
            quantity=item['quantity'],
            price=item['price']
        )
        
        # Create Payment record
        Payment.objects.create(
            order=order,
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature,
            amount=item['price'] * item['quantity'],
            status='success',
            payment_method='razorpay'
        )
        
        # Clear session
        if 'buy_now_item' in request.session:
            del request.session['buy_now_item']
        if 'razorpay_order_id' in request.session:
            del request.session['razorpay_order_id']
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': 'Order placed successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, order_id=order_id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'products/order_success.html', context)


# ... Keep all existing views ...

from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .models import UserOTP, UserProfile
from .utils import generate_otp, send_otp_email, send_welcome_email

# Login Page
def login_page(request):
    return render(request, 'products/login.html')

# Send OTP for Login
@require_POST
def send_login_otp(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    
    # Check if user exists
    try:
        user = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Account not found. Please register first.'})
    
    # Generate OTP
    otp = generate_otp()
    
    # Delete old OTPs for this email
    UserOTP.objects.filter(email=email).delete()
    
    # Create new OTP
    UserOTP.objects.create(email=email, otp=otp)
    
    # Send OTP via email
    if send_otp_email(email, otp):
        return JsonResponse({
            'success': True,
            'message': 'OTP sent successfully to your email'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        })

# Verify OTP and Login
@require_POST
def verify_login_otp(request):
    email = request.POST.get('email', '').strip()
    otp = request.POST.get('otp', '').strip()
    
    if not email or not otp:
        return JsonResponse({'success': False, 'message': 'Email and OTP are required'})
    
    try:
        otp_obj = UserOTP.objects.get(email=email, otp=otp, is_verified=False)
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP expired. Please request a new one.'})
        
        # OTP verified successfully
        otp_obj.is_verified = True
        otp_obj.save()
        
        # Get user
        user = UserProfile.objects.get(email=email)
        
        # Store user info in session
        request.session['user_email'] = user.email
        request.session['user_name'] = user.name
        request.session['user_id'] = user.id
        request.session['is_logged_in'] = True
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'redirect_url': '/'
        })
    
    except UserOTP.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid OTP'})

# Register Page
def register_page(request):
    return render(request, 'products/register.html')

# Register User
@require_POST
def register_user(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '').strip()
    
    if not all([name, email, phone, password]):
        return JsonResponse({'success': False, 'message': 'All fields are required'})
    
    # Check if user already exists
    if UserProfile.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'Email already registered'})
    
    # Generate OTP
    otp = generate_otp()
    
    # Store registration data in session temporarily
    request.session['temp_registration'] = {
        'name': name,
        'email': email,
        'phone': phone,
        'password': make_password(password),
        'otp': otp
    }
    
    # Send OTP
    if send_otp_email(email, otp):
        return JsonResponse({
            'success': True,
            'message': 'OTP sent to your email. Please verify to complete registration.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        })

# Verify Registration OTP
@require_POST
def verify_registration_otp(request):
    otp = request.POST.get('otp', '').strip()
    
    if not otp:
        return JsonResponse({'success': False, 'message': 'OTP is required'})
    
    # Get temp registration data
    temp_data = request.session.get('temp_registration')
    
    if not temp_data:
        return JsonResponse({'success': False, 'message': 'Session expired. Please try again.'})
    
    # Verify OTP
    if otp == temp_data['otp']:
        # Create user account
        user = UserProfile.objects.create(
            name=temp_data['name'],
            email=temp_data['email'],
            phone=temp_data['phone'],
            password=temp_data['password'],
            is_verified=True
        )
        
        # Send welcome email
        send_welcome_email(user.email, user.name)
        
        # Login user automatically
        request.session['user_email'] = user.email
        request.session['user_name'] = user.name
        request.session['user_id'] = user.id
        request.session['is_logged_in'] = True
        
        # Clear temp data
        del request.session['temp_registration']
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'redirect_url': '/'
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid OTP'})

# Logout
def logout_user(request):
    request.session.flush()
    return redirect('home')

# Check Login Status
def check_login_status(request):
    is_logged_in = request.session.get('is_logged_in', False)
    user_name = request.session.get('user_name', '')
    
    return JsonResponse({
        'is_logged_in': is_logged_in,
        'user_name': user_name
    })


# ... Keep all existing views ...

# Search Products
def search_products(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    # Search in product name, fabric, occasion
    products = Product.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(fabric__icontains=query) |
        models.Q(occasion__icontains=query) |
        models.Q(category__name__icontains=query),
        is_active=True
    ).distinct()
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
        'total_products': products.count(),
    }
    
    return render(request, 'products/search_results.html', context)

# Wishlist Page
def wishlist(request):
    # Get wishlist from session
    wishlist_items = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_items, is_active=True)
    
    context = {
        'products': products,
    }
    
    return render(request, 'products/wishlist.html', context)

# Add to Wishlist
@require_POST
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product ID required'})
    
    wishlist = request.session.get('wishlist', [])
    
    if int(product_id) in wishlist:
        return JsonResponse({'success': False, 'message': 'Already in wishlist'})
    
    wishlist.append(int(product_id))
    request.session['wishlist'] = wishlist
    
    return JsonResponse({
        'success': True,
        'message': 'Added to wishlist',
        'count': len(wishlist)
    })

# Remove from Wishlist
@require_POST
def remove_from_wishlist(request):
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product ID required'})
    
    wishlist = request.session.get('wishlist', [])
    
    if int(product_id) in wishlist:
        wishlist.remove(int(product_id))
        request.session['wishlist'] = wishlist
        
        return JsonResponse({
            'success': True,
            'message': 'Removed from wishlist',
            'count': len(wishlist)
        })
    
    return JsonResponse({'success': False, 'message': 'Not in wishlist'})

# Cart Page
def cart(request):
    # Get cart from session
    cart_items = request.session.get('cart', {})
    
    products_data = []
    total_amount = 0
    
    for product_id, item_data in cart_items.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.current_price * item_data['quantity']
            
            products_data.append({
                'product': product,
                'quantity': item_data['quantity'],
                'color': item_data.get('color', 'Default'),
                'item_total': item_total
            })
            
            total_amount += item_total
        except:
            pass
    
    context = {
        'cart_items': products_data,
        'total_amount': total_amount,
        'total_items': sum(item['quantity'] for item in products_data),
    }
    
    return render(request, 'products/cart.html', context)

# Add to Cart
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    color = request.POST.get('color', 'Default')
    
    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product ID required'})
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {
            'quantity': quantity,
            'color': color
        }
    
    request.session['cart'] = cart
    
    # Calculate total items
    total_items = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'success': True,
        'message': 'Added to cart',
        'count': total_items
    })

# Remove from Cart
@require_POST
def remove_from_cart(request):
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({'success': False, 'message': 'Product ID required'})
    
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        
        total_items = sum(item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'success': True,
            'message': 'Removed from cart',
            'count': total_items
        })
    
    return JsonResponse({'success': False, 'message': 'Not in cart'})

# My Orders Page
def my_orders(request):
    if not request.session.get('is_logged_in'):
        return redirect('login')
    
    user_email = request.session.get('user_email')
    orders = Order.objects.filter(customer_email=user_email).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'products/my_orders.html', context)


# Search Products (Fix the function)
def search_products(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    # Search in product name, fabric, occasion
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(fabric__icontains=query) |
        Q(occasion__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    ).distinct()
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
        'total_products': products.count(),
    }
    
    return render(request, 'products/search_results.html', context)


# ... Keep all existing views ...

# New Arrivals Page
def new_arrivals(request):
    # Products created in last 30 days
    from datetime import timedelta
    from django.utils import timezone
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    products = Product.objects.filter(
        created_at__gte=thirty_days_ago,
        is_active=True
    ).order_by('-created_at')
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_title': 'New Arrivals',
        'total_products': products.count(),
    }
    
    return render(request, 'products/category_products.html', context)

# Offers Page
def offers(request):
    # Products with discount > 30%
    products = Product.objects.filter(
        discount_percent__gte=30,
        is_active=True
    ).order_by('-discount_percent')
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_title': 'Special Offers',
        'total_products': products.count(),
    }
    
    return render(request, 'products/category_products.html', context)

# All Products Page
def all_products(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price-low':
        products = products.order_by('current_price')
    elif sort_by == 'price-high':
        products = products.order_by('-current_price')
    elif sort_by == 'new':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'discount':
        products = products.order_by('-discount_percent')
    
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_title': 'All Products',
        'total_products': products.count(),
        'current_sort': sort_by,
    }
    
    return render(request, 'products/category_products.html', context)


# ... Keep all existing views ...

# Get Cart Count
def get_cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': total_items})

# Get Wishlist Items
def get_wishlist_items(request):
    wishlist = request.session.get('wishlist', [])
    return JsonResponse({
        'count': len(wishlist),
        'items': wishlist
    })
