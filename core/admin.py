from django.contrib import admin
from .models import ClientProfile, AgentProfile, Transaction, AgentRequest


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('created_at',)


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_online')
    list_filter = ('is_online',)
    actions = ['make_online', 'make_offline']
    
    def make_online(self, request, queryset):
        for agent in queryset:
            agent.go_online()
        self.message_user(request, f'{queryset.count()} agent(s) are now online.')
    
    def make_offline(self, request, queryset):
        for agent in queryset:
            agent.go_offline()
        self.message_user(request, f'{queryset.count()} agent(s) are now offline.')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'platform', 'currency', 'amount', 'amount_to_receive', 'status', 'created_at')
    list_filter = ('status', 'platform', 'currency', 'payment_method', 'created_at')
    search_fields = ('client__first_name', 'client__last_name', 'transfer_address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AgentRequest)
class AgentRequestAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'requested_at', 'expires_at', 'is_accepted', 'is_expired')
    list_filter = ('is_accepted', 'is_expired', 'requested_at')
