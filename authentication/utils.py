# utils.py
def redirect_user_by_type(user):
    if user.user_type == 'student':
        return redirect('student_dashboard')
    elif user.user_type == 'client':
        return redirect('client_dashboard')
    elif user.user_type == 'staff':
        return redirect('staff_dashboard')
