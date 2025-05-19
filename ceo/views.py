from django.utils import timezone
from functools import wraps
from django.shortcuts import render, get_object_or_404
from main.models import  User
from  ceo.forms import MessageFormAll,MessageForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ceo.forms import MessageForm, UserForm
from main.models import Message, UserPagePermission
from django.views.decorators.http import require_POST
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from main.models import Payment, UserPagePermission

from django.contrib import messages

def company_code_check(company_code_value):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.company_code != company_code_value:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



@login_required
@require_POST
def toggle_user_active(request):
    user_id = request.POST.get('user_id')
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()


    active_user_count = User.objects.filter(is_active=True).count()
    inactive_user_count = User.objects.filter(is_active=False).count()

    return JsonResponse({
        'is_active': user.is_active,
        'active_user_count': active_user_count,
        'inactive_user_count': inactive_user_count
    })



@login_required
@company_code_check("ceo")
def ceo(request):
    # Fetch all users
    users = User.objects.all()
    user_count = users.count()
    messages_count = Message.objects.count()
    active_user_count = User.objects.filter(is_active=True).count()
    inactive_user_count = User.objects.filter(is_active=False).count()

    # Prepare user permissions
    user_permissions = {}
    for user in users:
        permissions = UserPagePermission.objects.filter(user=user).values_list('page_name', flat=True)
        modified_permissions = [
            'Dashboard' if perm == 'ceo' else
            'Payment' if perm == 'payment_list' else
            'Wordpress' if perm == 'project_toggle' else
            'Sales CRM' if perm == 'crm' else
            'Finance' if perm == 'finance_list' else
            perm for perm in permissions
        ]
        user_permissions[user.id] = modified_permissions

    # Add permissions to each user object for easier access in template
    for user in users:
        user.permissions = user_permissions.get(user.id, [])

    # Handle adding, editing, or deleting a user
    if request.method == "POST":
        if 'delete_user' in request.POST:  # Delete user logic
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, f"Foydalanuvchi {user.email} muvaffaqiyatli o‘chirildi.")
            return redirect('ceo')

        user_id = request.POST.get("user_id")
        if user_id:
            # Edit existing user
            user = get_object_or_404(User, id=user_id)
            form = UserForm(request.POST, instance=user)
        else:
            # Add new user
            form = UserForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f"Foydalanuvchi muvaffaqiyatli saqlandi.")
            return redirect('ceo')
        else:
            messages.error(request, "Forma xatolik bilan to'ldirildi. Qayta urining.")
    else:
        form = UserForm()

    return render(request, 'ceo.html', {
        'users': users,
        'user_count': user_count,
        'messages_count': messages_count,
        'active_user_count': active_user_count,
        'inactive_user_count': inactive_user_count,
        'form': form
    })

@login_required
@company_code_check("ceo")
def send_message_all(request):
    if request.method == 'POST':
        form = MessageFormAll(request.POST)
        if form.is_valid():
            message_data = form.save(commit=False)
            message_data.sender = request.user


            all_users = User.objects.all()


            for user in all_users:
                message = Message(
                    sender=request.user,
                    receiver=user,
                    subject=message_data.subject,
                    body=message_data.body,
                    sent_at=timezone.now()
                )
                message.save()

            return redirect('message_list_ceo')
    else:
        form = MessageFormAll()

    return render(request, 'send_message_all.html', {'form': form})


@login_required
@company_code_check("ceo")
def send_message(request, receiver_id=None):
    if receiver_id:
        receiver = get_object_or_404(User, id=receiver_id)
    else:
        receiver = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('message_list_ceo')
    else:
        form = MessageForm(initial={'receiver': receiver})

    return render(request, 'send_message.html', {'form': form, 'receiver': receiver})

from django.shortcuts import render


