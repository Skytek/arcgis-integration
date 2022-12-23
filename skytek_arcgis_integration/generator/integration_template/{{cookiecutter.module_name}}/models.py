import hashlib
import json

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from skytek_arcgis_integration import utils


class {{ cookiecutter.model_name }}(models.Model):
    {{ cookiecutter.specs.model_geometry_field.model_field_name }} = gis_models.{{ cookiecutter.specs.model_geometry_field.model_field_type }}(
        {{ cookiecutter.specs.model_geometry_field.model_field_kwargs | kwargs }}
    )
    unique_id = models.CharField(max_length=40)
{% for api_field in cookiecutter.specs.model_fields %}
    {%- set field = cookiecutter.specs.model_fields[api_field] -%}
{{""}}    {{ field.model_field_name }} = models.{{ field.model_field_type }}({{ field.model_field_kwargs | kwargs }})
{% endfor %}
    @property
    def geometry_wkt(self):
        return self.{{ cookiecutter.specs.model_geometry_field.model_field_name }}.wkt if self.{{ cookiecutter.specs.model_geometry_field.model_field_name }} else "POINT EMPTY"

    unique_id_fields = (
        {{ cookiecutter.specs.object_id_field_in_model | literal }},
        "geometry_wkt",
    )

    def create_unique_id(self):
        hashed_id = hashlib.sha1("\n".join([str(getattr(self, field)) for field in self.unique_id_fields] + [self.geometry.wkt]).encode("utf-8"))
        return hashed_id.hexdigest()

    @classmethod
    def from_api_payload(cls, payload):
        geojson_geometry = json.dumps(payload["geometry"])
        properties = payload["properties"]
        obj = cls(
            {{ cookiecutter.specs.model_geometry_field.model_field_name }}=utils.ensure_geometry(GEOSGeometry(geojson_geometry, srid={{ cookiecutter.specs.srid }}), cls.{{ cookiecutter.specs.model_geometry_field.model_field_name }}.field.geom_class),
{% for api_field in cookiecutter.specs.model_fields %}
            {%- set field = cookiecutter.specs.model_fields[api_field] -%}
{% if field.model_field_type == "DateTimeField" %}
{{""}}            {{ field.model_field_name }}=utils.ensure_datetime(properties[{{ field.api_field | literal }}]),
{% else %}
{{""}}            {{ field.model_field_name }}=properties[{{ field.api_field | literal }}],
{% endif %}
{% endfor -%}
{{""}}        )
        obj.unique_id = obj.create_unique_id()
        return obj
