from django.urls import path
from . import views

urlpatterns = [

    # Invoice
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoice/add/", views.add_invoice, name="add_invoice"),
    path("invoice/save/", views.save_invoice, name="save_invoice"),
    path("service/<int:pk>/", views.service_details, name="service_details"),

    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/add/", views.add_payment, name="add_payment"),
    path("payments/edit/<int:pk>/", views.edit_payment, name="edit_payment"),
    path("payments/delete/<int:pk>/", views.delete_payment, name="delete_payment"),

]