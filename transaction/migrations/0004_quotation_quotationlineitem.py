# Generated manually to add the Quotation system

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_service_hsn_code'),
        ('transaction', '0003_rename_rate_invoicelineitem_gst_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('quote_date', models.DateField()),
                ('valid_until', models.DateField()),
                ('prepared_by', models.CharField(blank=True, max_length=100)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('taxable_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('tax_rate', models.DecimalField(decimal_places=3, default=0, max_digits=6)),
                ('tax_due', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('other_charges', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('terms_and_conditions', models.TextField(blank=True, default='1. Customer will be billed after indicating acceptance of this quote\n2. Payment will be due prior to delivery of service and goods\n3. Please fax or mail the signed price quote to the address above')),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Sent', 'Sent'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Expired', 'Expired')], default='Draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='master.client')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='master.companyprofile')),
                ('gst', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master.gstconfiguration')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationLineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('hsn_code', models.CharField(blank=True, max_length=20, verbose_name='HSN/SAC')),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=10)),
                ('rate', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='transaction.quotation')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master.service')),
            ],
        ),
    ]
