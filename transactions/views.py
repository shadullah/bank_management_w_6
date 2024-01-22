from typing import Any
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import Depositform, WithdrawForm, LoanReqForm
from .constants import DEPOSIT,WITHDRAW,LOAN,LOAN_PAID
from django.contrib import messages

# Create your views here.

class TransactionCreateMix(LoginRequiredMixin,CreateView):
    template_name = ''
    model = Transaction
    title = ''
    success_url= ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account':self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title 
        })

class depostieView(TransactionCreateMix):
    form_class = Depositform
    title = "Deposit"

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )

        messages.success(self.request, f"{amount}$ was deposited to your account successfully")
        return super().form_valid(form)


class WithdrawView(TransactionCreateMix):
    form_class = WithdrawForm
    title = "Withdraw"

    def get_initial(self):
        initial = {'transaction_type': WITHDRAW}
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields = ['balance']
        )

        messages.success(self.request, f"{amount}$ was WITHDRAWED from your account successfully")
        return super().form_valid(form)