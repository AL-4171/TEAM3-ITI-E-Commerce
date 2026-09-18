from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    ordering = ("email",)

    list_display = (
        "email",
        "first_name",
        "last_name",
        "mobile",
        "is_staff"
    )

    fieldsets = (

        (
            None,
            {
                "fields": (
                    "email",
                    "password"
                )
            }
        ),

        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "mobile"
                )
            }
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions"
                )
            }
        ),

    )

    add_fieldsets = (

        (
            None,
            {
                "classes": ("wide",),

                "fields": (
                    "email",
                    "password1",
                    "password2"
                ),
            }
        ),

    )