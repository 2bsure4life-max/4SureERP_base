from .permissions import has_permission

def authorize(user_role, required_permission):
    """Middleware check before rendering a view"""
    if has_permission(user_role, required_permission):
        return True
    else:
        return False  # Block access (we can redirect to 'Access Denied')

