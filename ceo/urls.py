from ceo import views, wordpres_projects_view, sales_crm_view
from django.urls import path

from ceo.finance import FinanceListView, finance_transfer,finance_create, finance_update, finance_delete

urlpatterns = [
    path('ceo/',views.ceo,name='ceo'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('messages/', views.message_list, name='message_list'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('message/deleteceo/<int:message_id>/', views.delete_message_ceo, name='delete_message_ceo'),
    path('messagesceo/',views.message_list_ceo,name='message_list_ceo'),
    path('dashboard/<str:company_code>/', views.user_dashboard, name='user_dashboard'),
    path('message/send-to-all/', views.send_message_all, name='send_message_to_all'),
    path('toggle_user_active/', views.toggle_user_active, name='toggle_user_active'),
    path('payments/', views.payments_view, name='payment_list'),
    path('project-toggle/', wordpres_projects_view.project_toggle_view, name='project_toggle'),
    path('api/site-status/', wordpres_projects_view.site_status),
    path('crm/', sales_crm_view.crm_view, name='crm'),
    path('crm/delete/<int:pk>/', sales_crm_view.delete_customer, name='delete_customer'),
    path('finance/', FinanceListView.as_view(), name='finance_list'),
    path('create/', finance_create, name='finance_create'),
    path('<int:pk>/update/', finance_update, name='finance_update'),
    path('<int:pk>/delete/', finance_delete, name='finance_delete'),
    # path('finance/api/transactions/', finance_transactions_api, name='finance_transactions_api'),
    path('finance/transfer/', finance_transfer, name='finance_transfer'),


]
