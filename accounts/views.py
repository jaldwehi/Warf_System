from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import EmployeeCreateForm, EmployeeUpdateForm

import os
import uuid

from .models import Profile
from accounts.services.faceREC.face import verify_face, FACE_DB

User = get_user_model()


# -------------------------
# Access Helpers (Final)
# -------------------------
def is_admin(user):
    return user.is_authenticated and user.is_superuser


def admin_required(view_func):
    """
    Admin-only decorator (WARF policy).
    """
    return login_required(user_passes_test(is_admin, login_url="login")(view_func))


# -------------------------
# Public Pages
# -------------------------
def home(request):
    # Landing page (NOT dashboard)
    return render(request, "public/home.html")


def login_view(request):
    """
    Login using username OR email + password.
    Redirect rule:
      - superuser -> admin_dashboard
      - otherwise -> employee_dashboard
    """
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_superuser else "employee_dashboard")

    error = None

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        # 1) try username
        user = authenticate(request, username=identifier, password=password)

        # 2) if failed, try email
        if user is None:
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("admin_dashboard" if user.is_superuser else "employee_dashboard")

        error = "Invalid username/email or password."

    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------
# Dashboards
# -------------------------
@admin_required
def admin_dashboard(request):
    return render(request, "dashboards/admin_dashboard.html")


@login_required
def employee_dashboard(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    return render(request, "dashboards/employee_dashboard.html")

@login_required
def profile_view(request):
    """
    Self profile page (for current logged-in user).
    """
    profile = Profile.objects.select_related("user").filter(user=request.user).first()

    # إذا لسبب ما ما فيه Profile للمستخدم
    if profile is None:
        # خيار 1: تنشئينه تلقائيًا (إذا تبين)
        # profile = Profile.objects.create(user=request.user)
        return render(request, "accounts/profile.html", {"profile": None})

    return render(request, "accounts/profile.html", {"profile": profile})

# -------------------------
# Employees Management (Admin-only)
# -------------------------
@admin_required
def employee_list(request):
    profiles = Profile.objects.select_related("user").all().order_by("user__username")

    total = profiles.count()
    active_count = profiles.filter(status="active").count()
    suspended_count = profiles.filter(status="suspended").count()
    left_count = profiles.filter(status="left").count()

    return render(request, "accounts/employee_list.html", {
        "profiles": profiles,
        "total": total,
        "active_count": active_count,
        "suspended_count": suspended_count,
        "left_count": left_count,
    })



@admin_required
def employee_toggle_status(request, pk):
    """
    Admin-only: Toggle between active <-> suspended quickly.
    (Left status should be set explicitly from a dedicated UI later.)
    """
    profile = Profile.objects.select_related("user").get(pk=pk)

    if profile.status == "active":
        profile.status = "suspended"
        profile.user.is_active = False
    else:
        profile.status = "active"
        profile.user.is_active = True

    profile.user.save()
    profile.save()
    return redirect("accounts:employee_list")


# -------------------------
# Face Verification (KEEP)
# Not used in login flow. Used in meetings join flow.
# -------------------------
@login_required
def face_verify(request):
    result = None

    if request.method == "POST" and request.FILES.get("face_image"):
        img = request.FILES["face_image"]

        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}_{img.name}"
        temp_path = os.path.join(temp_dir, filename)

        with open(temp_path, "wb+") as f:
            for chunk in img.chunks():
                f.write(chunk)

        # Current behavior: allow comparison against FACE_DB identities
        authorized = list(FACE_DB.keys())
        result = verify_face(temp_path, authorized)

        try:
            os.remove(temp_path)
        except Exception:
            pass

        if result and result.get("approved"):
            request.session["face_verified"] = True

    return render(request, "accounts/face_verify.html", {"result": result})

@admin_required
def employee_create(request):
    if request.method == "POST":
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Employee created: {user.username}")
            return redirect("accounts:employee_list")
    else:
        form = EmployeeCreateForm()

    return render(request, "accounts/employee_create.html", {"form": form})


@admin_required
def employee_edit(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    user = profile.user

    if request.method == "POST":
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee updated: {user.username}")
            return redirect("accounts:employee_list")
    else:
        form = EmployeeUpdateForm(instance=user, profile=profile)

    return render(request, "accounts/employee_edit.html", {
        "form": form,
        "profile": profile,
        "employee_user": user,
    })
