from typing import Any
from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
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
