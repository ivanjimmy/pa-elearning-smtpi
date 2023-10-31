from django.contrib import admin

# Register your models here.
from .models import Siswa, Pengasuh, Jenjang, TahunAjaran, Assignment, Announcement


class SiswaAdmin(admin.ModelAdmin):
    list_display = ('siswa_id', 'name', 'tahunajaran')

class PengasuhAdmin(admin.ModelAdmin):
    list_display = ('pengasuh_id', 'name', 'tahunajaran')

admin.site.register(Siswa, SiswaAdmin)
admin.site.register(Pengasuh, PengasuhAdmin)
admin.site.register(Jenjang)
admin.site.register(TahunAjaran)
admin.site.register(Assignment)
admin.site.register(Announcement)