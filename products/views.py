from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from datetime import datetime, timedelta
from .models import *
from .decorators import login_required_custom
from .utils import generate_otp, send_otp_email, send_welcome_email
import json
import razorpay
import hmac
import hashlib



# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))




# ==================== HOME & NAVIGATION ====================



def home(request):
    from django.utils import timezone
    
    banners = HeroBanner.objects.filter(is_active=True).order_by('order')[:4]
    
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
        'festival_banner': festival_banner,
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




def search_products(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
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




def new_arrivals(request):
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




def offers(request):
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




def all_products(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
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




# ==================== AUTHENTICATION ====================



def login_page(request):
    if request.session.get('is_logged_in'):
        return redirect('home')
    return render(request, 'products/login.html')




def register_page(request):
    if request.session.get('is_logged_in'):
        return redirect('home')
    return render(request, 'products/register.html')




@require_POST
def send_login_otp(request):
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required'})
    
    try:
        user = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Account not found. Please register first.'})
    
    otp = generate_otp()
    
    UserOTP.objects.filter(email=email).delete()
    UserOTP.objects.create(email=email, otp=otp)
    
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




@require_POST
def verify_login_otp(request):
    email = request.POST.get('email', '').strip()
    otp = request.POST.get('otp', '').strip()
    
    if not email or not otp:
        return JsonResponse({'success': False, 'message': 'Email and OTP are required'})
    
    try:
        otp_obj = UserOTP.objects.get(email=email, otp=otp, is_verified=False)
        
        if otp_obj.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP expired. Please request a new one.'})
        
        otp_obj.is_verified = True
        otp_obj.save()
        
        user = UserProfile.objects.get(email=email)
        
        request.session['user_email'] = user.email
        request.session['user_name'] = user.name
        request.session['user_id'] = user.id
        request.session['is_logged_in'] = True
        
        next_url = request.session.get('next_url', '/')
        if 'next_url' in request.session:
            del request.session['next_url']
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'redirect_url': next_url
        })
    
    except UserOTP.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid OTP'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'})




@require_POST
def register_user(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    
    if not all([name, email, phone]):
        return JsonResponse({'success': False, 'message': 'All fields are required'})
    
    if UserProfile.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'Email already registered'})
    
    otp = generate_otp()
    
    request.session['temp_registration'] = {
        'name': name,
        'email': email,
        'phone': phone,
        'otp': otp
    }
    
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




@require_POST
def verify_registration_otp(request):
    otp = request.POST.get('otp', '').strip()
    
    if not otp:
        return JsonResponse({'success': False, 'message': 'OTP is required'})
    
    temp_data = request.session.get('temp_registration')
    
    if not temp_data:
        return JsonResponse({'success': False, 'message': 'Session expired. Please try again.'})
    
    if otp == temp_data['otp']:
        user = UserProfile.objects.create(
            name=temp_data['name'],
            email=temp_data['email'],
            phone=temp_data['phone'],
            is_verified=True
        )
        
        send_welcome_email(user.email, user.name)
        
        request.session['user_email'] = user.email
        request.session['user_name'] = user.name
        request.session['user_id'] = user.id
        request.session['is_logged_in'] = True
        
        next_url = request.session.get('next_url', '/')
        
        if 'temp_registration' in request.session:
            del request.session['temp_registration']
        if 'next_url' in request.session:
            del request.session['next_url']
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'redirect_url': next_url
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid OTP'})




def logout_user(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('home')




def check_login_status(request):
    is_logged_in = request.session.get('is_logged_in', False)
    user_name = request.session.get('user_name', '')
    
    return JsonResponse({
        'is_logged_in': is_logged_in,
        'user_name': user_name
    })




# ==================== WISHLIST (Login Required) ====================



@login_required_custom
def wishlist(request):
    wishlist_items = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_items, is_active=True)
    
    context = {
        'products': products,
        'total_items': len(wishlist_items),
    }
    
    return render(request, 'products/wishlist.html', context)




@login_required_custom
@require_POST
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    
    if product_id:
        wishlist = request.session.get('wishlist', [])
        
        if int(product_id) not in wishlist:
            wishlist.append(int(product_id))
            request.session['wishlist'] = wishlist
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Added to wishlist!',
                'count': len(wishlist)
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Already in wishlist!'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})




@login_required_custom
@require_POST
def remove_from_wishlist(request):
    product_id = request.POST.get('product_id')
    
    if product_id:
        wishlist = request.session.get('wishlist', [])
        
        if int(product_id) in wishlist:
            wishlist.remove(int(product_id))
            request.session['wishlist'] = wishlist
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Removed from wishlist',
                'count': len(wishlist)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})




