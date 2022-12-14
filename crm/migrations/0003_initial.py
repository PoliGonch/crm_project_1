# Generated by Django 4.0.4 on 2022-11-03 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0002_delete_user_delete_userrole'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=200, unique=True)),
                ('password', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('surname', models.CharField(blank=True, max_length=200)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.userrole')),
            ],
            options={
                'unique_together': {('email', 'password')},
            },
        ),
    ]
