from django.contrib import admin, messages
from django.contrib.gis import admin as gis_admin
from django_object_actions import DjangoObjectActions, action
from . import models
from . import tasks


@admin.register(models.{{ cookiecutter.model_name }})
class {{ cookiecutter.model_name }}Admin(DjangoObjectActions, admin.ModelAdmin):
    """Django admin for {{ cookiecutter.model_name }}"""

    def fetch_from_api(self, request, obj):  # pylint: disable=unused-argument
        tasks.fetch_data_from_arcgis_api.delay()
        messages.success(request, "Fetch queued.")

    changelist_actions = ("fetch_from_api",)

    def has_change_permission(self, request, obj=None):
        return False
