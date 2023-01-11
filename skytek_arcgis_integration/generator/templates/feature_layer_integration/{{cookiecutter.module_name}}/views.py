from generic_map_api.views import MapFeaturesBaseView, ViewPort

from . import models
from . import serializers


class {{ cookiecutter.model_name }}ApiView(MapFeaturesBaseView):
    """{{ cookiecutter.model_name }} API for mapping tool"""

    display_name = {{ cookiecutter.model_name | literal }}
    serializer = serializers.{{ cookiecutter.model_name }}Serializer()

    query_params = {
        # @TODO add some parameters: some grouping?, dates etc.
    }

    def get_items(self, viewport: ViewPort, params: dict):
        queryset = models.{{ cookiecutter.model_name }}.objects.all()
        if viewport:
            queryset = queryset.filter({{ cookiecutter.specs.model_geometry_field.model_field_name }}__intersects=viewport.to_polygon().wkt)

        # @TODO add filtering by params

        return queryset.iterator()

    def get_item(self, item_id):
        return models.{{ cookiecutter.model_name }}.objects.filter(id=item_id).first()
