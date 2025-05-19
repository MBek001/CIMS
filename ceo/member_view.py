from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from main.models import User, CreditCard, MonthlyUpdate, UserPagePermission
from datetime import datetime
import random
from datetime import datetime, date  # Added 'date' import
import random
import requests  # Bot so'rovi uchun (taqlidiy)


@login_required
def member_dashboard(request):
    user = request.user
    if user.role != 'Member':
        return redirect('ceo' if user.role == 'CEO' else 'login')

    # Fetch user's credit cards
    credit_cards = CreditCard.objects.filter(user=user)
    primary_card = credit_cards.filter(is_primary=True).first()
    secondary_card = credit_cards.filter(is_primary=False).first()

    # Fetch all monthly updates for table display
    monthly_updates = MonthlyUpdate.objects.filter(user=user).order_by('-update_date')

    # Check if new month has started
    latest_update = monthly_updates.first()
    today = date.today()
    current_year_month = (today.year, today.month)
    if not latest_update or (latest_update.update_date.year, latest_update.update_date.month) != current_year_month:
        update_monthly_percentage(user)
        monthly_updates = MonthlyUpdate.objects.filter(user=user).order_by('-update_date')

    # Fetch permissions for sidebar
    permissions = UserPagePermission.objects.filter(user=user).values_list('page_name', flat=True)
    page_order = ['ceo', 'payment_list', 'project_toggle', 'crm', 'finance_list']
    modified_permissions = []
    for page in page_order:
        if page in permissions:
            modified_permissions.append(
                'Dashboard' if page == 'ceo' else
                'Payment' if page == 'payment_list' else
                'Wordpress' if page == 'project_toggle' else
                'Sales CRM' if page == 'crm' else
                'Finance' if page == 'finance_list' else
                page
            )

    # Handle user profile edit
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            try:
                new_name = request.POST.get('name')
                new_surname = request.POST.get('surname')
                new_email = request.POST.get('email')
                new_telegram_id = request.POST.get('telegram_id', '')
                new_password = request.POST.get('password')

                # Tekshirish: Email allaqachon ishlatilganmi
                if new_email != user.email and User.objects.filter(email=new_email).exists():
                    messages.error(request, "Bu email allaqachon ro‘yxatdan o‘tgan!")
                    return redirect('member_dashboard')

                # Ma’lumotlarni yangilash (default_salary tahrirlanmaydi)
                user.name = new_name
                user.surname = new_surname
                user.email = new_email
                user.telegram_id = new_telegram_id
                if new_password:
                    user.set_password(new_password)

                # Foydalanuvchi ob'ektini saqlash
                user.save()

                # Sessiyani yangilash
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                messages.success(request, "Profil muvaffaqiyatli yangilandi!")
                return redirect('member_dashboard')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
                return redirect('member_dashboard')

        # Handle credit card add/edit
        elif 'update_cards' in request.POST:
            primary_card_number = request.POST.get('primary_card')
            secondary_card_number = request.POST.get('secondary_card')

            # Primary card
            if primary_card_number and len(primary_card_number) == 16 and primary_card_number.isdigit():
                if primary_card:
                    primary_card.card_number = primary_card_number
                    primary_card.save()
                else:
                    if CreditCard.objects.filter(user=user, is_primary=True).count() == 0:
                        CreditCard.objects.create(user=user, card_number=primary_card_number, is_primary=True)
            elif primary_card and not primary_card_number:
                primary_card.delete()

            # Secondary card
            if secondary_card_number and len(secondary_card_number) == 16 and secondary_card_number.isdigit():
                if secondary_card:
                    secondary_card.card_number = secondary_card_number
                    secondary_card.save()
                else:
                    if CreditCard.objects.filter(user=user, is_primary=False).count() == 0:
                        CreditCard.objects.create(user=user, card_number=secondary_card_number, is_primary=False)
            elif secondary_card and not secondary_card_number:
                secondary_card.delete()

            update_monthly_percentage(user)
            messages.success(request, "Kredit kartalar muvaffaqiyatli yangilandi!")
            return redirect('member_dashboard')

    return render(request, 'member_dashboard.html', {
        'user': user,
        'primary_card': primary_card,
        'secondary_card': secondary_card,
        'monthly_updates': monthly_updates,
        'permissions': modified_permissions
    })


def update_monthly_percentage(user):
    today = date.today()
    last_update = MonthlyUpdate.objects.filter(user=user).order_by('-update_date').first()
    current_year_month = (today.year, today.month)

    # Yangi oy boshlangan bo'lsa yoki hech qanday yangilanish bo'lmasa
    if not last_update or (last_update.update_date.year, last_update.update_date.month) != current_year_month:
        # Botga so'rov yuborish (taqlidiy)
        try:
            # Haqiqiy bot API so'rovi (placeholder)
            # response = requests.post('http://your-bot-api.com/get_percentage', data={'telegram_id': user.telegram_id})
            # percentage = response.json().get('percentage', random.uniform(0.5, 5.0))
            percentage = 100

            # potential_monthly = default_salary * (update_percentage / 100)
            potential_monthly = float(user.default_salary)
            print(potential_monthly)
            MonthlyUpdate.objects.create(
                user=user,
                update_percentage=percentage,
                potential_monthly=potential_monthly,
                update_date=today
            )
        except Exception as e:
            # Bot so'rovi muvaffaqiyatsiz bo'lsa, default qiymat
            percentage = 100
            potential_monthly = float(user.default_salary)
            MonthlyUpdate.objects.create(
                user=user,
                update_percentage=percentage,
                potential_monthly=potential_monthly,
                update_date=today
            )