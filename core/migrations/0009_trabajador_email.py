# Generated by Django 3.1.4 on 2021-06-17 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20210616_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='email',
            field=models.EmailField(default='', max_length=254, unique=True),
        ),
    ]
