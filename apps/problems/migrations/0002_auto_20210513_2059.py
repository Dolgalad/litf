# Generated by Django 3.2 on 2021-05-13 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codes', '0001_initial'),
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemmodel',
            name='input_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_input_type', to='codes.codemodel'),
        ),
        migrations.AlterField(
            model_name='problemmodel',
            name='output_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problem_output_type', to='codes.codemodel'),
        ),
    ]
