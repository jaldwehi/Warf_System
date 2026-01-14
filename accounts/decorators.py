from django.shortcuts import redirect
from django.urls import reverse

def face_required(view_func):
    def _wrapped(request, *args, **kwargs):
        # لازم يكون مسجل دخول + وجهه متحقق
        if not request.user.is_authenticated:
            return redirect("login")  # اسم صفحة الدخول عندك غالباً login

        if not request.session.get("face_verified"):
            return redirect(reverse("face_verify"))

        return view_func(request, *args, **kwargs)
    return _wrapped
