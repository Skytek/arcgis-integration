from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from generic_map_api import params
from generic_map_api.views import MapFeaturesBaseView, ViewPort

from . import models
from . import serializers


class {{ cookiecutter.model_name }}ApiView(MapFeaturesBaseView):
    """{{ cookiecutter.model_name }} API for mapping tool"""

    display_name = {{ cookiecutter.model_name | literal }}
    serializer = serializers.{{ cookiecutter.model_name }}Serializer()

    def get_layer_choices(self, *args, **kwargs):
        return [
            params.Select.Choice(value=str(layer.id), label=layer.created_at)
            for layer in models.{{ cookiecutter.model_name }}.objects.all().order_by("-created_at")
        ]

    query_params = {
        "layer": params.Select(label="Layer sync time", choices=get_layer_choices),
    }

    def get_items(self, viewport: ViewPort, params: dict):
        queryset = models.{{ cookiecutter.model_name }}Image.objects.all()
        if viewport:
            queryset = queryset.filter(bounds__intersects=viewport.to_polygon().wkt)

        layer_id = int(params.get("layer", 0))
        queryset = queryset.filter(layer_id=layer_id)
        queryset = queryset.filter(min_zoom__lte=viewport.zoom, max_zoom__gte=viewport.zoom)

        for item in queryset.iterator():
            item.url = item.download_url(self.request)
            yield item

    def get_item(self, id):
        return {}


def image(request, id, filename):
    image = get_object_or_404(models.{{ cookiecutter.model_name }}Image, id=id)
    data = image.image.read()
    return HttpResponse(data, content_type="image/png")
