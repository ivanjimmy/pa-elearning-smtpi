from django.db import models
from froala_editor.fields import FroalaField
# Create your models here.


class Siswa(models.Model):
    siswa_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255, null=False)
    role = models.CharField(
        default="Siswa", max_length=100, null=False, blank=True)
    jenjang = models.ManyToManyField(
        'Jenjang', related_name='siswas', blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True,
                              null=False, default='profile_pics/default_siswa.png')
    tahunajaran = models.ForeignKey(
        'TahunAjaran', on_delete=models.CASCADE, null=False, blank=False, related_name='siswas')

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_siswa.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Siswa'

    def __str__(self):
        return self.name


class Pengasuh(models.Model):
    pengasuh_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255, null=False)
    tahunajaran = models.ForeignKey(
        'TahunAjaran', on_delete=models.CASCADE, null=False, related_name='pengasuh')
    role = models.CharField(
        default="Pengasuh", max_length=100, null=False, blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True,
                              null=False, default='profile_pics/default_pengasuh.png')

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_pengasuh.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Pengasuh'

    def __str__(self):
        return self.name


class TahunAjaran(models.Model):
    tahunajaran_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Tahun Ajaran'

    def __str__(self):
        return self.name

    def siswa_count(self):
        return self.siswas.count()

    def pengasuh_count(self):
        return self.pengasuh.count()

    def jenjang_count(self):
        return self.jenjangs.count()


class Jenjang(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    tahunajaran = models.ForeignKey(
        TahunAjaran, on_delete=models.CASCADE, null=False, related_name='jenjangs')
    pengasuh = models.ForeignKey(
        Pengasuh, on_delete=models.SET_NULL, null=True, blank=True)
    siswaKey = models.IntegerField(null=False, unique=True)
    pengasuhKey = models.IntegerField(null=False, unique=True)

    class Meta:
        unique_together = ('code', 'tahunajaran', 'name')
        verbose_name_plural = "Jenjang"

    def __str__(self):
        return self.name


class Announcement(models.Model):
    jenjang_code = models.ForeignKey(
        Jenjang, on_delete=models.CASCADE, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    description = FroalaField()

    class Meta:
        verbose_name_plural = "Pengumuman"
        ordering = ['-datetime']

    def __str__(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")


class Assignment(models.Model):
    jenjang_code = models.ForeignKey(
        Jenjang, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    deadline = models.DateTimeField(null=False)
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    marks = models.DecimalField(max_digits=6, decimal_places=2, null=False)

    class Meta:
        verbose_name_plural = "Tugas"
        ordering = ['-datetime']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def due_date(self):
        return self.deadline.strftime("%d-%b-%y, %I:%M %p")


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, null=False)
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, null=False)
    file = models.FileField(upload_to='submissions/', null=True,)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    marks = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def file_name(self):
        return self.file.name.split('/')[-1]

    def time_difference(self):
        difference = self.assignment.deadline - self.datetime
        days = difference.days
        hours = difference.seconds//3600
        minutes = (difference.seconds//60) % 60
        seconds = difference.seconds % 60

        if days == 0:
            if hours == 0:
                if minutes == 0:
                    return str(seconds) + " seconds"
                else:
                    return str(minutes) + " minutes " + str(seconds) + " seconds"
            else:
                return str(hours) + " hours " + str(minutes) + " minutes " + str(seconds) + " seconds"
        else:
            return str(days) + " days " + str(hours) + " hours " + str(minutes) + " minutes " + str(seconds) + " seconds"

    def submission_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.siswa.name + " - " + self.assignment.title

    class Meta:
        unique_together = ('assignment', 'siswa')
        verbose_name_plural = "Submissions"
        ordering = ['datetime']


class Material(models.Model):
    jenjang_code = models.ForeignKey(
        Jenjang, on_delete=models.CASCADE, null=False)
    description = models.TextField(max_length=2000, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    file = models.FileField(upload_to='materials/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Materi"
        ordering = ['-datetime']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")