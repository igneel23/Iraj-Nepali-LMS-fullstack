# admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

DEFAULT_STUDENT_PASSWORD = "student@123"
DEFAULT_MENTOR_PASSWORD = "mentor@123"

class UserAddForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'is_staff', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Auto-set password based on role
        if user.role == 'student':
            user.set_password(DEFAULT_STUDENT_PASSWORD)
        elif user.role == 'mentor':
            user.set_password(DEFAULT_MENTOR_PASSWORD)
        if commit:
            user.save()
        return user

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserAddForm
    model = User

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'is_staff', 'is_active')}
        ),
    )
