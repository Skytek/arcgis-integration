from generic_map_api.serializers import BaseFeatureSerializer


class {{cookiecutter.model_name}}Serializer(BaseFeatureSerializer):
    def get_id(self, obj):
        return obj.id

    def get_geometry(self, obj):
        return obj.geometry

    def serialize_details(self, obj):
        return {
            **super().serialize_details(obj),
{% for api_field in cookiecutter.specs.model_fields %}
            {%- set field = cookiecutter.specs.model_fields[api_field] -%}
{{""}}            {{ field.model_field_name | literal }}: obj.{{ field.model_field_name }},
{% endfor -%}
{{""}}        }
