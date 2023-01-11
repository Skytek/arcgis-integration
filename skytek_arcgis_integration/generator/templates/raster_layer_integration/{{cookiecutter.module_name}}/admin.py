from base64 import b64encode

from django.utils.safestring import mark_safe
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


@admin.register(models.{{ cookiecutter.model_name }}Image)
class {{ cookiecutter.model_name }}ImageAdmin(admin.ModelAdmin):
    """Django admin for {{ cookiecutter.model_name }}Image"""

    list_display = (
        "preview",
        "name",
        "layer_timestamp",
    )

    list_filter = ("layer",)

    readonly_fields = ("full_preview",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def preview(self, obj):
        src = "data:image/jpg;base64," + b64encode(obj.image.read()).decode("ascii")
        return mark_safe(
            f'<img src="{src}" title="{obj.name}" width="50" height="50" />'
        )

    def full_preview(self, obj):
        src = "data:image/jpg;base64," + b64encode(obj.image.read()).decode("ascii")
        return mark_safe(f'<img src="{src}" title="{obj.name}" />')

    def layer_timestamp(self, obj):
        return obj.layer.created_at
