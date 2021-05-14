# Generated by Django 3.2 on 2021-05-13 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('codes', '0001_initial'),
        ('problems', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SolverModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('date', models.DateTimeField()),
                ('description', models.CharField(blank=True, max_length=20000, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('implementation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codes.codemodel')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.problemmodel')),
            ],
        ),
    ]