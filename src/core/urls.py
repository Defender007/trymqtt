from django.urls import path
from .views import TransactionView


urlpatterns = [
    path(
        "transactions",
        TransactionView.as_view(),
        name="transaction_list_api_view",
    ),
     path(
        "transactions/access-control",
        TransactionView.as_view(),
        name="transaction_create_api_view",
    ),
]
