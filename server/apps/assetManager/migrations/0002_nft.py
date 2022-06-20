# Generated by Django 4.0.5 on 2022-06-17 04:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0015_alter_user_email'),
        ('assetManager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nft_id', models.IntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('sk', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
