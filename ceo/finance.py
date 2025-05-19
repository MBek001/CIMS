from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Finance, DonationBalance, ExchangeRate
from  main.models import  User
from .forms import FinanceForm
from main.models import UserPagePermission
from django.utils import timezone



def is_ceo_or_finance_director(user):
    return user.is_authenticated and user.company_code in ['ceo', 'finance_director']

class FinanceListView(ListView):
    model = Finance
    template_name = 'ceo_finance.html'
    context_object_name = 'finances'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FinanceForm()
        donation_balance = DonationBalance.get_or_create()
        context['donation_balance'] = donation_balance.total_donation

        # User permissions
        user = self.request.user
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
                    'Finance' if page == 'finance_list' else page
                )
        context['permissions'] = modified_permissions

        # Exchange rate
        exchange_rate = ExchangeRate.get_current_rate()
        context['exchange_rate'] = "{:,.2f}".format(exchange_rate)

        # Card balances calculation (only real transactions)
        card1_balance = Decimal('0')  # Company Account UZB (UZS)
        card2_balance = Decimal('0')  # Uzcard UZB (UZS)
        card3_balance = Decimal('0')  # Company Account US (USD)
        potential_income = Decimal('0')
        potential_outcome = Decimal('0')

        today = timezone.now().date()
        next_30 = today + timedelta(days=30)

        for finance in Finance.objects.all():
            # Donation ni mos valyutaga aylantirish
            donation_in_currency = finance.donation
            if finance.currency == 'USD':
                # donation UZS da saqlangan, uni USD ga aylantiramiz
                donation_in_currency = finance.donation / finance.exchange_rate
            else:
                # donation allaqachon UZS da
                donation_in_currency = finance.donation

            # Net amount calculation based on transaction type
            if finance.type == 'incomer':
                netto_amount = finance.summ - donation_in_currency
            else:  # outcomer
                netto_amount = -finance.summ

            netto_amount_uzs = netto_amount * exchange_rate if finance.currency == 'USD' else netto_amount

            # Real transactions affect card balances immediately
            if finance.transaction_status == 'real':
                if finance.card == 'card1':
                    card1_balance += netto_amount_uzs
                elif finance.card == 'card2':
                    card2_balance += netto_amount_uzs
                elif finance.card == 'card3':
                    card3_balance += netto_amount

            # Statistical transactions affect potential balance
            elif finance.transaction_status == 'statistical' and today < finance.date <= next_30:
                if finance.type == 'incomer':
                    potential_income += netto_amount_uzs
                else:  # outcomer
                    potential_outcome += abs(netto_amount_uzs)

            # Monthly transactions
            if finance.status == 'monthly':
                repeat_date = finance.initial_date  # Initial date dan boshlaymiz
                while repeat_date <= next_30:
                    # Agar takrorlanish sanasi bugungi kun bo'lsa va tranzaksiya real bo'lsa
                    if repeat_date == today and finance.transaction_status == 'real':
                        if finance.card == 'card1':
                            card1_balance += netto_amount_uzs
                        elif finance.card == 'card2':
                            card2_balance += netto_amount_uzs
                        elif finance.card == 'card3':
                            card3_balance += netto_amount
                    # Agar takrorlanish sanasi bugundan keyin va 30 kun ichida bo'lsa
                    if today <= repeat_date <= next_30:
                        if finance.type == 'incomer':
                            potential_income += netto_amount_uzs
                        else:  # outcomer
                            potential_outcome += abs(netto_amount_uzs)
                    # Increment by one month
                    year = repeat_date.year + (repeat_date.month // 12)
                    month = repeat_date.month % 12 + 1
                    day = min(repeat_date.day, [31, 28 if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0) else 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
                    repeat_date = repeat_date.replace(year=year, month=month, day=day)

        total_balance = card1_balance + card2_balance + (card3_balance * exchange_rate)
        potential_balance = total_balance + potential_income - potential_outcome

        members = User.objects.filter(role='Member')
        member_data = []
        for member in members:
            credit_cards = member.credit_cards.filter(is_active=True).values('card_number', 'is_primary')
            member_data.append({
                'name': member.name,
                'surname': member.surname,
                'cards': [{'card_number': card['card_number'], 'is_primary': card['is_primary']} for card in
                          credit_cards]  # To'liq raqam
            })
        context['member_data'] = member_data

        # Format amounts for display
        context['card1_balance'] = "{:,.2f}".format(card1_balance)
        context['card2_balance'] = "{:,.2f}".format(card2_balance)
        context['card3_balance'] = "{:,.2f}".format(card3_balance)
        context['total_balance'] = "{:,.2f}".format(total_balance)
        context['potential_balance'] = "{:,.2f}".format(potential_balance)

        return context

def finance_create(request):
    if request.method == 'POST':
        post_data = {
            'type': request.POST.get('type', ''),
            'status': request.POST.get('status', ''),
            'card': request.POST.get('card', ''),
            'service': request.POST.get('service', ''),
            'summ': request.POST.get('summ', ''),
            'currency': request.POST.get('currency', ''),
            'date': request.POST.get('date', ''),
            'donation_percentage': request.POST.get('donation_percentage', ''),
        }

        # Card-based currency
        if post_data['card'] in ['card1', 'card2']:
            post_data['currency'] = 'UZS'
        elif post_data['card'] == 'card3':
            post_data['currency'] = 'USD'

        if post_data['date']:
            try:
                post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
            except ValueError:
                post_data['date'] = None
        else:
            post_data['date'] = None

        if post_data['donation_percentage']:
            post_data['donation_percentage'] = Decimal(post_data['donation_percentage'])
        else:
            post_data['donation_percentage'] = Decimal('0')

        form = FinanceForm(post_data)
        if form.is_valid():
            finance = form.save(commit=False)
            finance.exchange_rate = ExchangeRate.get_current_rate()
            if finance.type == 'incomer' and finance.donation_percentage > 0:
                # Donation ni USD da hisoblaymiz, keyin UZS ga aylantirib saqlaymiz
                donation_in_currency = finance.summ * (finance.donation_percentage / 100)
                if finance.currency == 'USD':
                    finance.donation = donation_in_currency * finance.exchange_rate
                else:
                    finance.donation = donation_in_currency
                donation_balance = DonationBalance.get_or_create()
                donation_balance.total_donation += finance.donation
                donation_balance.save()
            else:
                finance.donation = Decimal('0')
            finance.save()
            formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'card': finance.card,
                'card_display': finance.get_card_display(),
                'service': finance.service,
                'summ': str(finance.summ),
                'currency': finance.currency,
                'date': formatted_date,
                'donation': str(finance.donation),
                'donation_percentage': str(finance.donation_percentage),
                'exchange_rate': str(finance.exchange_rate),
                'transaction_status': finance.transaction_status,
                'message': 'Muvaffaqiyatli qo‘shildi'
            })
        print("Form errors:", form.errors)
        return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('finance_list')

