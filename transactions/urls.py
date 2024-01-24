from django.urls import path 
from .views import depostieView, WithdrawView, TransactionReportView, LoanReqView, LoanListView, PayLoanView

urlpatterns = [
    path("deposit/", depostieView.as_view(), name='deposit'),
    path("report/", TransactionReportView.as_view(), name='report'),
    path("withdraw/", WithdrawView.as_view(), name='withdraw'),
    path("loan_request/", LoanReqView.as_view(), name='loan_request'),
    path("loans/", LoanListView.as_view(), name='loan_list'),
    path("loan/<int:loan_id>/", PayLoanView.as_view(), name='loan_pay'),
    
]
