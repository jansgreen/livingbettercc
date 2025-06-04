# users/decorators.py
from django.shortcuts import redirect

def user_type_required(required_type):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.user_type != required_type:
                return redirect('no_access')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

student_required = user_type_required('student')
client_required = user_type_required('client')
staff_required = user_type_required('staff')
