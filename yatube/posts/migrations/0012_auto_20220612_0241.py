# Generated by Django 2.2.16 on 2022-06-11 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220612_0211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Введите текст комментария', verbose_name='Текст комментария'),
        ),
    ]
