# Generated by Django 3.1.2 on 2020-11-09 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0004_move_json_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="bibliography",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="document",
            name="comments",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
