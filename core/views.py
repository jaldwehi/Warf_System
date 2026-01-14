from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.decorators import face_required

@login_required
def role_redirect(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        return redirect("admin_dashboard")
    return redirect("employee_home")


@login_required
def employee_home(request):
    return HttpResponse("Employee Portal")


@login_required
@face_required
def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")


@login_required
def role_redirect(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")    
    return redirect("employee_dashboard")