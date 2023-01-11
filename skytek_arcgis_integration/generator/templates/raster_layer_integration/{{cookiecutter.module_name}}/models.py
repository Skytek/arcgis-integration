import hashlib
import json

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from skytek_arcgis_integration import utils
from django.urls import reverse


UPLOAD_DIRECTORY_NAME = ""


class {{ cookiecutter.model_name }}(models.Model):
    """Represents a group of images"""

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.created_at)


class {{ cookiecutter.model_name }}Image(models.Model):
    """Represents a single image"""

    created_at = models.DateTimeField(auto_now_add=True)

    layer = models.ForeignKey({{ cookiecutter.model_name }}, on_delete=models.CASCADE, null=True, related_name="images")
    bounds = gis_models.PolygonField()
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to=f"files/{UPLOAD_DIRECTORY_NAME}/")
    min_zoom = models.PositiveSmallIntegerField(default=0)
    max_zoom = models.PositiveSmallIntegerField(default=99)

    def download_url(self, request):
        return request.build_absolute_uri(
            reverse(
                "{{ cookiecutter.module_name }}-image-download", kwargs={"id": self.id, "filename": self.name}
            )
        )
