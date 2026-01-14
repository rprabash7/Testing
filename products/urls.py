from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_collection, name='category_collection'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('check-pincode/', views.check_pincode, name='check_pincode'),
    path('buy-now/<slug:slug>/', views.buy_now, name='buy_now'),
    path('order-summary/', views.order_summary, name='order_summary'),
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    
    # Authentication
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('send-login-otp/', views.send_login_otp, name='send_login_otp'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('register-user/', views.register_user, name='register_user'),
    path('verify-registration-otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('logout/', views.logout_user, name='logout'),
    path('check-login-status/', views.check_login_status, name='check_login_status'),
    
    # Features
    path('search/', views.search_products, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Navigation Pages
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('offers/', views.offers, name='offers'),
    path('all-products/', views.all_products, name='all_products'),

    # ... existing urls ...

# Helper APIs
path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
path('get-wishlist-items/', views.get_wishlist_items, name='get_wishlist_items'),

]
