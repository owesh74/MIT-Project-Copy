from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from master.models import CompanyProfile, Client, Service, GstConfiguration
from .forms import (
    InvoiceForm, InvoiceLineItemForm, PaymentForm,
    QuotationForm, QuotationLineItemForm,
)
from .models import Invoice, InvoiceLineItem, Payment, Quotation, QuotationLineItem
from .pdf import build_invoice_pdf, build_quotation_pdf

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


# -----------------------------
# Download Invoice PDF
# -----------------------------

@login_required
def invoice_pdf(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    buffer = build_invoice_pdf(invoice)

    response = HttpResponse(buffer.read(), content_type="application/pdf")

    filename = f"Invoice_{invoice.invoice_number}.pdf"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


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


# =========================================================
# QUOTATIONS
# =========================================================

@login_required
def quotation_list(request):

    quotations = Quotation.objects.all().order_by("-id")

    return render(
        request,
        "transaction/quotation_list.html",
        {
            "quotations": quotations
        }
    )


@login_required
def add_quotation(request):

    quotation_form = QuotationForm()

    item_form = QuotationLineItemForm()

    gst_options = GstConfiguration.objects.filter(is_active=True)

    return render(

        request,

        "transaction/quotation_form.html",

        {

            "quotation_form": quotation_form,

            "item_form": item_form,

            "services": Service.objects.filter(is_active=True),

            "gst_options": gst_options,

            "gst_rates_json": {
                str(g.id): float(g.gst_percentage) for g in gst_options
            },

        }

    )


def _build_quotation_items(quotation, request):
    """
    Rebuild the quotation's line items from POST data and return
    (subtotal, item_count). Existing items are expected to already
    be cleared by the caller before this runs.
    """

    descriptions = request.POST.getlist("description[]")
    hsn_codes = request.POST.getlist("hsn_code[]")
    quantities = request.POST.getlist("qty[]")
    rates = request.POST.getlist("rate[]")
    service_ids = request.POST.getlist("service[]")

    subtotal = Decimal("0")
    count = 0

    for i, description in enumerate(descriptions):

        description = (description or "").strip()

        if description == "":
            continue

        try:
            quantity = Decimal(quantities[i] or "0")
            rate = Decimal(rates[i] or "0")
        except (InvalidOperation, IndexError):
            continue

        if quantity <= 0:
            continue

        service = None
        service_id = service_ids[i] if i < len(service_ids) else ""
        if service_id:
            service = Service.objects.filter(pk=service_id).first()

        hsn_code = hsn_codes[i] if i < len(hsn_codes) else ""

        amount = quantity * rate

        QuotationLineItem.objects.create(
            quotation=quotation,
            service=service,
            description=description,
            hsn_code=hsn_code,
            quantity=quantity,
            rate=rate,
            amount=amount,
        )

        subtotal += amount
        count += 1

    return subtotal, count


def _apply_quotation_totals(quotation, request, subtotal):

    gst_id = request.POST.get("gst")

    if gst_id:
        gst = GstConfiguration.objects.filter(pk=gst_id).first()
        tax_rate = gst.gst_percentage if gst else Decimal("0")
    else:
        gst = None
        try:
            tax_rate = Decimal(request.POST.get("tax_rate") or "0")
        except InvalidOperation:
            tax_rate = Decimal("0")

    try:
        other_charges = Decimal(request.POST.get("other_charges") or "0")
    except InvalidOperation:
        other_charges = Decimal("0")

    taxable_amount = subtotal
    tax_due = (taxable_amount * tax_rate) / Decimal("100")
    grand_total = taxable_amount + tax_due + other_charges

    quotation.gst = gst
    quotation.subtotal = subtotal
    quotation.taxable_amount = taxable_amount
    quotation.tax_rate = tax_rate
    quotation.tax_due = tax_due
    quotation.other_charges = other_charges
    quotation.grand_total = grand_total


@login_required
@require_POST
def save_quotation(request):

    company = get_object_or_404(
        CompanyProfile,
        pk=request.POST.get("company")
    )

    client = get_object_or_404(
        Client,
        pk=request.POST.get("client")
    )

    prepared_by = request.POST.get("prepared_by") or (
        request.user.get_full_name() or request.user.username
    )

    quotation = Quotation.objects.create(

        company=company,

        client=client,

        quote_date=request.POST.get("quote_date"),

        valid_until=request.POST.get("valid_until"),

        prepared_by=prepared_by,

        terms_and_conditions=request.POST.get("terms_and_conditions") or "",

        status=request.POST.get("status") or "Draft",

    )

    subtotal, count = _build_quotation_items(quotation, request)

    if count == 0:

        messages.error(
            request,
            "Please add at least one item to the quotation."
        )

        quotation.delete()

        return redirect("add_quotation")

    _apply_quotation_totals(quotation, request, subtotal)

    quotation.save()

    messages.success(
        request,
        "Quotation Created Successfully."
    )

    return redirect("quotation_list")


@login_required
def edit_quotation(request, pk):

    quotation = get_object_or_404(Quotation, pk=pk)

    if request.method == "POST":

        company = get_object_or_404(
            CompanyProfile,
            pk=request.POST.get("company")
        )

        client = get_object_or_404(
            Client,
            pk=request.POST.get("client")
        )

        descriptions = [d for d in request.POST.getlist("description[]") if d.strip() != ""]

        if len(descriptions) == 0:

            messages.error(
                request,
                "Please add at least one item to the quotation."
            )

            return redirect("edit_quotation", pk=quotation.pk)

        quotation.company = company
        quotation.client = client
        quotation.quote_date = request.POST.get("quote_date")
        quotation.valid_until = request.POST.get("valid_until")
        quotation.prepared_by = request.POST.get("prepared_by") or quotation.prepared_by
        quotation.terms_and_conditions = request.POST.get("terms_and_conditions") or ""
        quotation.status = request.POST.get("status") or quotation.status

        # Rebuild line items from scratch, same pattern used by edit_invoice,
        # to avoid duplicate or orphaned rows.
        quotation.items.all().delete()

        subtotal, count = _build_quotation_items(quotation, request)

        _apply_quotation_totals(quotation, request, subtotal)

        quotation.save()

        messages.success(
            request,
            "Quotation Updated Successfully."
        )

        return redirect("quotation_list")

    quotation_form = QuotationForm(instance=quotation)

    items = quotation.items.select_related("service").all()

    gst_options = GstConfiguration.objects.filter(is_active=True)

    return render(

        request,

        "transaction/quotation_form.html",

        {

            "quotation_form": quotation_form,

            "quotation": quotation,

            "items": items,

            "services": Service.objects.filter(is_active=True),

            "gst_options": gst_options,

            "gst_rates_json": {
                str(g.id): float(g.gst_percentage) for g in gst_options
            },

        }

    )


@login_required
def delete_quotation(request, pk):

    quotation = get_object_or_404(Quotation, pk=pk)

    quote_number = quotation.quote_number

    quotation.delete()

    messages.success(
        request,
        f"Quotation {quote_number} deleted successfully."
    )

    return redirect("quotation_list")


@login_required
def quotation_pdf(request, pk):

    quotation = get_object_or_404(Quotation, pk=pk)

    buffer = build_quotation_pdf(quotation)

    response = HttpResponse(buffer.read(), content_type="application/pdf")

    filename = f"Quotation_{quotation.quote_number}.pdf"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


