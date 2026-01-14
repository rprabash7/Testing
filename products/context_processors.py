from .models import SiteSetting, Category

def site_settings(request):
    """Make site settings available in all templates"""
    try:
        settings = SiteSetting.objects.first()
    except:
        settings = None
    
    # Get all active categories for navigation
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    return {
        'site_settings': settings,
        'nav_categories': categories,  # ✅ Add this
        'is_logged_in': request.session.get('is_logged_in', False),
        'user_name': request.session.get('user_name', ''),
    }
