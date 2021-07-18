# Generated by Django 3.1.4 on 2021-04-06 04:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("document", "0012_auto_20210405_1821"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accessright",
            name="user",
        ),
        migrations.AlterField(
            model_name="accessright",
            name="holder_id",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="accessright",
            name="holder_type",
            field=models.ForeignKey(
                limit_choices_to=models.Q(("app_label", "user"), ("model", "user")),
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
    ]
