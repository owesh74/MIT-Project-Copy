from django.contrib import admin
from .models import Invoice, InvoiceLineItem, GstBreakdown, Payment

admin.site.register(Invoice)
admin.site.register(InvoiceLineItem)
admin.site.register(GstBreakdown)
admin.site.register(Payment)