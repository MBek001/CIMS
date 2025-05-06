from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from ceo.forms import FinanceForm
from ceo.models import Finance


class FinanceListView(ListView):
    model = Finance
    template_name = 'ceo_finance.html'
    context_object_name = 'finances'
    ordering = ['-date']  # Changed from -created_at to -date to match your template
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FinanceForm()
        return context


def finance_create(request):
    if request.method == 'POST':
        form = FinanceForm(request.POST)
        if form.is_valid():
            finance = form.save()
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'service': finance.service,
                'summ': str(finance.summ),  # Convert to string to avoid JSON serialization issues
                'date': finance.date.strftime('%Y-%m-%d')  # Format date as string
            })
        return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('finance_list')


def finance_update(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        form = FinanceForm(request.POST, instance=finance)
        if form.is_valid():
            finance = form.save()
            return JsonResponse({
                'success': True,
                'id': finance.id,
                'type': finance.type,
                'status': finance.status,
                'service': finance.service,
                'summ': str(finance.summ),
                'date': finance.date.strftime('%Y-%m-%d')
            })
        return JsonResponse({'success': False, 'errors': form.errors})

    # For GET requests (when clicking edit button)
    return JsonResponse({
        'id': finance.id,
        'type': finance.type,
        'status': finance.status,
        'service': finance.service,
        'summ': str(finance.summ),
        'date': finance.date.strftime('%Y-%m-%d')
    })


def finance_delete(request, pk):
    finance = get_object_or_404(Finance, pk=pk)
    if request.method == 'POST':
        finance.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})