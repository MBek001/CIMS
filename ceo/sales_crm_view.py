from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from main.models import  UserPagePermission

from . import models
from .models import Customer
from .forms import CustomerForm
from .views import company_code_check

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from ceo.serializers import CustomerSerializer

@login_required(login_url='')

def crm_view(request):
    form = CustomerForm()
    edit_id = request.POST.get('edit_id')
    show_all = False

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
    selected_status = request.GET.get('status')  # Get the selected status from GET parameters

    # Initialize the customer queryset
    if query and query.strip():
        customers = Customer.objects.filter(
            Q(full_name__icontains=query) |
            Q(platform__icontains=query) |
            Q(phone_number=query) |
            Q(username__icontains=query) |
            Q(assistant_name__icontains=query) |
            Q(status__icontains=query)
        )
    elif show_all:
        customers = Customer.objects.all()
    else:
        # Default to 'contacted' status if no status is selected
        customers = Customer.objects.filter(status='contacted') if not selected_status else Customer.objects.filter(status=selected_status)

    customers = customers.order_by('-created_at')

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
                'Wordpress' if page == 'project-toggle' else
                'Sales CRM' if page == 'crm' else
                'Finance' if page == 'finance_list' else
                page
            )

    return render(request, 'crm_page.html', {
        'form': CustomerForm(),
        'customers': customers,
        'edit_id': int(edit_id) if edit_id else None,
        'permissions': modified_permissions,
        'status_choices': Customer.STATUS_CHOICES,  # Pass status choices to template
        'selected_status': selected_status,  # Pass selected status to template
    })




@login_required(login_url='')
@company_code_check("ceo")
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect(f"{reverse('crm')}#customer-deleted")





class CustomerCreateAPIView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

