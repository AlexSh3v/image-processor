# Generated by Django 5.0.7 on 2024-08-02 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original', models.ImageField(upload_to='uploads/')),
                ('processed', models.ImageField(blank=True, null=True, upload_to='processed/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
