# Generated by Django 5.1.3 on 2024-11-30 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_repairrequest_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancearticle',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='maintenance_articles/'),
        ),
    ]