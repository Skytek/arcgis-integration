from generic_map_api.serializers import BaseFeatureSerializer


class {{ cookiecutter.model_name }}Serializer(BaseFeatureSerializer):
    feature_type = "image"

    def serialize(self, obj):
        serialized = super().serialize(obj)
        serialized.update({"url": obj.url})
        return serialized

    def get_geometry(self, obj):
        return obj.bounds

    def get_id(self, obj):
        return obj.id