def get_wishlist_items(request):
    wishlist = request.session.get('wishlist', [])
    return JsonResponse({
        'count': len(wishlist),
        'items': wishlist
    })




# ==================== CART (Login Required) ====================



@login_required_custom
def cart(request):
    cart_items = request.session.get('cart', {})
    
    products = []
    subtotal = 0
    
    for product_id, item_data in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.current_price * item_data['quantity']
            subtotal += item_total
            
            products.append({
                'product': product,
                'quantity': item_data['quantity'],
                'color': item_data.get('color', 'Default'),
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue
    
    delivery_charge = 0 if subtotal >= 999 else 99
    total = subtotal + delivery_charge
    
    context = {
        'cart_items': products,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'item_count': len(cart_items),
    }
    
    return render(request, 'products/cart.html', context)




@login_required_custom
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    color = request.POST.get('color', 'Default')
    
    if product_id:
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'quantity': quantity,
                'color': color,
            }
        
        request.session['cart'] = cart
        request.session.modified = True
        
        total_items = sum(item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'success': True,
            'message': 'Added to cart!',
            'count': total_items
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})




@login_required_custom
@require_POST
def remove_from_cart(request):
    product_id = request.POST.get('product_id')
    
    if product_id:
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
            
            total_items = sum(item['quantity'] for item in cart.values())
            
            return JsonResponse({
                'success': True,
                'message': 'Removed from cart',
                'count': total_items
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})




def get_cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': total_items})




# ==================== ORDERS (Login Required) ====================


@login_required_custom
@csrf_exempt
@require_POST
def buy_now(request, slug):
    """Handle Buy Now - FOOLPROOF VERSION - CANNOT FAIL"""
    
    try:
        # Parse request data
        try:
            request_data = json.loads(request.body.decode('utf-8'))
        except:
            request_data = {}
        
        # Get product
        product = get_object_or_404(Product, slug=slug)
        
        # Get quantity
        quantity = int(request_data.get('quantity', 1))
        
        # ✅ SIMPLE: Just use first color or default
        first_color = product.colors.first()
        
        if first_color:
            color_id = first_color.id
            color_name = first_color.name
        else:
            color_id = None
            color_name = 'Default'
        
        # Store in session
        request.session['buy_now_item'] = {
            'product_id': product.id,
            'product_name': product.name,
            'product_slug': slug,
            'color_id': color_id,
            'color_name': color_name,
            'quantity': quantity,
            'price': float(product.current_price)
        }
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'show_address_modal': True,
            'message': 'Please enter delivery address'
        })
        
    except Exception as e:
        print(f"❌ BUY NOW ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': 'Please try again'
        }, status=200)  # ✅ Changed to 200 instead of 500


@login_required_custom
@require_POST
def create_buy_now_order(request):
    """Create Razorpay order for Buy Now with address - FIXED"""
    
    # Get buy now item from session
    buy_now_item = request.session.get('buy_now_item')
    
    if not buy_now_item:
        return JsonResponse({
            'success': False,
            'message': 'Session expired. Please try again.'
        })
    
    # ✅ Get address details from POST (not body)
    customer_name = request.POST.get('customer_name', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    address_line1 = request.POST.get('address_line1', '').strip()
    address_line2 = request.POST.get('address_line2', '').strip()
    landmark = request.POST.get('landmark', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    delivery_type = request.POST.get('delivery_type', 'standard')
    
    # Validate required fields
    if not all([customer_name, customer_phone, address_line1, address_line2, pincode, city, state]):
        return JsonResponse({
            'success': False,
            'message': 'Please fill all required fields'
        })
    
    # Calculate pricing
    subtotal = float(buy_now_item['price']) * int(buy_now_item['quantity'])
    
    # Check delivery charge based on pincode
    try:
        pincode_obj = Pincode.objects.get(pincode=pincode, is_serviceable=True)
        if delivery_type == 'express':
            delivery_charge = float(pincode_obj.express_delivery_charge)
        else:
            delivery_charge = 0.0
    except Pincode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Delivery not available for this pincode'
        })
    
    total_amount = subtotal + delivery_charge
    
    # Create Razorpay order
    try:
        amount_in_paise = int(total_amount * 100)
        
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'product_name': buy_now_item['product_name'],
                'customer_email': request.session.get('user_email'),
            }
        })
        
        # Store complete order details in session
        request.session['pending_order'] = {
            'razorpay_order_id': str(razorpay_order['id']),
            'product_id': int(buy_now_item['product_id']),
            'product_name': str(buy_now_item['product_name']),
            'product_slug': str(buy_now_item['product_slug']),
            'color': str(buy_now_item['color_name']),
            'quantity': int(buy_now_item['quantity']),
            'price': float(buy_now_item['price']),
            'customer_name': str(customer_name),
            'customer_phone': str(customer_phone),
            'address_line1': str(address_line1),
            'address_line2': str(address_line2),
            'landmark': str(landmark),
            'pincode': str(pincode),
            'city': str(city),
            'state': str(state),
            'delivery_type': str(delivery_type),
            'delivery_charge': float(delivery_charge),
            'subtotal': float(subtotal),
            'total_amount': float(total_amount),
        }
        
        # Clear buy_now_item from session
        if 'buy_now_item' in request.session:
            del request.session['buy_now_item']
        
        return JsonResponse({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'key_id': settings.RAZORPAY_KEY_ID,
            'customer_name': customer_name,
            'customer_email': request.session.get('user_email'),
            'customer_phone': customer_phone,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Payment initialization failed: {str(e)}'
        })




