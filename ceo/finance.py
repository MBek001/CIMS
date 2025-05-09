from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from ceo.forms import FinanceForm
from ceo.models import Finance
from datetime import datetime
from django.views.decorators.http import require_POST

class FinanceListView(ListView):
    model = Finance
    template_name = 'ceo_finance.html'
    context_object_name = 'finances'
    ordering = ['-date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FinanceForm()
        return context

def finance_create(request):
    if request.method == 'POST':
        post_data = {
            'type': request.POST.get('type', ''),
            'status': request.POST.get('status', ''),
            'card': request.POST.get('card', ''),
            'service': request.POST.get('service', ''),
            'summ': request.POST.get('summ', ''),
            'date': request.POST.get('date', '')
        }
        if post_data['date']:
            try:
                post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
            except ValueError:
                post_data['date'] = None
        else:
            post_data['date'] = None

        form = FinanceForm(post_data)
        if form.is_valid():
            finance = form.save()
            formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'card': finance.card,
                'service': finance.service,
                'summ': str(finance.summ),
                'date': formatted_date,
                'message': 'Muvaffiqiyatli q\'oshildi'
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
            'date': request.POST.get('date', '')
        }
        if post_data['date']:
            try:
                post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
            except ValueError:
                post_data['date'] = finance.date
        else:
            post_data['date'] = finance.date

        form = FinanceForm(post_data, instance=finance)
        if form.is_valid():
            finance = form.save()
            formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'card': finance.card,
                'service': finance.service,
                'summ': str(finance.summ),
                'date': formatted_date,
                'message': 'Muvaffiqiyatli yangilandi'
            })
        print("Form errors:", form.errors)
        return JsonResponse({'success': False, 'errors': form.errors})

    formatted_date = finance.date.strftime('%Y-%m-%d') if finance.date else ''
    return JsonResponse({
        'id': finance.id,
        'type': finance.type,
        'status': finance.status,
        'card': finance.card,
        'service': finance.service,
        'summ': str(finance.summ),
        'date': formatted_date
    })

def finance_delete(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        finance.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@require_POST
def finance_transfer(request):
    from_card = request.POST.get('from_card')
    to_card = request.POST.get('to_card')
    amount = request.POST.get('amount')

    if not all([from_card, to_card, amount]):
        return JsonResponse({'success': False, 'error': 'All fields are required'})

    if from_card == to_card:
        return JsonResponse({'success': False, 'error': 'Cannot transfer to the same card'})

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid amount'})

    # Create two transactions: one outgoing, one incoming
    today = datetime.now().date()
    from_finance = Finance.objects.create(
        type='outcomer',
        status='one_time',
        card=from_card,
        service=f'Transfer to {to_card}',
        summ=amount,
        date=today
    )
    to_finance = Finance.objects.create(
        type='incomer',
        status='one_time',
        card=to_card,
        service=f'Transfer from {from_card}',
        summ=amount,
        date=today
    )

    return JsonResponse({
        'success': True,
        'from_id': from_finance.id,
        'to_id': to_finance.id,
        'from_card': from_card,
        'to_card': to_card,
        'amount': str(amount),
        'date': today.strftime('%Y-%m-%d')
    })