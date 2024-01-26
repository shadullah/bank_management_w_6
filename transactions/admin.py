from django.contrib import admin
from .models import Transaction
from .views import send_transacton_email
# Register your models here.
# admin.site.register(Transaction)
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']

    def save_model(self, request, obj, form, change):
        if obj.loan_approve == True:
            obj.account.balance += obj.amount
            obj.balance_after_transaction = obj.account.balance 
            send_transacton_email(obj.account, obj.amount, "Loan approval", "transactions/admin_email.html")
            obj.account.save()
        super().save_model(request, obj, form, change)