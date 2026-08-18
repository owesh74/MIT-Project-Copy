from django import forms
from .models import CompanyProfile, GstConfiguration, Client, Service


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = "__all__"

        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "owner_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.TextInput(attrs={"class": "form-control", "placeholder": "www.example.com"}),
            "gst_number": forms.TextInput(attrs={"class": "form-control"}),
            "pan_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control"}),
            "account_number": forms.TextInput(attrs={"class": "form-control"}),
            "ifsc_code": forms.TextInput(attrs={"class": "form-control"}),
            "company_logo": forms.FileInput(attrs={"class": "form-control"}),
        }


class GstConfigurationForm(forms.ModelForm):
    class Meta:
        model = GstConfiguration
        fields = "__all__"

        widgets = {
            "gst_name": forms.TextInput(attrs={"class": "form-control"}),
            "gst_percentage": forms.NumberInput(attrs={"class": "form-control"}),
            "cgst": forms.NumberInput(attrs={"class": "form-control"}),
            "sgst": forms.NumberInput(attrs={"class": "form-control"}),
            "igst": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "gst_number": forms.TextInput(attrs={"class": "form-control"}),
            "pan_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        exclude = ["service_code"]

        widgets = {
            "service_name": forms.TextInput(attrs={"class": "form-control"}),
            "hsn_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 998313"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "gst": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


