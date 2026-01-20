import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(email, otp):
    """Send OTP via email"""
    subject = 'Your Manovastra Login OTP'
    message = f'''
    Hello,
    
    Your OTP for Manovastra login is: {otp}
    
    This OTP is valid for {settings.OTP_EXPIRY_TIME} minutes.
    
    Please do not share this OTP with anyone.
    
    Thank you,
    Manovastra Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_welcome_email(email, name):
    """Send welcome email after successful registration"""
    subject = 'Welcome to Manovastra!'
    message = f'''
    Dear {name},
    
    Welcome to Manovastra - Your destination for premium Indian ethnic wear!
    
    Your account has been created successfully. You can now:
    ✓ Browse our exclusive collection
    ✓ Track your orders
    ✓ Manage your wishlist
    ✓ Get exclusive offers
    
    Thank you for choosing Manovastra!
    
    Best regards,
    Manovastra Team
    '''
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


import string
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_otp():
    """
    Generate a random 6-digit OTP
    Returns: String of 6 digits
    """
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp):
    """
    Send OTP to user's email
    Args:
        email: User's email address
        otp: 6-digit OTP code
    Returns:
        Boolean: True if email sent successfully, False otherwise
    """
    try:
        subject = f'Your OTP for Manovastra - {otp}'
        
        # HTML message
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                }}
                .header p {{
                    color: #FFE4B5;
                    margin: 5px 0 0 0;
                    font-size: 14px;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .otp-box {{
                    background: linear-gradient(135deg, #FFF8DC 0%, #FFE4B5 100%);
                    border: 2px dashed #8B4513;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 30px 0;
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #8B4513;
                    letter-spacing: 8px;
                    margin: 10px 0;
                }}
                .message {{
                    color: #333;
                    font-size: 16px;
                    line-height: 1.6;
                    margin: 20px 0;
                }}
                .note {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: left;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #8B4513;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Manovastra</h1>
                    <p>Elegance Redefined</p>
                </div>
                <div class="content">
                    <h2 style="color: #333;">Verify Your Email</h2>
                    <p class="message">
                        Thank you for choosing Manovastra! Use the OTP below to complete your verification:
                    </p>
                    <div class="otp-box">
                        <p style="margin: 0; color: #666; font-size: 14px;">Your OTP Code</p>
                        <div class="otp-code">{otp}</div>
                        <p style="margin: 0; color: #666; font-size: 12px;">Valid for 5 minutes</p>
                    </div>
                    <div class="note">
                        <strong>⚠️ Security Note:</strong><br>
                        • Do not share this OTP with anyone<br>
                        • Our team will never ask for your OTP<br>
                        • This OTP is valid for 5 minutes only
                    </div>
                </div>
                <div class="footer">
                    <p>If you didn't request this OTP, please ignore this email.</p>
                    <p>Need help? Contact us at <a href="mailto:support@manovastra.com">support@manovastra.com</a></p>
                    <p style="margin-top: 15px;">© 2026 Manovastra. All Rights Reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text message (fallback)
        plain_message = f"""
        Manovastra - Email Verification
        
        Your OTP Code: {otp}
        
        This OTP is valid for 5 minutes.
        
        Do not share this OTP with anyone.
        
        If you didn't request this OTP, please ignore this email.
        
        © 2026 Manovastra. All Rights Reserved.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False


def send_welcome_email(email, name):
    """
    Send welcome email to newly registered user
    Args:
        email: User's email address
        name: User's name
    Returns:
        Boolean: True if email sent successfully, False otherwise
    """
    try:
        subject = f'Welcome to Manovastra, {name}!'
        
        # HTML message
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 32px;
                }}
                .header p {{
                    color: #FFE4B5;
                    margin: 10px 0 0 0;
                    font-size: 16px;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .welcome-message {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .welcome-message h2 {{
                    color: #8B4513;
                    font-size: 28px;
                    margin: 0 0 10px 0;
                }}
                .welcome-message p {{
                    color: #666;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .benefits {{
                    background: #FFF8DC;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 30px 0;
                }}
                .benefits h3 {{
                    color: #8B4513;
                    margin-top: 0;
                }}
                .benefit-item {{
                    display: flex;
                    align-items: center;
                    margin: 15px 0;
                }}
                .benefit-icon {{
                    width: 40px;
                    height: 40px;
                    background: #8B4513;
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 15px;
                    font-size: 20px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
                    color: white;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .social-links {{
                    margin: 20px 0;
                }}
                .social-links a {{
                    display: inline-block;
                    width: 35px;
                    height: 35px;
                    background: #8B4513;
                    color: white;
                    border-radius: 50%;
                    line-height: 35px;
                    margin: 0 5px;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Manovastra</h1>
                    <p>Elegance Redefined</p>
                </div>
                <div class="content">
                    <div class="welcome-message">
                        <h2>Welcome, {name}! 🎉</h2>
                        <p>Thank you for joining the Manovastra family. We're excited to have you with us!</p>
                    </div>
                    
                    <div class="benefits">
                        <h3>What You Can Enjoy:</h3>
                        <div class="benefit-item">
                            <div class="benefit-icon">✨</div>
                            <div>
                                <strong>Exclusive Collections</strong><br>
                                <span style="color: #666;">Access to premium ethnic wear</span>
                            </div>
                        </div>
                        <div class="benefit-item">
                            <div class="benefit-icon">🎁</div>
                            <div>
                                <strong>Special Offers</strong><br>
                                <span style="color: #666;">Member-only discounts and deals</span>
                            </div>
                        </div>
                        <div class="benefit-item">
                            <div class="benefit-icon">🚚</div>
                            <div>
                                <strong>Free Shipping</strong><br>
                                <span style="color: #666;">On orders above ₹999</span>
                            </div>
                        </div>
                        <div class="benefit-item">
                            <div class="benefit-icon">🔄</div>
                            <div>
                                <strong>Easy Returns</strong><br>
                                <span style="color: #666;">7-day hassle-free returns</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="http://127.0.0.1:8000/" class="cta-button">Start Shopping</a>
                    </div>
                    
                    <p style="text-align: center; color: #666; margin-top: 30px;">
                        Need assistance? Our customer support team is here to help!<br>
                        <a href="mailto:support@manovastra.com" style="color: #8B4513;">support@manovastra.com</a> | 
                        <a href="tel:+919876543210" style="color: #8B4513;">+91 98765 43210</a>
                    </p>
                </div>
                <div class="footer">
                    <div class="social-links">
                        <a href="#">📘</a>
                        <a href="#">📷</a>
                        <a href="#">🐦</a>
                        <a href="#">📺</a>
                    </div>
                    <p>Follow us on social media for latest updates and offers!</p>
                    <p style="margin-top: 15px;">© 2026 Manovastra. All Rights Reserved.</p>
                    <p>
                        <a href="#" style="color: #8B4513; text-decoration: none;">Privacy Policy</a> | 
                        <a href="#" style="color: #8B4513; text-decoration: none;">Terms & Conditions</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text message (fallback)
        plain_message = f"""
        Welcome to Manovastra, {name}!
        
        Thank you for joining the Manovastra family. We're excited to have you with us!
        
        What You Can Enjoy:
        ✨ Exclusive Collections - Access to premium ethnic wear
        🎁 Special Offers - Member-only discounts and deals
        🚚 Free Shipping - On orders above ₹999
        🔄 Easy Returns - 7-day hassle-free returns
        
        Start shopping now: http://127.0.0.1:8000/
        
        Need assistance?
        Email: support@manovastra.com
        Phone: +91 98765 43210
        
        © 2026 Manovastra. All Rights Reserved.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        return False


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    Args:
        order: Order object
    Returns:
        Boolean: True if email sent successfully, False otherwise
    """
    try:
        subject = f'Order Confirmed - {order.order_id}'
        
        # Calculate order items
        items_html = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    {item.product.name}<br>
                    <small style="color: #666;">Color: {item.color} | Qty: {item.quantity}</small>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    ₹{item.get_total()}
                </td>
            </tr>
            """
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .email-container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); padding: 30px; text-align: center; color: white; }}
                .content {{ padding: 30px; }}
                .order-box {{ background: #FFF8DC; border-radius: 10px; padding: 20px; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                .total-row {{ font-weight: bold; background: #f8f9fa; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Order Confirmed! ✅</h1>
                    <p>Thank you for your order</p>
                </div>
                <div class="content">
                    <h2>Hello {order.customer_name},</h2>
                    <p>Your order has been confirmed and is being processed.</p>
                    
                    <div class="order-box">
                        <h3>Order Details</h3>
                        <p><strong>Order ID:</strong> {order.order_id}</p>
                        <p><strong>Order Date:</strong> {order.created_at.strftime('%d %B %Y')}</p>
                        <p><strong>Payment Method:</strong> {order.get_payment_method_display()}</p>
                    </div>
                    
                    <h3>Items Ordered</h3>
                    <table>
                        {items_html}
                        <tr>
                            <td style="padding: 10px;"><strong>Subtotal:</strong></td>
                            <td style="padding: 10px; text-align: right;"><strong>₹{order.subtotal}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Delivery Charges:</td>
                            <td style="padding: 10px; text-align: right;">₹{order.delivery_charge}</td>
                        </tr>
                        <tr class="total-row">
                            <td style="padding: 15px;"><strong>Total Amount:</strong></td>
                            <td style="padding: 15px; text-align: right;"><strong>₹{order.total_amount}</strong></td>
                        </tr>
                    </table>
                    
                    <h3>Delivery Address</h3>
                    <p>
                        {order.address_line1}<br>
                        {order.address_line2}<br>
                        {order.city}, {order.state} - {order.pincode}
                    </p>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="http://127.0.0.1:8000/my-orders/" style="display: inline-block; background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold;">Track Your Order</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Need help? Contact us at support@manovastra.com</p>
                    <p>© 2026 Manovastra. All Rights Reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=f'Your order {order.order_id} has been confirmed.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending order confirmation email: {str(e)}")
        return False
