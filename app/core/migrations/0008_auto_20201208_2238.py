# Generated by Django 2.2.16 on 2020-12-08 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='degree1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='degree1', to='core.Degree'),
        ),
        migrations.AddField(
            model_name='student',
            name='degree2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='degree2', to='core.Degree'),
        ),
        migrations.AddField(
            model_name='student',
            name='degree3',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='degree3', to='core.Degree'),
        ),
    ]
