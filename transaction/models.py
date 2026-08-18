from django.db import models
from master.models import CompanyProfile, Client, Service


class Invoice(models.Model):

    STATUS = [
        ("Draft", "Draft"),
        ("Generated", "Generated"),
        ("Cancelled", "Cancelled"),
    ]

    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.PROTECT
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT
    )

    invoice_date = models.DateField()

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    gst_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Draft"
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.invoice_number:

            last = Invoice.objects.order_by("-id").first()

            if last:
                number = int(last.invoice_number[3:]) + 1
            else:
                number = 1

            self.invoice_number = f"INV{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class InvoiceLineItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gst_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):

        self.price = self.service.price
        self.gst_percentage = self.service.gst.gst_percentage

        subtotal = self.price * self.quantity

        self.gst_amount = (
            subtotal * self.gst_percentage
        ) / 100

        self.total = subtotal + self.gst_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return self.service.service_name


class GstBreakdown(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )

    invoice_item = models.ForeignKey(
        InvoiceLineItem,
        on_delete=models.CASCADE
    )

    cgst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    sgst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    igst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_gst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.invoice.invoice_number


class Payment(models.Model):

    MODE = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Cheque", "Cheque"),
        ("Net Banking", "Net Banking"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )

    payment_date = models.DateField()

    payment_mode = models.CharField(
        max_length=30,
        choices=MODE
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.invoice.invoice_number