from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from . import models
from .models import Customer
from .forms import CustomerForm
from .views import company_code_check


@login_required(login_url='')
@company_code_check("ceo")
def crm_view(request):
    form = CustomerForm()

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crm')  # Prevent resubmission on refresh

    query = request.GET.get('search')
    if query and query.strip():  # Only search if query exists and is not empty
        customers = Customer.objects.filter(
            Q(full_name__icontains=query) |
            Q(platform__icontains=query) |
            Q(username__icontains=query) |
            Q(assistant_name__icontains=query)
        ).order_by('-created_at')
    else:
        customers = Customer.objects.order_by('-created_at')[:4]  # Default to last 4

    return render(request, 'crm_page.html', {
        'form': form,
        'customers': customers
    })
