import string
from dataclasses import asdict, dataclass
from os import path
from typing import List, Optional

from cookiecutter.main import cookiecutter
from django.conf import settings

from skytek_arcgis_integration.client import ArcGisClient


def ask_user(prompt, default=None):
    if default:
        message = f"{prompt} [{default}]: "
    else:
        message = f"{prompt}: "

    raw_value = input(message)
    if default and raw_value == "":
        raw_value = default
    return raw_value


def generate_django_module(  # pylint: disable=too-many-locals,too-many-branches
    base_layer_url=None,
    module_path=None,
    model_name=None,
    celery_app_path=None,
    interactive=True,
):
    given_base_layer_url = base_layer_url
    given_module_path = module_path
    given_model_name = model_name
    given_celery_app_path = celery_app_path

    if interactive and not given_base_layer_url:
        base_layer_url = ask_user("Enter base layer_url")

    client = ArcGisClient(base_layer_url)
    info = client.get_info()

    if info.get("type") != "Feature Layer":
        raise ValueError("Unsupported arcgis layer")

    template_data = TemplateData.from_arcgis_info(info)

    template_directory = path.join(path.dirname(__file__), "integration_template")
    main_django_app_module = ".".join(settings.SETTINGS_MODULE.split(".")[:-1])

    if given_module_path:
        module_name = given_module_path.split(".")[-1]
        full_module_name = given_module_path
    else:
        module_name = make_python_style_variable_name(info["name"])
        if module_name[-1] != "s":
            module_name += "s"
        full_module_name = f"arcgis.{module_name}"

        if interactive:
            full_module_name = ask_user("Enter full module path", full_module_name)

    if given_model_name:
        model_name = given_model_name
    else:
        model_name = make_python_style_class_name(info["name"])
        if model_name[-1].lower() == "s":
            model_name = model_name[:-1]

        if interactive:
            model_name = ask_user("Enter model name", model_name)

    if given_celery_app_path:
        celery_app = given_celery_app_path
    else:
        celery_app = f"{main_django_app_module}.celery.app"

        if interactive:
            celery_app = ask_user("Enter celery app path", celery_app)

    output_directory = path.join(settings.BASE_DIR, *full_module_name.split(".")[:-1])
    module_name = full_module_name.split(".")[-1]
    extra_context = {
        "module_name": module_name,
        "model_name": model_name,
        "celery_app": celery_app,
        "base_layer_url": base_layer_url,
        "specs": template_data.to_dict(),
    }

    cookiecutter(
        template=template_directory,
        output_dir=output_directory,
        extra_context=extra_context,
        no_input=True,
    )

    full_output_directory = path.join(settings.BASE_DIR, *full_module_name.split("."))

    return full_output_directory, full_module_name


TYPE_MAPPING = {
    "esriFieldTypeOID": "IntegerField",
    "esriFieldTypeSmallInteger": "IntegerField",
    "esriFieldTypeInteger": "IntegerField",
    "esriFieldTypeDate": "DateTimeField",
    "esriFieldTypeSingle": "FloatField",
    "esriFieldTypeDouble": "FloatField",
    "esriFieldTypeString": "CharField",
}


def make_python_style_variable_name(name):
    output = ""
    for previous_letter, letter in zip("_" + name, name):
        if letter == "_" and output[-1:] == "_":
            continue

        if (
            letter in string.ascii_uppercase
            and previous_letter in string.ascii_lowercase
        ):
            output += "_"

        output += letter.lower()
    return output


def make_python_style_class_name(name):
    output = ""
    for previous_letter, letter in zip("_" + name, name):
        if letter in string.ascii_letters + string.digits:
            if previous_letter not in string.ascii_letters:
                output += letter.upper()
            else:
                output += letter.lower()

    return output


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
        model_field_type = field_mapping.get(info_dict["geometryType"], "GeometryField")
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
