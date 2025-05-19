from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'surname', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')  # Bu xatoga sabab bo'lgan qator
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')  # groups maydoni uchun





# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from main.models import User, UserPagePermission

class UserPagePermissionInline(admin.TabularInline):
    model = UserPagePermission
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'surname', 'company_code', 'role', 'is_active', 'page_permissions_display', 'edit_permissions')
    list_filter = ('company_code', 'role', 'is_active')
    search_fields = ('email', 'name', 'surname')
    inlines = [UserPagePermissionInline]

    def page_permissions_display(self, obj):
        permissions = obj.page_permissions.all().values_list('page_name', flat=True)
        return ", ".join(permissions) if permissions else "No permissions"
    page_permissions_display.short_description = 'Page Permissions'

    def edit_permissions(self, obj):
        return f'<a href="/admin/custom/edit-permissions/{obj.id}/" class="button">Edit</a>'
    edit_permissions.allow_tags = True
    edit_permissions.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('edit-permissions/<int:user_id>/', self.admin_site.admin_view(self.edit_permissions_view), name='edit_permissions'),
        ]
        return custom_urls + urls

    def edit_permissions_view(self, request, user_id):
        user = User.objects.get(id=user_id)
        if request.method == 'POST':
            UserPagePermission.objects.filter(user=user).delete()
            selected_pages = request.POST.getlist('pages')
            for page in selected_pages:
                UserPagePermission.objects.create(user=user, page_name=page)
            messages.success(request, f"Ruxsatlar {user.email} uchun muvaffaqiyatli yangilandi.")
            return HttpResponseRedirect("/admin/auth/user/")

        all_pages = [
            ('ceo', 'Dashboard'),
            ('payment_list', 'Payment'),
            ('project-toggle', 'WordPress'),
            ('crm', 'Sales CRM'),
            ('finance_list', 'Finance'),
        ]
        current_permissions = user.page_permissions.values_list('page_name', flat=True)

        return render(request, 'admin/edit_permissions.html', {
            'user': user,
            'all_pages': all_pages,
            'current_permissions': current_permissions,
        })