def finance_update(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        post_data = {
            'type': request.POST.get('type', ''),
            'status': request.POST.get('status', ''),
            'card': request.POST.get('card', ''),
            'service': request.POST.get('service', ''),
            'summ': request.POST.get('summ', ''),
            'currency': request.POST.get('currency', ''),
            'date': request.POST.get('date', ''),
            'donation_percentage': request.POST.get('donation_percentage', ''),
        }
        if post_data['date']:
            try:
                post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
            except ValueError:
                post_data['date'] = finance.date
        else:
            post_data['date'] = finance.date

        if post_data['donation_percentage']:
            post_data['donation_percentage'] = Decimal(post_data['donation_percentage'])
        else:
            post_data['donation_percentage'] = Decimal('0')

        old_donation = finance.donation
        form = FinanceForm(post_data, instance=finance)
        if form.is_valid():
            finance = form.save(commit=False)
            finance.exchange_rate = ExchangeRate.get_current_rate()
            donation_balance = DonationBalance.get_or_create()
            if old_donation:
                donation_balance.total_donation -= old_donation
            if finance.type == 'incomer' and finance.donation_percentage > 0:
                donation_in_currency = finance.summ * (finance.donation_percentage / 100)
                if finance.currency == 'USD':
                    finance.donation = donation_in_currency * finance.exchange_rate
                else:
                    finance.donation = donation_in_currency
                donation_balance.total_donation += finance.donation
            else:
                finance.donation = Decimal('0')
            donation_balance.save()
            finance.save()
            formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'card': finance.card,
                'card_display': finance.get_card_display(),
                'service': finance.service,
                'summ': str(finance.summ),
                'currency': finance.currency,
                'date': formatted_date,
                'donation': str(finance.donation),
                'donation_percentage': str(finance.donation_percentage),
                'exchange_rate': str(finance.exchange_rate),
                'transaction_status': finance.transaction_status,
                'message': 'Muvaffaqiyatli yangilandi'
            })
        print("Form errors:", form.errors)
        return JsonResponse({'success': False, 'errors': form.errors})

    formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
    return JsonResponse({
        'id': finance.id,
        'type': finance.type,
        'status': finance.status,
        'card': finance.card,
        'card_display': finance.get_card_display(),
        'service': finance.service,
        'summ': str(finance.summ),
        'currency': finance.currency,
        'date': formatted_date,
        'donation': str(finance.donation),
        'donation_percentage': str(finance.donation_percentage),
        'exchange_rate': str(finance.exchange_rate),
        'transaction_status': finance.transaction_status
    })

