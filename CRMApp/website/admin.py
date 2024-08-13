from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class MyAdminSite(admin.AdminSite):
    site_header = _("Lead Management Admin")
    site_title = _("Admin Panel")
    index_title = _("Welcome to the Admin Panel")

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff


admin_site = MyAdminSite(name='myadmin')

# Register your models with the custom admin site


admin_site.register(User)
