from django.contrib import admin

# Register your models here.
from .models import SiswaDiscussion, PengasuhDiscussion

class SiswaDiscussionAdmin(admin.ModelAdmin):
    list_display = ('jenjang', 'sent_by', 'content', 'sent_at', 'time')

class PengasuhDiscussionAdmin(admin.ModelAdmin):
    list_display = ('jenjang', 'sent_by', 'content', 'sent_at', 'time')

admin.site.register(SiswaDiscussion, SiswaDiscussionAdmin)
admin.site.register(PengasuhDiscussion, PengasuhDiscussionAdmin)

