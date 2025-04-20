from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ceo.models import SiteControl
from django.http import JsonResponse

from ceo.views import company_code_check


@login_required(login_url='')
@company_code_check("ceo")
def project_toggle_view(request):
    site_control = SiteControl.objects.first()
    if not site_control:
        site_control = SiteControl.objects.create(is_site_on=True)

    if request.method == 'POST':
        action = request.POST.get('toggle_site')
        if action == 'toggle':
            site_control.is_site_on = not site_control.is_site_on
            site_control.save()

    return render(request, 'wordpres_projects.html', {'site_status': site_control.is_site_on})



def site_status(request):
    site_control = SiteControl.objects.first()
    return JsonResponse({'is_site_on': site_control.is_site_on if site_control else True})