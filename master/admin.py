from django.contrib import admin
from .models import CompanyProfile, GstConfiguration, Client, Service


admin.site.register(CompanyProfile)
admin.site.register(GstConfiguration)
admin.site.register(Client)
admin.site.register(Service)