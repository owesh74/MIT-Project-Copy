from django import forms
from .models import Invoice, InvoiceLineItem, Payment, Quotation, QuotationLineItem


class InvoiceForm(forms.ModelForm):

    class Meta:

        model = Invoice

        fields = [
            "company",
            "client",
            "invoice_date",
            "discount",
            "status",
            "notes",
        ]

        widgets = {

            "company": forms.Select(attrs={"class": "form-select"}),

            "client": forms.Select(attrs={"class": "form-select"}),

            "invoice_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "discount": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "status": forms.Select(
                attrs={"class": "form-select"}
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

        }


class InvoiceLineItemForm(forms.ModelForm):

    class Meta:

        model = InvoiceLineItem

        fields = [
            "service",
            "quantity",
        ]

        widgets = {

            "service": forms.Select(
                attrs={"class": "form-select"}
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1
                }
            ),

        }


class PaymentForm(forms.ModelForm):

    class Meta:

        model = Payment

        fields = [
            "invoice",
            "payment_date",
            "payment_mode",
            "transaction_id",
            "amount",
            "remarks",
        ]

        widgets = {

            "invoice": forms.Select(attrs={"class": "form-select"}),

            "payment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "payment_mode": forms.Select(attrs={"class": "form-select"}),

            "transaction_id": forms.TextInput(attrs={"class": "form-control"}),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0.01,
                    "step": "0.01"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount


class QuotationForm(forms.ModelForm):

    class Meta:

        model = Quotation

        fields = [
            "company",
            "client",
            "quote_date",
            "valid_until",
            "prepared_by",
            "gst",
            "other_charges",
            "terms_and_conditions",
            "status",
        ]

        widgets = {

            "company": forms.Select(attrs={"class": "form-select"}),

            "client": forms.Select(attrs={"class": "form-select"}),

            "quote_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "valid_until": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "prepared_by": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "gst": forms.Select(attrs={"class": "form-select"}),

            "other_charges": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "terms_and_conditions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

            "status": forms.Select(
                attrs={"class": "form-select"}
            ),

        }


class QuotationLineItemForm(forms.ModelForm):

    class Meta:

        model = QuotationLineItem

        fields = [
            "service",
            "description",
            "hsn_code",
            "quantity",
            "rate",
        ]

        widgets = {

            "service": forms.Select(
                attrs={"class": "form-select"}
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2
                }
            ),

            "hsn_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1
                }
            ),

            "rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

        }


