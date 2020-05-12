# Generated by Django 2.2.12 on 2020-05-12 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HMInstallTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=60, unique=True)),
                ('repo', models.SlugField(max_length=60)),
                ('chart', models.SlugField(max_length=60)),
                ('chart_version', models.CharField(max_length=60)),
                ('context', models.TextField()),
                ('macros', models.TextField()),
                ('values', models.TextField()),
            ],
            options={
                'verbose_name': 'Install Template',
                'verbose_name_plural': 'Install Templates',
            },
        ),
    ]
