
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, LoginForm
from django.http import JsonResponse
from main.models import Payment
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from .models import UserPagePermission
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

def custom_page_not_found(request, exception):

    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print(f"Attempting to authenticate user with email: {email}")  # Debug
            user = authenticate(request, username=email, password=password)

            if user is not None:
                print(f"User authenticated successfully: {user}")  # Debug
                if user.is_active:
                    print("User is active, logging in...")  # Debug
                    login(request, user, backend='main.auth_backends.EmailBackend')

                    # Role’ni tekshirish: Agar Member bo‘lsa, member_dashboard’ga yo‘naltirish
                    if user.role == 'Member':
                        print("User role is Member, redirecting to member_dashboard")  # Debug
                        return redirect('member_dashboard')

                    # Agar role Member bo‘lmasa, mavjud logikaga o‘tish
                    valid_company_codes = ['telegram', 'ceo', 'logistic', 'consulting', 'service']
                    print(f"User company_code: {user.company_code}")  # Debug

                    if user.company_code in valid_company_codes:
                        print(f"Redirecting based on company_code: {user.company_code}")  # Debug
                        if user.company_code == 'telegram':
                            return redirect('index1')
                        elif user.company_code == 'ceo':
                            return redirect('ceo')
                        elif user.company_code == 'logistic':
                            return redirect('index')
                        elif user.company_code == 'consulting':
                            return redirect('consulting')
                        elif user.company_code == 'service':
                            return redirect('service_all')
                    else:
                        permissions = list(UserPagePermission.objects.filter(user=user).values_list('page_name', flat=True))
                        print(f"User permissions: {permissions}")  # Debug

                        if permissions:
                            first_permission = permissions[0]
                            print(f"First permission: {first_permission}")  # Debug

                            redirect_map = {
                                'ceo': 'ceo',
                                'crm': 'crm',
                                'payment_list': 'payment_list',
                                'finance_list': 'finance_list',
                                'project_toggle': 'project_toggle',
                                'dashboard': 'user_dashboard',
                            }

                            redirect_url = redirect_map.get(first_permission)
                            if redirect_url:
                                print(f"Redirecting to: {redirect_url}")  # Debug
                                if redirect_url == 'user_dashboard':
                                    return redirect('user_dashboard', company_code=user.company_code)
                                return redirect(redirect_url)
                            else:
                                print(f"Unknown permission: {first_permission}")  # Debug
                                return HttpResponseForbidden(f"Noma'lum ruxsat: {first_permission}. Iltimos, administrator bilan bog'laning.")
                        else:
                            print("No permissions found for user.")  # Debug
                            return HttpResponseForbidden("Sizda hech qanday sahifaga kirish huquqi yo‘q.")

                else:
                    print("User is inactive.")  # Debug
                    return render(request, 'signin.html', {
                        'form': form,
                        'invalid': True,
                        'error_message': 'Your account is inactive. Please contact support.'
                    })
            else:
                print("Authentication failed.")  # Debug
                return render(request, 'signin.html', {'form': form, 'invalid': True})

    else:
        form = LoginForm()

    print("Rendering login page.")  # Debug
    return render(request, 'signin.html', {'form': form, 'invalid': False})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'signup.html', {'form': form})




def logout_view(request):
    logout(request)
    return redirect('login')



def payment_status(request, project_name):
    try:
        payment = Payment.objects.get(project=project_name)
        return JsonResponse({
            "project": payment.project,
            "payment": payment.payment
        })
    except Payment.DoesNotExist:
        return JsonResponse({
            "error": "Project not found"
        }, status=404)







