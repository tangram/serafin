# this somehow runs before wsgi.py so...

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serafin.settings')

from django.contrib import admin
from django.contrib.admin import sites


class CustomAdminSite(admin.AdminSite):

    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        from request.models import Request
        from request.plugins import plugins

        if extra_context is None:
            extra_context = {}

        active_program = None
        if request.user.is_superuser:
            active_program = None
        elif request.user.program_restrictions.exists():
            active_program = request.user.program_restrictions.first()

        if active_program is not None:
            request.session["_program_id"] = active_program.id

        qs = Request.objects.this_month()
        for plugin in plugins.plugins:
            plugin.qs = qs

        extra_context['plugins'] = plugins.plugins

        return super().index(request, extra_context)


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site
sites.site = custom_admin_site