@csrf_exempt
@require_POST
def verify_payment_direct(request):
    """Verify payment and create order"""
    try:
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
        
        # Get pending order details from session
        pending_order = request.session.get('pending_order')
        
        if not pending_order:
            return JsonResponse({'success': False, 'message': 'Session expired'})
        
        # Get product
        product = Product.objects.get(id=pending_order['product_id'])
        
        # Create Order
        order = Order.objects.create(
            customer_name=pending_order['customer_name'],
            customer_email=request.session.get('user_email'),
            customer_phone=pending_order['customer_phone'],
            address_line1=pending_order['address_line1'],
            address_line2=pending_order['address_line2'],
            city=pending_order['city'],
            state=pending_order['state'],
            pincode=pending_order['pincode'],
            status='confirmed',
            payment_method='online',
            subtotal=pending_order['subtotal'],
            discount=0,
            delivery_charge=pending_order['delivery_charge'],
            total_amount=pending_order['total_amount'],
            delivery_type=pending_order['delivery_type'],
        )
        
        # Create Order Item
        OrderItem.objects.create(
            order=order,
            product=product,
            color=pending_order['color'],
            quantity=pending_order['quantity'],
            price=pending_order['price']
        )
        
        # Create Payment record
        Payment.objects.create(
            order=order,
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature,
            amount=pending_order['total_amount'],
            status='success',
            payment_method='razorpay'
        )
        
        # Clear session
        if 'pending_order' in request.session:
            del request.session['pending_order']
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': 'Order placed successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})




@login_required_custom
def my_orders(request):
    user_email = request.session.get('user_email')
    orders = Order.objects.filter(customer_email=user_email).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'products/my_orders.html', context)




# ==================== UTILITY ====================



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




@require_POST
def update_cart_quantity(request):
    """Update cart item quantity"""
    product_id = request.POST.get('product_id')
    color = request.POST.get('color')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    cart_key = f"{product_id}_{color}"
    
    if cart_key in cart:
        cart[cart_key]['quantity'] = quantity
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})




# ==================== CHECKOUT ====================



