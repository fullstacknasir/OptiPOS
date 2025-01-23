from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from .models import User


class CustomUserAdmin(UserAdmin):
    # Specify the forms to use for adding and changing users
    form = UserChangeForm
    add_form = UserCreationForm

    # Define the fields to display in the admin interface
    list_display = ('username', 'email', 'role', 'store', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    # Define the fieldsets for editing user details
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name')}),
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'role', 'store')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    # Define the fields to show when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'role', 'store', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('username', 'email', 'role')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
