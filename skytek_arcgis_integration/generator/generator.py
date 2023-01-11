from os import path

from cookiecutter.main import cookiecutter
from django.conf import settings

from skytek_arcgis_integration.client import ArcGisClient

from .feature_layer_generator import generate_feature_layer_django_module
from .raster_layer_generator import generate_raster_layer_django_module
from .utils import (
    ask_user,
    make_python_style_class_name,
    make_python_style_variable_name,
)

LAYER_TYPE_MAP = {
    "Feature Layer": generate_feature_layer_django_module,
    "Raster Layer": generate_raster_layer_django_module,
}


def _get_full_module_name(layer_name, given_module_path, interactive):
    if given_module_path:
        module_name = given_module_path.split(".")[-1]
        full_module_name = given_module_path
    else:
        module_name = make_python_style_variable_name(layer_name)
        if module_name[-1] != "s":
            module_name += "s"
        full_module_name = f"arcgis.{module_name}"

        if interactive:
            full_module_name = ask_user("Enter full module path", full_module_name)
    return full_module_name


def _get_model_name(layer_name, given_model_name, interactive):
    if given_model_name:
        model_name = given_model_name
    else:
        model_name = make_python_style_class_name(layer_name)
        if model_name[-1].lower() == "s":
            model_name = model_name[:-1]

        if interactive:
            model_name = ask_user("Enter model name", model_name)
    return model_name


def _get_celery_app(given_celery_app_path, interactive):
    main_django_app_module = ".".join(settings.SETTINGS_MODULE.split(".")[:-1])

    if given_celery_app_path:
        celery_app = given_celery_app_path
    else:
        celery_app = f"{main_django_app_module}.celery.app"

        if interactive:
            celery_app = ask_user("Enter celery app path", celery_app)
    return celery_app


def _get_layer_type(base_layer_url, info):
    layer_type = info.get("type")
    if not layer_type and (
        base_layer_url.endswith("/MapServer/") or base_layer_url.endswith("/MapServer")
    ):
        layer_type = "Raster Layer"

    if layer_type not in LAYER_TYPE_MAP:
        raise ValueError(f"Unsupported arcgis layer ({layer_type})")

    return layer_type


def _get_module_directory(full_module_name):
    return path.join(settings.BASE_DIR, *full_module_name.split("."))


def _get_output_directory(full_module_name):
    return path.join(settings.BASE_DIR, *full_module_name.split(".")[:-1])


def _get_top_module_name(full_module_name):
    return full_module_name.split(".")[-1]


def _get_template_directory(template_name):
    return path.join(path.dirname(__file__), "templates", template_name)


def generate_django_module(
    base_layer_url=None,
    module_path=None,
    model_name=None,
    celery_app_path=None,
    interactive=True,
):
    if interactive and not base_layer_url:
        base_layer_url = ask_user("Enter base layer_url")

    client = ArcGisClient(base_layer_url)
    info = client.get_info()

    layer_type = _get_layer_type(base_layer_url, info)

    layer_name = info.get("name") or info.get("mapName")
    full_module_name = _get_full_module_name(layer_name, module_path, interactive)
    model_name = _get_model_name(layer_name, model_name, interactive)
    celery_app = _get_celery_app(celery_app_path, interactive)

    template_name, extra_context = LAYER_TYPE_MAP[layer_type](info=info)

    extra_context = {
        "module_name": _get_top_module_name(full_module_name),
        "model_name": model_name,
        "celery_app": celery_app,
        "base_layer_url": base_layer_url,
        **extra_context,
    }

    cookiecutter(
        template=_get_template_directory(template_name),
        output_dir=_get_output_directory(full_module_name),
        extra_context=extra_context,
        no_input=True,
    )

    return _get_module_directory(full_module_name), full_module_name
