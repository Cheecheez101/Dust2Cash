from django.contrib import admin
from django.utils import timezone
from .models import AdminProfile, ClientProfile, AgentProfile, Transaction, AgentRequest, AgentApplication


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'phone_number')


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


@admin.register(AgentApplication)
class AgentApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'country', 'status', 'submitted_at')
    list_filter = ('status', 'country', 'has_aml_policy', 'accepts_background_check')
    search_fields = ('full_name', 'email', 'phone_number', 'id_number')
    readonly_fields = ('submitted_at', 'reviewed_at', 'reviewed_by')
    actions = ['mark_verified', 'mark_cancelled']

    def mark_verified(self, request, queryset):
        updated = queryset.update(status=AgentApplication.STATUS_VERIFIED, reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"{updated} application(s) marked as verified")

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=AgentApplication.STATUS_CANCELLED, reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"{updated} application(s) marked as cancelled")

    mark_verified.short_description = 'Mark selected applications as verified'
    mark_cancelled.short_description = 'Mark selected applications as cancelled'
