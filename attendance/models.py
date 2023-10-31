from django.db import models
from main.models import Siswa, Jenjang

# Create your models here.


class Attendance(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    jenjang = models.ForeignKey(Jenjang, on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False)
    status = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Kehadiran'

    def __str__(self):
        return self.siswa.name + ' - ' + self.jenjang.name + ' - ' + self.date.strftime('%d-%m-%Y')

    def total_absent(self):
        absent = Attendance.objects.filter(
            siswa=self.siswa, status=False).count()
        return absent
        # if absent == 0:
        #     return absent
        # else:
        #     return absent - 1

    def total_present(self):
        present = Attendance.objects.filter(
            siswa=self.siswa, status=True).count()
        return present
        # if present == 0:
        #     return present
        # else:
        #     return present - 1
