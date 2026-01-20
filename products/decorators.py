from django.shortcuts import redirect
from functools import wraps

def login_required_custom(view_func):
    """
    Custom login required decorator using session
    Redirects to login page if user is not logged in
    Stores the requested URL to redirect back after login
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.session.get('is_logged_in', False):
            # Store the requested URL to redirect back after login
            request.session['next_url'] = request.get_full_path()
            # Redirect to login page
            return redirect('login')
        
        # User is logged in, proceed with the view
        return view_func(request, *args, **kwargs)
    
    return wrapper