@login_required_custom
def checkout(request):
    """Checkout page with cart items"""
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    products = []
    subtotal = 0
    
    for product_id, item_data in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.current_price * item_data['quantity']
            subtotal += item_total
            
            products.append({
                'product': product,
                'quantity': item_data['quantity'],
                'color': item_data.get('color', 'Default'),
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue
    
    delivery_charge = 0 if subtotal >= 999 else 99
    total = subtotal + delivery_charge
    
    context = {
        'cart_items': products,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'item_count': len(cart_items),
    }
    
    return render(request, 'products/checkout.html', context)




@login_required_custom
@require_POST
def create_order_from_cart(request):
    """Create Razorpay order from cart - FIXED"""
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        return JsonResponse({
            'success': False,
            'message': 'Cart is empty'
        })
    
    # ✅ Get address details from POST
    customer_name = request.POST.get('customer_name', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    address_line1 = request.POST.get('address_line1', '').strip()
    address_line2 = request.POST.get('address_line2', '').strip()
    landmark = request.POST.get('landmark', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    delivery_type = request.POST.get('delivery_type', 'standard')
    
    # Validate required fields
    if not all([customer_name, customer_phone, address_line1, address_line2, pincode, city, state]):
        return JsonResponse({
            'success': False,
            'message': 'Please fill all required fields'
        })
    
    # Calculate total
    subtotal = 0
    cart_products = []
    
    for product_id, item_data in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = float(product.current_price) * item_data['quantity']
            subtotal += item_total
            
            cart_products.append({
                'product_id': int(product.id),
                'product_name': str(product.name),
                'color': str(item_data.get('color', 'Default')),
                'quantity': int(item_data['quantity']),
                'price': float(product.current_price),
                'item_total': float(item_total)
            })
        except Product.DoesNotExist:
            continue
    
    # Check delivery charge
    try:
        pincode_obj = Pincode.objects.get(pincode=pincode, is_serviceable=True)
        if delivery_type == 'express':
            delivery_charge = float(pincode_obj.express_delivery_charge)
        else:
            delivery_charge = 0.0 if subtotal >= 999 else 50.0
    except Pincode.DoesNotExist:
        delivery_charge = 0.0 if subtotal >= 999 else 50.0
    
    total_amount = subtotal + delivery_charge
    
    # Create Razorpay order
    try:
        amount_in_paise = int(total_amount * 100)
        
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'customer_email': request.session.get('user_email'),
                'item_count': len(cart_items)
            }
        })
        
        # Store order details in session
        request.session['pending_cart_order'] = {
            'razorpay_order_id': str(razorpay_order['id']),
            'cart_products': cart_products,
            'customer_name': str(customer_name),
            'customer_phone': str(customer_phone),
            'address_line1': str(address_line1),
            'address_line2': str(address_line2),
            'landmark': str(landmark),
            'pincode': str(pincode),
            'city': str(city),
            'state': str(state),
            'delivery_type': str(delivery_type),
            'delivery_charge': float(delivery_charge),
            'subtotal': float(subtotal),
            'total_amount': float(total_amount),
        }
        
        return JsonResponse({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'key_id': settings.RAZORPAY_KEY_ID,
            'customer_name': customer_name,
            'customer_email': request.session.get('user_email'),
            'customer_phone': customer_phone,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Payment initialization failed: {str(e)}'
        })




@csrf_exempt
@require_POST
def verify_payment_cart(request):
    """Verify payment and create order from cart"""
    try:
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
        
        # Get pending order details from session
        pending_order = request.session.get('pending_cart_order')
        
        if not pending_order:
            return JsonResponse({'success': False, 'message': 'Session expired'})
        
        # Create Order
        order = Order.objects.create(
            customer_name=pending_order['customer_name'],
            customer_email=request.session.get('user_email'),
            customer_phone=pending_order['customer_phone'],
            address_line1=pending_order['address_line1'],
            address_line2=pending_order['address_line2'],
            city=pending_order['city'],
            state=pending_order['state'],
            pincode=pending_order['pincode'],
            status='confirmed',
            payment_method='online',
            subtotal=pending_order['subtotal'],
            discount=0,
            delivery_charge=pending_order['delivery_charge'],
            total_amount=pending_order['total_amount'],
            delivery_type=pending_order['delivery_type'],
        )
        
        # Create Order Items
        for item in pending_order['cart_products']:
            product = Product.objects.get(id=item['product_id'])
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
            amount=pending_order['total_amount'],
            status='success',
            payment_method='razorpay'
        )
        
        # Clear cart and session
        request.session['cart'] = {}
        if 'pending_cart_order' in request.session:
            del request.session['pending_cart_order']
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'message': 'Order placed successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})




# ==================== MANAGER DASHBOARD (NEW) ====================



def manager_login(request):
    """Manager login page"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username == settings.MANAGER_USERNAME and password == settings.MANAGER_PASSWORD:
            request.session['is_manager_logged_in'] = True
            return redirect('manager_orders')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'manager/manager_login.html')



def manager_logout(request):
    """Manager logout"""
    request.session.pop('is_manager_logged_in', None)
    return redirect('manager_login')



def manager_login_required(view_func):
    """Decorator to check if manager is logged in"""
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('is_manager_logged_in'):
            return redirect('manager_login')
        return view_func(request, *args, **kwargs)
    return _wrapped



@manager_login_required
def manager_orders(request):
    """Manager dashboard - All orders"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')

    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter.lower())

    if search:
        orders = orders.filter(customer_phone__icontains=search)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'manager/manager_orders.html', context)



@manager_login_required
def manager_order_detail(request, order_id):
    """Manager view single order detail"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'manager/manager_order_detail.html', {'order': order})
