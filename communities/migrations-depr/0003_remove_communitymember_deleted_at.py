# Generated by Django 5.1.6 on 2025-02-28 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0002_alter_communitymember_community'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communitymember',
            name='deleted_at',
        ),
    ]
