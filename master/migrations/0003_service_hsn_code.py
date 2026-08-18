from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0002_alter_client_options_alter_companyprofile_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="hsn_code",
            field=models.CharField(
                blank=True,
                help_text="HSN/SAC code shown on invoice and quotation PDFs.",
                max_length=20,
                verbose_name="HSN/SAC Code",
            ),
        ),
    ]