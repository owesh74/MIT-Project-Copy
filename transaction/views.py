from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from master.models import CompanyProfile, Client, Service
from .forms import InvoiceForm
from .models import Invoice, InvoiceLineItem
from django.http import JsonResponse, HttpResponse
from .forms import InvoiceForm, InvoiceLineItemForm

# -----------------------------
# Dashboard Invoice List
# -----------------------------

@login_required
def invoice_list(request):

    invoices = Invoice.objects.all().order_by("-id")

    return render(
        request,
        "transaction/invoice_list.html",
        {
            "invoices": invoices
        }
    )


# -----------------------------
# Create Invoice Page
# -----------------------------
@login_required
def add_invoice(request):

    invoice_form = InvoiceForm()

    item_form = InvoiceLineItemForm()

    return render(

        request,

        "transaction/invoice_form.html",

        {

            "invoice_form": invoice_form,

            "item_form": item_form,

            "services": Service.objects.filter(is_active=True),

        }

    )

# -----------------------------
# Service API
# -----------------------------

@login_required
def service_details(request, pk):

    service = get_object_or_404(Service, pk=pk)

    return JsonResponse({

        "id": service.id,

        "name": service.service_name,

        "price": float(service.price),

        "gst": float(service.gst.gst_percentage)

    })


# -----------------------------
# Save Invoice
# -----------------------------

@login_required
@require_POST
def save_invoice(request):

    company = get_object_or_404(
        CompanyProfile,
        pk=request.POST.get("company")
    )

    client = get_object_or_404(
        Client,
        pk=request.POST.get("client")
    )

    invoice = Invoice.objects.create(

        company=company,

        client=client,

        invoice_date=request.POST.get("invoice_date"),

        discount=Decimal(
            request.POST.get("discount") or "0"
        ),

        status=request.POST.get("status") or "Draft",

        notes=request.POST.get("notes")

    )

    subtotal = Decimal("0")
    gst_total = Decimal("0")

    services = request.POST.getlist("service[]")
    quantities = request.POST.getlist("qty[]")

    if len(services) == 0:

        messages.error(
            request,
            "Please add at least one service."
        )

        invoice.delete()

        return redirect("add_invoice")

    for service_id, qty in zip(services, quantities):

        if service_id == "":
            continue

        service = get_object_or_404(
            Service,
            pk=service_id
        )

        quantity = Decimal(qty)

        price = Decimal(service.price)

        gst_percent = Decimal(
            service.gst.gst_percentage
        )

        line_subtotal = price * quantity

        gst_amount = (
            line_subtotal * gst_percent
        ) / Decimal("100")

        total = line_subtotal + gst_amount

        InvoiceLineItem.objects.create(

            invoice=invoice,

            service=service,

            quantity=quantity,

            price=price,

            gst_percentage=gst_percent,

            gst_amount=gst_amount,

            total=total

        )

        subtotal += line_subtotal

        gst_total += gst_amount

    invoice.subtotal = subtotal

    invoice.gst_amount = gst_total

    invoice.grand_total = (

        subtotal +

        gst_total -

        invoice.discount

    )

    invoice.save()

    messages.success(
        request,
        "Invoice Created Successfully."
    )

    return redirect("invoice_list")

from .models import Payment


@login_required
def payment_list(request):

    payments = Payment.objects.all().order_by("-id")

    return render(
        request,
        "transaction/payment_list.html",
        {
            "payments": payments
        }
    )


@login_required
def add_payment(request):
    return HttpResponse("Add Payment Page")


@login_required
def edit_payment(request, pk):
    return HttpResponse("Edit Payment")


@login_required
def delete_payment(request, pk):
    return HttpResponse("Delete Payment")