from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from cims import settings
from main.models import UserPagePermission

from . import models
from .models import Customer
from .forms import CustomerForm
from .views import company_code_check
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from ceo.serializers import CustomerSerializer
from django.http import JsonResponse


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
        elif 'delete_id' in request.POST:
            customer = get_object_or_404(Customer, pk=request.POST.get('delete_id'))
            customer.delete()
            return redirect(reverse('crm'))

    if request.method == 'DELETE':
        try:
            data = json.loads(request.body.decode('utf-8'))
            customer_id = data.get('id')
            if not customer_id:
                return JsonResponse({'status': 'error', 'message': 'Customer ID is required'}, status=400)
            customer = get_object_or_404(Customer, pk=customer_id)
            customer.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    query = request.GET.get('search')
    selected_status = request.GET.get('status')

    if query and query.strip():
        customers = Customer.objects.filter(
            Q(full_name__icontains=query) |
            Q(platform__icontains=query) |
            Q(phone_number=query) |
            Q(username__icontains=query) |
            Q(assistant_name__icontains=query) |
            Q(status__icontains=query)
        )
    elif show_all or not selected_status:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(status=selected_status)

    customers = customers.order_by('-created_at')

    # Calculate status statistics
    status_stats = Customer.objects.aggregate(
        total_customers=Count('id'),
        need_to_call=Count('id', filter=Q(status='need_to_call')),
        contacted=Count('id', filter=Q(status='contacted')),
        project_started=Count('id', filter=Q(status='project_started')),
        continuing=Count('id', filter=Q(status='continuing')),
        finished=Count('id', filter=Q(status='finished')),
        rejected=Count('id', filter=Q(status='rejected'))
    )

    # Get dynamic status counts for any additional statuses
    status_counts = Customer.objects.values('status').annotate(
        count=Count('status')
    ).order_by('status')

    # Convert to dictionary for easier template access
    status_dict = {item['status']: item['count'] for item in status_counts}

    # Calculate percentages (optional)
    total = status_stats['total_customers']
    status_percentages = {}
    if total > 0:
        for status_key, count in status_dict.items():
            status_percentages[status_key] = round((count / total) * 100, 1)

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
        'status_choices': Customer.STATUS_CHOICES,
        'selected_status': selected_status,
        'status_stats': status_stats,
        'status_dict': status_dict,
        'status_percentages': status_percentages,
    })


@login_required(login_url='')
@company_code_check("ceo")
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect(f"{reverse('crm')}#customer-deleted")


class CustomerCreateAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.headers.get('X-API-TOKEN')

        if token != settings.COGNILABS_API_SECRET:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
