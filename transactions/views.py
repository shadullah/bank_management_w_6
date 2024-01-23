from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import Depositform, WithdrawForm, LoanReqForm
from .constants import DEPOSIT,WITHDRAW,LOAN,LOAN_PAID
from django.contrib import messages
from datetime import datetime
from django.db import Sum
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
    
class LoanReqView(TransactionCreateMix):
    form_class = LoanReqForm
    title = "request for Loan"

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        
        current_loan_cnt = Transaction.objects.filter(account = self.request.user.account, transaction_type=3, loan_approve = True).count()

        if current_loan_cnt>=3:
            return HttpResponse('you have crossed your limits')

        messages.success(self.request, f"Loan request for {amount}$ was sent to your account successfully")
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = ""
    model = Transaction
    balance = 0

    def get_queryset(self):
        # jodi user kono filter na kore taile full data show krbe
        queryset = super().get_queryset().filter(
            account = self.request.user.account 
        )
        
        start_data_str = self.request.GET.get('start_date')
        end_data_str = self.request.GET.get('end_date')

        if start_data_str and end_data_str:
            start_date = datetime.strptime(start_data_str, "%Y-%m-%d").date() 
            end_date = datetime.strptime(end_data_str, "%Y-%m-%d").date()

            # queryset = queryset.filter(timestamp_date_gte = start_date, timestamp_date_lte = end_date).aggregate(sum('amount'))['amount__sum'] 

            self.balance = Transaction.objects.filter(timestamp_date_gte = start_date, timestamp_date_lte = end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account 
        })
        return context
    
