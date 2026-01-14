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
