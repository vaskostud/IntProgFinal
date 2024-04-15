# Generated by Django 5.0.2 on 2024-04-12 10:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0007_alter_car_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="reviewer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="listings.purchase"
            ),
        ),
    ]