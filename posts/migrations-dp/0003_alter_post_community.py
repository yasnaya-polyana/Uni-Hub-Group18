# Generated by Django 5.1.6 on 2025-02-28 18:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0002_alter_communitymember_community'),
        ('posts', '0002_post_community'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='communities.communities'),
        ),
    ]
