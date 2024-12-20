# Generated by Django 4.2.16 on 2024-12-04 16:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="available_normal_tickets",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="event",
            name="available_vip_tickets",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="ticket_type",
            field=models.CharField(
                choices=[("VIP", "VIP"), ("Normal", "Normal")],
                default="Normal",
                max_length=50,
            ),
        ),
    ]
