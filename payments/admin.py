from django.contrib import admin
from .models import PaymentMethod, Payment, Invoice, Refund


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'payment_type', 'is_active', 'min_amount', 'max_amount', 'fees_percentage']
    list_filter = ['payment_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'payment_type', 'description', 'logo', 'is_active')
        }),
        ('Configuration API', {
            'fields': ('api_key', 'api_secret', 'merchant_id'),
            'classes': ('collapse',)
        }),
        ('Paramètres', {
            'fields': ('min_amount', 'max_amount', 'fees_percentage', 'fees_fixed')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'course', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'currency']
    search_fields = ['payment_id', 'user__username', 'user__email', 'course__title', 'transaction_id']
    readonly_fields = ['payment_id', 'created_at', 'updated_at', 'completed_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('payment_id', 'transaction_id')
        }),
        ('Relations', {
            'fields': ('user', 'course', 'payment_method')
        }),
        ('Montants', {
            'fields': ('amount', 'fees', 'total_amount', 'currency')
        }),
        ('Statut et dates', {
            'fields': ('status', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Informations supplémentaires', {
            'fields': ('phone_number', 'reference', 'notes'),
            'classes': ('collapse',)
        }),
        ('Données API', {
            'fields': ('api_response',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_completed()
        self.message_user(request, f"{queryset.count()} paiements marqués comme terminés.")
    mark_as_completed.short_description = "Marquer comme terminés"
    
    def mark_as_failed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_failed("Marqué comme échoué par l'administrateur")
        self.message_user(request, f"{queryset.count()} paiements marqués comme échoués.")
    mark_as_failed.short_description = "Marquer comme échoués"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} paiements annulés.")
    mark_as_cancelled.short_description = "Annuler les paiements"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'payment', 'billing_name', 'issue_date', 'due_date']
    list_filter = ['issue_date', 'due_date']
    search_fields = ['invoice_number', 'billing_name', 'billing_email']
    readonly_fields = ['invoice_number', 'issue_date']
    date_hierarchy = 'issue_date'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'status', 'requested_at', 'processed_at', 'processed_by']
    list_filter = ['status', 'requested_at', 'processed_at']
    search_fields = ['payment__payment_id', 'payment__user__username', 'reason']
    readonly_fields = ['requested_at', 'processed_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Dates', {
            'fields': ('requested_at', 'processed_at')
        }),
        ('Traitement', {
            'fields': ('processed_by', 'admin_notes')
        }),
    )
    
    actions = ['approve_refunds', 'reject_refunds']
    
    def approve_refunds(self, request, queryset):
        queryset.update(status='completed', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} remboursements approuvés.")
    approve_refunds.short_description = "Approuver les remboursements"
    
    def reject_refunds(self, request, queryset):
        queryset.update(status='rejected', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} remboursements rejetés.")
    reject_refunds.short_description = "Rejeter les remboursements"