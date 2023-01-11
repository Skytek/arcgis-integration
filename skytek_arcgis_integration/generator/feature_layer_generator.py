from dataclasses import asdict, dataclass
from typing import List, Optional

from .utils import make_python_style_variable_name


def generate_feature_layer_django_module(  # pylint: disable=too-many-locals,too-many-branches
    info,
    **kwargs,
):
    template_data = TemplateData.from_arcgis_info(info)
    extra_context = {
        "specs": template_data.to_dict(),
    }

    return "feature_layer_integration", extra_context


TYPE_MAPPING = {
    "esriFieldTypeOID": "IntegerField",
    "esriFieldTypeSmallInteger": "IntegerField",
    "esriFieldTypeInteger": "IntegerField",
    "esriFieldTypeDate": "DateTimeField",
    "esriFieldTypeSingle": "FloatField",
    "esriFieldTypeDouble": "FloatField",
    "esriFieldTypeString": "CharField",
}


@dataclass
class TemplateData:
    srid: int
    object_id_field: str
    object_id_field_in_model: str

    model_geometry_field: "Field"
    model_fields: List["Field"]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_arcgis_info(cls, info_dict):
        model_geometry_field = cls.make_geometry_field(info_dict)
        model_fields = {
            field.api_field: field
            for field in [
                Field.from_esri_field(arcgis_field)
                for arcgis_field in info_dict["fields"]
            ]
            if field is not None
        }

        return cls(
            srid=info_dict["extent"]["spatialReference"]["wkid"],
            object_id_field=info_dict["objectIdField"],
            object_id_field_in_model=make_python_style_variable_name(
                info_dict["objectIdField"]
            ),
            model_geometry_field=model_geometry_field,
            model_fields=model_fields,
        )

    @classmethod
    def make_geometry_field(cls, info_dict):
        field_mapping = {
            "esriGeometryPoint": "PointField",
            "esriGeometryMultipoint": "MultiPointField",
            "esriGeometryPolygon": "MultiPolygonField",
        }
        model_field_type = field_mapping.get(
            info_dict.get("geometryType", None), "GeometryField"
        )
        return Field(
            api_field="",
            model_field_name="geometry",
            model_field_type=model_field_type,
            model_field_kwargs={"null": False},
        )


@dataclass
class Field:
    api_field: str
    model_field_name: str
    model_field_type: str
    model_field_kwargs: dict

    @classmethod
    def from_esri_field(cls, field_dict) -> Optional["Field"]:
        api_field = field_dict["name"]
        field_name = cls._transform_name(field_dict)
        field_type = cls._transform_type(field_dict)
        field_kwargs = cls._create_field_kwargs(field_dict)

        return cls(api_field, field_name, field_type, field_kwargs)

    @staticmethod
    def _transform_name(field_dict):
        name = field_dict["name"]
        name = make_python_style_variable_name(name)
        return name

    @staticmethod
    def _transform_type(field_dict):
        field_type = field_dict["type"]
        return TYPE_MAPPING.get(field_type, "CharField")

    @staticmethod
    def _create_field_kwargs(field_dict):
        kwargs = {}

        if "nullable" in field_dict and field_dict["nullable"]:
            kwargs["null"] = True

        if "alias" in field_dict and field_dict["alias"]:
            kwargs["verbose_name"] = field_dict["alias"]

        if field_dict["type"] == "esriFieldTypeString":
            kwargs["max_length"] = field_dict["length"]

        if field_dict["type"] not in TYPE_MAPPING:
            kwargs["max_length"] = 255

        return kwargs
