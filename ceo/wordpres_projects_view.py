from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ceo.models import SiteControl
from django.http import JsonResponse
from  main.models import  UserPagePermission
from ceo.views import company_code_check


@login_required(login_url='')
def project_toggle_view(request):
    site_control = SiteControl.objects.first()
    if not site_control:
        site_control = SiteControl.objects.create(is_site_on=True)

    if request.method == 'POST':
        action = request.POST.get('toggle_site')
        if action == 'toggle':
            site_control.is_site_on = not site_control.is_site_on
            site_control.save()

    # Fetch and sort user permissions
    user = request.user
    permissions = UserPagePermission.objects.filter(user=user).values_list('page_name', flat=True)
    # Define desired order of pages
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

    return render(request, 'wordpres_projects.html', {
        'site_status': site_control.is_site_on,
        'permissions': modified_permissions  # Ruxsatlarni kontekstga qo‘shish
    })



def site_status(request):
    site_control = SiteControl.objects.first()
    return JsonResponse({'is_site_on': site_control.is_site_on if site_control else True})