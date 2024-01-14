from typing import Any
from django import forms 
from .models import Transaction

class Transactionform(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super.__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True 
        self.fields['transaction_type'].widget = forms.HiddenInput() 

    def save(self, commit: True):
        self.instance.account = self.account 
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
class Depostieform(Transactionform):
    def clean_amount(self):
        min_depo_amount=100
        amount = self.cleaned_data.get('amount')
        if amount < min_depo_amount:
            raise forms.ValidationError(
                f'you need at least {min_depo_amount} to deposite'
            )
        return amount 
    
class WithdrawForm(Transactionform):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdrw = 20000
        balance = self.balance
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'you need withdraw at least {min_withdraw_amount} '
            )
        
        if amount > max_withdrw:
            raise forms.ValidationError(
                f'you can withdraw maximum {max_withdrw}'
            )
        
        if amount > balance:
            raise forms.ValidationError(
                f'you have {balance} in your account'
            )
        
        return amount
    
class LoanRegForm(Transactionform):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
    
        return amount