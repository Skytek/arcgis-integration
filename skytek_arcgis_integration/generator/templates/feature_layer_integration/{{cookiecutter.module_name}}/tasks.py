{%- set celery_app_module = ".".join(cookiecutter.celery_app.split(".")[:-1]) -%}
{%- set celery_app = cookiecutter.celery_app.split(".")[-1] -%}
from {{ celery_app_module }} import {{ celery_app }}{% if celery_app != "app" %} as app{% endif %}
from . import models
from skytek_arcgis_integration.client import ArcGisClient
from shapely import wkt
from typing import Optional
from shapely.geometry import box


@app.task()
def fetch_data_from_arcgis_api():
    longitude_step = 60
    latitude_step = 30

    for longitude in range(-180, 180, longitude_step):
        for latitude in range(-90, 90, latitude_step):
            bounds = box(longitude, latitude, longitude+longitude_step, latitude+latitude_step)
            fetch_data_from_arcgis_api_single_chunk.delay(bounds_wkt=bounds.wkt)


@app.task()
def fetch_data_from_arcgis_api_single_chunk(bounds_wkt: Optional[str]=None, where: Optional[str]=None):
    base_layer_url = {{ cookiecutter.base_layer_url | literal}}
    client = ArcGisClient(base_layer_url)
    client.fields = ("*",)

    kwargs = {}
    if bounds_wkt:
        bounds = wkt.loads(bounds_wkt)
        kwargs["bounding_polygon"] = bounds
    if where:
        kwargs["params"] = {"where": where}

    features = client.get_feature_list(**kwargs)

    for feature in features:
        store_fetched_data_from_arcgis.delay(feature)


@app.task()
def store_fetched_data_from_arcgis(feature_dict):
    obj = models.{{ cookiecutter.model_name }}.from_api_payload(feature_dict)
    if models.{{ cookiecutter.model_name }}.objects.filter(unique_id=obj.unique_id).exists():
        return
    obj.save()
