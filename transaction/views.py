from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from master.models import CompanyProfile, Client, Service
from .forms import InvoiceForm, InvoiceLineItemForm, PaymentForm
from .models import Invoice, InvoiceLineItem, Payment

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


# -----------------------------
# Edit Invoice
# -----------------------------

@login_required
def edit_invoice(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == "POST":

        company = get_object_or_404(
            CompanyProfile,
            pk=request.POST.get("company")
        )

        client = get_object_or_404(
            Client,
            pk=request.POST.get("client")
        )

        services = request.POST.getlist("service[]")
        quantities = request.POST.getlist("qty[]")

        valid_services = [s for s in services if s != ""]

        if len(valid_services) == 0:

            messages.error(
                request,
                "Please add at least one service."
            )

            return redirect("edit_invoice", pk=invoice.pk)

        invoice.company = company
        invoice.client = client
        invoice.invoice_date = request.POST.get("invoice_date")
        invoice.discount = Decimal(
            request.POST.get("discount") or "0"
        )
        invoice.status = request.POST.get("status") or invoice.status
        invoice.notes = request.POST.get("notes") or ""

        # Recreate line items from scratch: remove the existing ones
        # (GstBreakdown rows cascade-delete along with them) and rebuild
        # so there's no risk of duplicates or orphaned records.
        invoice.items.all().delete()

        subtotal = Decimal("0")
        gst_total = Decimal("0")

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
            "Invoice Updated Successfully."
        )

        return redirect("invoice_list")

    invoice_form = InvoiceForm(instance=invoice)

    items = invoice.items.select_related("service").all()

    return render(

        request,

        "transaction/invoice_form.html",

        {

            "invoice_form": invoice_form,

            "invoice": invoice,

            "items": items,

            "services": Service.objects.filter(is_active=True),

        }

    )


# -----------------------------
# Delete Invoice
# -----------------------------

@login_required
def delete_invoice(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    invoice_number = invoice.invoice_number

    invoice.delete()

    messages.success(
        request,
        f"Invoice {invoice_number} deleted successfully."
    )

    return redirect("invoice_list")


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

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Payment Recorded Successfully."
            )

            return redirect("payment_list")

    else:

        form = PaymentForm()

    return render(
        request,
        "transaction/payment_form.html",
        {
            "form": form
        }
    )


@login_required
def edit_payment(request, pk):

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == "POST":

        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Payment Updated Successfully."
            )

            return redirect("payment_list")

    else:

        form = PaymentForm(instance=payment)

    return render(
        request,
        "transaction/payment_form.html",
        {
            "form": form,
            "payment": payment
        }
    )


@login_required
def delete_payment(request, pk):

    payment = get_object_or_404(Payment, pk=pk)

    payment.delete()

    messages.success(
        request,
        "Payment Deleted Successfully."
    )

    return redirect("payment_list")