def finance_delete(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        donation_balance = DonationBalance.get_or_create()
        if finance.donation:
            donation_balance.total_donation -= finance.donation
            donation_balance.save()
        finance.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@require_POST
def finance_transfer(request):
    from_card = request.POST.get('from_card')
    to_card = request.POST.get('to_card')
    amount = request.POST.get('amount')
    tax_percentage = request.POST.get('tax_percentage', '0')

    if not all([from_card, to_card, amount]):
        return JsonResponse({'success': False, 'error': 'Barcha maydonlar (From Card, To Card, Amount) to‘ldirilishi kerak'})

    if from_card == to_card:
        return JsonResponse({'success': False, 'error': 'Bir xil kartaga o‘tkazib bo‘lmaydi'})

    try:
        amount = Decimal(amount)
        tax_percentage = Decimal(tax_percentage)
        if amount <= 0 or tax_percentage < 0 or tax_percentage > 100:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Noto‘g‘ri summa yoki tax foizi'})

    exchange_rate = ExchangeRate.get_current_rate()
    currency = 'UZS' if from_card in ['card1', 'card2'] else 'USD'
    tax_amount = amount * (tax_percentage / 100)
    net_amount = amount - tax_amount

    today = timezone.now().date()
    from_finance = Finance.objects.create(
        type='outcomer',
        status='one_time',
        card=from_card,
        service=f'Transfer to {to_card}',
        summ=amount,
        currency=currency,
        date=today,
        tax_percentage=tax_percentage,
        donation=0,
        exchange_rate=exchange_rate,
        transaction_status='real'
    )

    to_currency = 'UZS' if to_card in ['card1', 'card2'] else 'USD'
    if from_card == 'card3' and to_card in ['card1', 'card2']:
        net_amount_converted = net_amount * exchange_rate
    elif from_card in ['card1', 'card2'] and to_card == 'card3':
        net_amount_converted = net_amount / exchange_rate
    else:
        net_amount_converted = net_amount

    to_finance = Finance.objects.create(
        type='incomer',
        status='one_time',
        card=to_card,
        service=f'Transfer from {from_card}',
        summ=net_amount_converted,
        currency=to_currency,
        date=today,
        tax_percentage=tax_percentage,
        donation=0,
        exchange_rate=exchange_rate,
        transaction_status='real'
    )

    return JsonResponse({
        'success': True,
        'from_id': from_finance.id,
        'to_id': to_finance.id,
        'from_card': from_card,
        'from_card_display': from_finance.get_card_display(),
        'to_card': to_card,
        'to_card_display': to_finance.get_card_display(),
        'amount': str(amount),
        'currency': currency,
        'tax_percentage': str(tax_percentage),
        'net_amount': str(net_amount_converted),
        'to_currency': to_currency,
        'exchange_rate': str(exchange_rate),
        'date': today.strftime('%Y-%m-%d')
    })

@require_POST
@user_passes_test(is_ceo_or_finance_director)
def reset_donation_balance(request):
    donation_balance = DonationBalance.get_or_create()
    donation_balance.total_donation = Decimal('0')
    donation_balance.updated_by = request.user
    donation_balance.save()
    return JsonResponse({'success': True, 'message': 'Donation balansi muvaffaqiyatli 0 qilindi'})