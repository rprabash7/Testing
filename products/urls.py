from django.urls import path
from . import views


urlpatterns = [
    # Home & Navigation
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_collection, name='category_collection'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search_products, name='search_products'),
    path('search/', views.search_products, name='search'),  # alias
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('offers/', views.offers, name='offers'),
    path('all-products/', views.all_products, name='all_products'),
    
    # Authentication
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('send-login-otp/', views.send_login_otp, name='send_login_otp'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('register-user/', views.register_user, name='register_user'),
    path('verify-registration-otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('check-login-status/', views.check_login_status, name='check_login_status'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('get-wishlist-items/', views.get_wishlist_items, name='get_wishlist_items'),
    
    # Cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    
    # Orders & Payment (DIRECT BUY NOW)
    path('product/<slug:slug>/buy-now/', views.buy_now, name='buy_now'),
    path('create-buy-now-order/', views.create_buy_now_order, name='create_buy_now_order'),   # ✅ NEW URL
    path('verify-payment-direct/', views.verify_payment_direct, name='verify_payment_direct'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Utility
    path('check-pincode/', views.check_pincode, name='check_pincode'),

    # Checkout from cart
    path('checkout/', views.checkout, name='checkout'),
    path('create-order-from-cart/', views.create_order_from_cart, name='create_order_from_cart'),
    path('verify-payment-cart/', views.verify_payment_cart, name='verify_payment_cart'),

    # Manager
    path('manager/login/', views.manager_login, name='manager_login'),
    path('manager/logout/', views.manager_logout, name='manager_logout'),
    path('manager/orders/', views.manager_orders, name='manager_orders'),
    path('manager/orders/<int:order_id>/', views.manager_order_detail, name='manager_order_detail'),


    path('manager/order/<int:order_id>/mark-refund/', views.manager_mark_refund, name='manager_mark_refund'),
path('manager/order/<int:order_id>/mark-refunded/', views.manager_mark_refunded, name='manager_mark_refunded'),

]
