# Generated by Django 2.0.6 on 2018-07-26 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_aqinowcasthistory_aqirange_backgroundtaskmodel_faq_measuredataview'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='BackgroundTaskModel',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('task_params', models.TextField()),
        #         ('task_hash', models.CharField(max_length=40)),
        #         ('repeat', models.BigIntegerField()),
        #         ('repeat_until', models.DateTimeField()),
        #         ('task_name', models.CharField(max_length=190)),
        #     ],
        #     options={
        #         'db_table': 'background_task',
        #         'managed': False,
        #     },
        # ),
        # migrations.CreateModel(
        #     name='MeasureDataView',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('elapsed_time', models.IntegerField()),
        #         ('data', models.FloatField()),
        #         ('utimestamp', models.DateTimeField()),
        #     ],
        #     options={
        #         'db_table': 'fullmeasure',
        #         'managed': False,
        #     },
        # ),
        migrations.AddField(
            model_name='aqirange',
            name='color',
            field=models.CharField(default=0, max_length=150),
            preserve_default=False,
        ),
    ]
