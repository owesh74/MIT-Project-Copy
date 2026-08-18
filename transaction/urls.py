from django.urls import path
from . import views

urlpatterns = [

    # Invoice
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoice/add/", views.add_invoice, name="add_invoice"),
    path("invoice/save/", views.save_invoice, name="save_invoice"),
    path("invoice/edit/<int:pk>/", views.edit_invoice, name="edit_invoice"),
    path("invoice/delete/<int:pk>/", views.delete_invoice, name="delete_invoice"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("service/<int:pk>/", views.service_details, name="service_details"),

    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/add/", views.add_payment, name="add_payment"),
    path("payments/edit/<int:pk>/", views.edit_payment, name="edit_payment"),
    path("payments/delete/<int:pk>/", views.delete_payment, name="delete_payment"),

    # Quotations
    path("quotations/", views.quotation_list, name="quotation_list"),
    path("quotation/add/", views.add_quotation, name="add_quotation"),
    path("quotation/save/", views.save_quotation, name="save_quotation"),
    path("quotation/edit/<int:pk>/", views.edit_quotation, name="edit_quotation"),
    path("quotation/delete/<int:pk>/", views.delete_quotation, name="delete_quotation"),
    path("quotations/<int:pk>/pdf/", views.quotation_pdf, name="quotation_pdf"),

]