@login_required
def message_list(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-sent_at')
    company_code = request.user.company_code
    return render(request, 'message_list.html', {
        'received_messages': received_messages,
        'company_code': company_code,
    })

@login_required
@company_code_check("ceo")
def message_list_ceo(request):
    received_messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'message_list_ceo.html', {'received_messages': received_messages})



@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    return render(request, 'message_detail.html', {'message': message})



@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)

    if request.method == 'POST':
        message.delete()
        return redirect('message_list')

    return redirect('message_detail', message_id=message_id)



@login_required
def delete_message_ceo(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    if request.method == 'POST':
        message.delete()
        return redirect('message_list_ceo')

    return redirect('message_detail', message_id=message_id)



@login_required
def user_dashboard(request, company_code):

    user = get_object_or_404(User, company_code=company_code, id=request.user.id)

    if user.company_code == 'telegram':
        return redirect('index1')
    elif user.company_code == 'ceo':
        return redirect('ceo')
    elif user.company_code == 'logistic':
        return redirect('index')
    elif user.company_code=='service':
        return  redirect('service_all')
    elif user.company_code == 'consulting':
        return redirect('consulting')
    else:
        return redirect('default_dashboard')



@login_required
def payments_view(request):
    if request.method == "POST":
        # Add Payment
        if 'add_payment' in request.POST:
            project_name = request.POST.get('project_name')
            date = request.POST.get('date')
            summ = request.POST.get('summ')
            if project_name and date and summ:
                Payment.objects.create(
                    project=project_name,
                    date=date,
                    summ=summ,
                )
                return redirect('payment_list')

        # Edit Payment
        if 'edit_payment' in request.POST:
            payment_id = request.POST.get('id')
            project_name = request.POST.get('project_name')
            date_str = request.POST.get('date')
            summ = request.POST.get('summ')
            payment_status = request.POST.get('payment') == 'True'


            if payment_id and payment_id.isdigit() and project_name and date_str and summ:
                payment = Payment.objects.filter(id=payment_id).first()
                if payment:
                    try:
                        payment.project = project_name
                        payment.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        payment.summ = summ
                        payment.payment = payment_status
                        payment.save()
                        return JsonResponse({
                            'status': 'success',
                            'payment': {
                                'id': payment.id,
                                'project': payment.project,
                                'date': payment.date.strftime('%Y-%m-%d'),
                                'summ': float(payment.summ),
                                'payment_status': payment.payment
                            }
                        })
                    except Exception as e:
                        return JsonResponse({'status': 'error', 'message': str(e)})
                return JsonResponse({'status': 'error', 'message': 'Payment not found.'})
            return JsonResponse({'status': 'error', 'message': 'Missing required fields.'})

        # Delete Payment
        if 'delete_payment' in request.POST:
            payment_id = request.POST.get('id')
            if payment_id and payment_id.isdigit():
                Payment.objects.filter(id=payment_id).delete()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Invalid payment ID.'})

        # Toggle Payment Status
        if 'toggle_payment' in request.POST:
            payment_id = request.POST.get('id')
            if payment_id and payment_id.isdigit():
                payment = Payment.objects.filter(id=payment_id).first()
                if payment:
                    payment.payment = not payment.payment
                    payment.save()
                    return JsonResponse({
                        'status': 'success',
                        'payment': {
                            'id': payment.id,
                            'project': payment.project,
                            'date': payment.date.strftime('%Y-%m-%d'),
                            'summ': payment.summ,
                            'payment': payment.payment
                        }
                    })
            return JsonResponse({'status': 'error', 'message': 'Invalid payment ID.'})

    # Get Payments
    payments = Payment.objects.all()

    # Fetch and sort user permissions
    user = request.user
    permissions = UserPagePermission.objects.filter(user=user).values_list('page_name', flat=True)
    page_order = ['ceo', 'payment_list', 'project-toggle', 'crm', 'finance_list']
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

    return render(request, 'ceo_payment.html', {
        'payments': payments,
        'permissions': modified_permissions
    })

