from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('pricing/', views.pricing_page, name='pricing'),
    path('how-it-works/', views.how_it_works_page, name='how_it_works'),
    path('features/', views.features_page, name='features'),
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

    path('console/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('console/clients/', views.AdminClientListView.as_view(), name='admin_clients'),
    path('console/clients/create/', views.AdminClientCreateView.as_view(), name='admin_client_create'),
    path('console/clients/<int:pk>/edit/', views.AdminClientUpdateView.as_view(), name='admin_client_edit'),
    path('console/clients/<int:pk>/delete/', views.AdminClientDeleteView.as_view(), name='admin_client_delete'),

    path('console/agents/', views.AdminAgentListView.as_view(), name='admin_agents'),
    path('console/agents/create/', views.AdminAgentCreateView.as_view(), name='admin_agent_create'),
    path('console/agents/<int:pk>/edit/', views.AdminAgentUpdateView.as_view(), name='admin_agent_edit'),
    path('console/agents/<int:pk>/delete/', views.AdminAgentDeleteView.as_view(), name='admin_agent_delete'),

    path('console/transactions/', views.AdminTransactionListView.as_view(), name='admin_transactions'),
    path('console/transactions/<int:pk>/edit/', views.AdminTransactionUpdateView.as_view(), name='admin_transaction_edit'),
    path('console/transactions/<int:pk>/delete/', views.AdminTransactionDeleteView.as_view(), name='admin_transaction_delete'),
    path('console/reports/', views.AdminReportsView.as_view(), name='admin_reports'),
    path('console/reports/clients.csv', views.export_clients_csv, name='export_clients_csv'),
    path('console/reports/agents.csv', views.export_agents_csv, name='export_agents_csv'),
    path('console/reports/transactions.csv', views.export_transactions_csv, name='export_transactions_csv'),
]
