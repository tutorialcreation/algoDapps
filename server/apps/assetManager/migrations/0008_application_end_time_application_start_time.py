# Generated by Django 4.0.5 on 2022-06-20 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetManager', '0007_asset_bidders_alter_asset_nft'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='end_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='start_time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
