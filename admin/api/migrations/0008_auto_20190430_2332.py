# Generated by Django 2.1.7 on 2019-04-30 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20190430_2302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'type'},
        ),
    ]