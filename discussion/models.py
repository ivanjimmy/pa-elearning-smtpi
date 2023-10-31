from django.db import models
from main.models import Siswa, Pengasuh, Jenjang


class SiswaDiscussion(models.Model):
    content = models.TextField(max_length=1600, null=False)
    jenjang = models.ForeignKey(
        Jenjang, on_delete=models.CASCADE, related_name='discussions')
    sent_by = models.ForeignKey(
        Siswa, on_delete=models.CASCADE, related_name='discussions')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = 'Oleh siswa'

    def __str__(self):
        return self.content[:30]

    def time(self):
        return self.sent_at.strftime("%d-%b-%y, %I:%M %p")


class PengasuhDiscussion(models.Model):
    content = models.TextField(max_length=1600, null=False)
    jenjang = models.ForeignKey(
        Jenjang, on_delete=models.CASCADE, related_name='jenjangDiscussions')
    sent_by = models.ForeignKey(
        Pengasuh, on_delete=models.CASCADE, related_name='jenjangDiscussions')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = 'Oleh pengasuh'

    def __str__(self):
        return self.content[:30]

    def time(self):
        return self.sent_at.strftime("%d-%b-%y, %I:%M %p")
