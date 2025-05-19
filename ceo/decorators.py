from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from main.models import UserPagePermission

# Eski dekorator (company_code tekshiruvi)
def company_code_check(company_code_value):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.company_code != company_code_value:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Yangi dekorator (faqat page ruxsatlarini tekshiradi)
def restrict_page_access(page_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')

            # Superuser bo‘lsa, barcha sahifalarga kirish huquqi bor
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Agar company_code "oddiy" bo‘lmasa, faqat company_code ga asoslanib ishlaydi
            if user.company_code != "oddiy":
                return view_func(request, *args, **kwargs)

            # Agar company_code "oddiy" bo‘lsa, faqat page ruxsatlarini tekshiradi
            has_permission = UserPagePermission.objects.filter(
                user=user,
                page_name=page_name
            ).exists()

            if not has_permission:
                return HttpResponseForbidden("Sizda bu sahifaga kirish huquqi yo‘q.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator





