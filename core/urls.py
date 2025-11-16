from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('client/profile/', views.client_profile, name='client_profile'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client/transaction/create/', views.create_transaction, name='create_transaction'),
    path('client/transaction/<int:transaction_id>/request-agent/', views.request_agent, name='request_agent'),
    path('client/transaction/<int:transaction_id>/address/', views.request_address, name='request_address'),
    
    path('agent/portal/', views.agent_portal, name='agent_portal'),
    path('agent/request/<int:request_id>/accept/', views.agent_accept_request, name='agent_accept_request'),
    path('agent/transaction/<int:transaction_id>/provide-address/', views.agent_provide_address, name='agent_provide_address'),
    path('agent/transaction/<int:transaction_id>/confirm-receipt/', views.agent_confirm_receipt, name='agent_confirm_receipt'),
    path('agent/transaction/<int:transaction_id>/send-payment/', views.agent_send_payment, name='agent_send_payment'),
]
