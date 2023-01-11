from base64 import b64encode

from generic_map_api.serializers import BaseFeatureSerializer
from shapely.geometry import box


class ParametrizedArcGisSerializer(BaseFeatureSerializer):
    feature_type = "arc-gis-adhoc"

    def get_id(self, obj):
        feature_id = obj.get("id", None)
        if not feature_id:
            return None
        return f"{b64encode(obj['_layer_url'])},{feature_id}"

    def get_geometry(self, obj):
        return obj["geometry"]

    def serialize_details(self, obj):
        return {
            **obj["feature"]["attributes"],
        }


class AdHocBaseArcGisSerializer(BaseFeatureSerializer):
    feature_type = "arc-gis-adhoc"

    def get_id(self, obj):
        return obj.get("id", None)

    def get_geometry(self, obj):
        return obj["geometry"]

    def serialize_details(self, obj):
        return {
            **obj["feature"]["attributes"],
        }


class RasterAdHocBaseArcGisSerializer(BaseFeatureSerializer):
    feature_type = "image"

    def serialize(self, obj):
        url = None
        if "href" in obj:
            url = obj["href"]
        elif "contentType" in obj and "imageData" in obj:
            url = f"data:{obj['contentType']};base64, {obj['imageData']}"

        return {**super().serialize(obj), "url": url}

    def get_id(self, obj):
        return None

    def get_geometry(self, obj):
        return box(
            obj["extent"]["xmin"],
            obj["extent"]["ymin"],
            obj["extent"]["xmax"],
            obj["extent"]["ymax"],
        )

    def serialize_details(self, obj):
        return {}
