from django.db import models


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=100)

    email = models.EmailField()
    phone = models.CharField(max_length=15)

    gst_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)

    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)

    company_logo = models.ImageField(upload_to="company_logo/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class GstConfiguration(models.Model):
    gst_name = models.CharField(max_length=50)

    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    igst = models.DecimalField(max_digits=5, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gst_name


class Client(models.Model):
    client_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150, blank=True)

    email = models.EmailField()
    phone = models.CharField(max_length=15)

    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)

    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    contact_person = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client_name


class Service(models.Model):
    service_code = models.CharField(max_length=10, unique=True, editable=False)

    service_name = models.CharField(max_length=100)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    gst = models.ForeignKey(
        GstConfiguration,
        on_delete=models.PROTECT
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.service_code:

            last = Service.objects.order_by("-id").first()

            if last:
                number = int(last.service_code[3:]) + 1
            else:
                number = 1

            self.service_code = f"SER{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.service_name