# Generated by Django 5.1b1 on 2024-07-17 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_alter_meetingrecord_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='social_media_details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
