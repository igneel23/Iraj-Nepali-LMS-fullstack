from django.contrib import admin
from .models import MentorProfile

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ('mentor_id', 'get_full_name', 'get_email','photo', 'expertise','current_company','experience', 'joined_on')
    search_fields = ('mentor_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name', 'expertise')
    list_filter = ('joined_on',)
    readonly_fields = ('mentor_id', 'user', 'joined_on')
    ordering = ('-joined_on',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = "Full Name"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"
