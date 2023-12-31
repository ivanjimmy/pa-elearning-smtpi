# Generated by Django 4.2.3 on 2023-07-26 11:35

from django.db import migrations, models
import django.db.models.deletion
import froala_editor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jenjang',
            fields=[
                ('code', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('siswaKey', models.IntegerField(unique=True)),
                ('pengasuhKey', models.IntegerField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Jenjang',
            },
        ),
        migrations.CreateModel(
            name='TahunAjaran',
            fields=[
                ('tahunajaran_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Tahun Ajaran',
            },
        ),
        migrations.CreateModel(
            name='Siswa',
            fields=[
                ('siswa_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(blank=True, default='Siswa', max_length=100)),
                ('photo', models.ImageField(blank=True, default='profile_pics/default_siswa.png', upload_to='profile_pics')),
                ('jenjang', models.ManyToManyField(blank=True, related_name='siswas', to='main.jenjang')),
                ('tahunajaran', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='siswas', to='main.tahunajaran')),
            ],
            options={
                'verbose_name_plural': 'Siswa',
            },
        ),
        migrations.CreateModel(
            name='Pengasuh',
            fields=[
                ('pengasuh_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(blank=True, default='Pengasuh', max_length=100)),
                ('photo', models.ImageField(blank=True, default='profile_pics/default_pengasuh.png', upload_to='profile_pics')),
                ('tahunajaran', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pengasuh', to='main.tahunajaran')),
            ],
            options={
                'verbose_name_plural': 'Pengasuh',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=2000)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='materials/')),
                ('jenjang_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.jenjang')),
            ],
            options={
                'verbose_name_plural': 'Materi',
                'ordering': ['-datetime'],
            },
        ),
        migrations.AddField(
            model_name='jenjang',
            name='pengasuh',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.pengasuh'),
        ),
        migrations.AddField(
            model_name='jenjang',
            name='tahunajaran',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jenjangs', to='main.tahunajaran'),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('deadline', models.DateTimeField()),
                ('file', models.FileField(blank=True, null=True, upload_to='assignments/')),
                ('marks', models.DecimalField(decimal_places=2, max_digits=6)),
                ('jenjang_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.jenjang')),
            ],
            options={
                'verbose_name_plural': 'Tugas',
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('description', froala_editor.fields.FroalaField()),
                ('jenjang_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.jenjang')),
            ],
            options={
                'verbose_name_plural': 'Announcements',
                'ordering': ['-datetime'],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='submissions/')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('marks', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.assignment')),
                ('siswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.siswa')),
            ],
            options={
                'verbose_name_plural': 'Submissions',
                'ordering': ['datetime'],
                'unique_together': {('assignment', 'siswa')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='jenjang',
            unique_together={('code', 'tahunajaran', 'name')},
        ),
    ]
