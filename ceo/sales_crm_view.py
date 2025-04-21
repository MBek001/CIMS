from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from . import models
from .models import Customer
from .forms import CustomerForm
from .views import company_code_check


@login_required(login_url='')
@company_code_check("ceo")
def crm_view(request):
    form = CustomerForm()
    edit_id = request.POST.get('edit_id')
    show_all = False  # Default

    if request.method == 'POST':
        if 'save_edit' in request.POST:
            customer = get_object_or_404(Customer, pk=edit_id)
            form = CustomerForm(request.POST, instance=customer)
            if form.is_valid():
                form.save()
                return redirect(f"{reverse('crm')}#customer-{edit_id}")
        elif 'edit_id' in request.POST:
            pass
        elif 'add_customer' in request.POST:
            form = CustomerForm(request.POST)
            if form.is_valid():
                new_customer = form.save()
                return redirect(f"{reverse('crm')}#customer-{new_customer.id}")
        elif 'see_all' in request.POST:
            show_all = True

    query = request.GET.get('search')
    if query and query.strip():
        customers = Customer.objects.filter(
            Q(full_name__icontains=query) |
            Q(platform__icontains=query) |
            Q(username__icontains=query) |
            Q(assistant_name__icontains=query) |
            Q(status__icontains=query)
        ).order_by('-created_at')
    elif show_all:
        customers = Customer.objects.all().order_by('-created_at')
    else:
        customers = Customer.objects.all().order_by('-created_at')[:4]

    return render(request, 'crm_page.html', {
        'form': CustomerForm(),
        'customers': customers,
        'edit_id': int(edit_id) if edit_id else None,
    })





@login_required(login_url='')
@company_code_check("ceo")
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect(f"{reverse('crm')}#customer-deleted")





