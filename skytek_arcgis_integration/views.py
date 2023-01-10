from base64 import b64decode

from generic_map_api import params as api_params
from generic_map_api.views import MapFeaturesBaseView, ViewPort

from . import serializers
from .client import ArcGisClient
from .utils import divide_rectangle


class ParametrizedArcGisView(MapFeaturesBaseView):
    display_name = "ArcGis"
    serializer = serializers.ParametrizedArcGisSerializer()

    query_params = {"layer_url": api_params.Text("Layer base url")}

    def get_items(self, viewport: ViewPort, params: dict):
        layer_url = params["layer_url"]
        arc_gis = ArcGisClient(layer_url)
        for item in arc_gis.get_feature_list(
            viewport.to_polygon() if viewport else None
        ):
            item["_layer_url"] = layer_url
            yield item

    def get_item(self, item_id):
        layer_url, feature_id = item_id.split(",")
        layer_url = b64decode(layer_url)
        arc_gis = ArcGisClient(layer_url)
        return arc_gis.get_feature(feature_id)


class AdHocBaseArcGisView(MapFeaturesBaseView):
    display_name = "ArcGis"
    serializer = serializers.AdHocBaseArcGisSerializer()

    layer_url = None

    def get_items(self, viewport: ViewPort, params: dict):
        layer_url = self.layer_url
        arc_gis = ArcGisClient(layer_url)
        return arc_gis.get_feature_list(viewport.to_polygon() if viewport else None)

    def get_item(self, item_id):
        layer_url = self.layer_url
        arc_gis = ArcGisClient(layer_url)
        arc_gis.format = "json"
        return arc_gis.get_feature(item_id)


class RasterAdHocBaseArcGisView(MapFeaturesBaseView):
    display_name = "ArcGis Raster"
    serializer = serializers.AdHocBaseArcGisSerializer()

    layer_url = None

    def get_items(self, viewport: ViewPort, params: dict):
        layer_url = self.layer_url
        arc_gis = ArcGisClient(layer_url)
        arc_gis.format = "json"

        params = {
            "size": "512,512",
        }
        for rect in divide_rectangle(viewport.to_polygon(), (5, 4)):
            response = arc_gis.export_raster_image(rect, params=params)
            yield response

    def get_item(self, item_id):
        return {}


def arcgis_view_factory(layer_url, feature_type=None, display_name=None):
    feature_type = feature_type or serializers.AdHocBaseArcGisSerializer.feature_type
    display_name = display_name or AdHocBaseArcGisView.display_name

    class AdHocSerializer(serializers.AdHocBaseArcGisSerializer):
        pass

    AdHocSerializer.feature_type = feature_type

    class AdHocView(AdHocBaseArcGisView):  # pylint: disable=too-many-ancestors
        pass

    AdHocView.layer_url = layer_url
    AdHocView.serializer = AdHocSerializer()
    AdHocView.display_name = display_name

    return AdHocView


def arcgis_raster_view_factory(layer_url, feature_type=None, display_name=None):
    feature_type = (
        feature_type or serializers.RasterAdHocBaseArcGisSerializer.feature_type
    )
    display_name = display_name or RasterAdHocBaseArcGisView.display_name

    class AdHocSerializer(serializers.RasterAdHocBaseArcGisSerializer):
        pass

    AdHocSerializer.feature_type = feature_type

    class AdHocView(RasterAdHocBaseArcGisView):  # pylint: disable=too-many-ancestors
        pass

    AdHocView.layer_url = layer_url
    AdHocView.serializer = AdHocSerializer()
    AdHocView.display_name = display_name

    return AdHocView
