from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import CreateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import Depositform, WithdrawForm, LoanReqForm
from .constants import DEPOSIT,WITHDRAW,LOAN,LOAN_PAID
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from transactions.models import Transaction
# Create your views here.

def send_transacton_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user': user ,
        'amount': amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

class TransactionCreateMix(LoginRequiredMixin,CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url= reverse_lazy('report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context

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
        send_transacton_email(self.request.user, amount, "Deposite message", "transactions/deposite_email.html")
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
        send_transacton_email(self.request.user, amount, "Withrawal message", "transactions/withdrawal_email.html")
        messages.success(self.request, f"{amount}$ was WITHDRAWED from your account successfully")
        return super().form_valid(form)
    
class LoanReqView(TransactionCreateMix):
    form_class = LoanReqForm
    title = "Request For Loan"

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        
        current_loan_cnt = Transaction.objects.filter(account = self.request.user.account, transaction_type=3, loan_approve = True).count()

        if current_loan_cnt>=3:
            return HttpResponse('you have crossed your limits')
        send_transacton_email(self.request.user, amount, "Loan message", "transactions/loan_email.html")
        messages.success(self.request, f"Loan request for {amount}$ was sent to your account successfully")
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transactions/transaction_report.html"
    model = Transaction
    balance = 0

    def get_queryset(self):
        # jodi user kono filter na kore taile full data show krbe
        queryset = super().get_queryset().filter(
            account = self.request.user.account 
        )
        
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() 
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date)

            self.balance = Transaction.objects.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account 
        })
        return context
    
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id = loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, f"loan amount is greater than available balance")
                
        return redirect('loan_list')
            
class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/loan_request.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account = user_account, transaction_type = 3)
        return queryset