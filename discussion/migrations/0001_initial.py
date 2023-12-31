# Generated by Django 4.2.3 on 2023-07-26 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiswaDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1600)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('jenjang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussions', to='main.jenjang')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussions', to='main.siswa')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
        migrations.CreateModel(
            name='PengasuhDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1600)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('jenjang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jenjangDiscussions', to='main.jenjang')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jenjangDiscussions', to='main.pengasuh')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
    ]
