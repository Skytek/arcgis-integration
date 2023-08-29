{%- set celery_app_module = ".".join(cookiecutter.celery_app.split(".")[:-1]) -%}
{%- set celery_app = cookiecutter.celery_app.split(".")[-1] -%}
from {{ celery_app_module }} import {{ celery_app }}{% if celery_app != "app" %} as app{% endif %}
from . import models
from . import queues
from skytek_arcgis_integration.client import ArcGisClient, WGS84
from skytek_arcgis_integration.utils import float_range
from shapely import wkt
from typing import Optional
from shapely.geometry import box
from django.contrib.gis.geos import GEOSGeometry
from django.core.files.base import ContentFile
from uuid import uuid4
from base64 import b64decode
import requests


DOWNLOAD_BOUNDS = (
    (-180, -90),
    (180, 90),
)

DOWNLOAD_RESOLUTION = {  # maps zoom levels to dimensions of a single image (in deg)
    (0, 4): (5, 5),
    (5, 8): (2, 2),
    (9, 99): (1, 1),
}
IMAGE_SIZE = (512, 512)


@app.task(
    queue=queues.FETCH_DATA_BULK,
)
def fetch_data_from_arcgis_api():

    layer = models.{{ cookiecutter.model_name }}.objects.create()

    for zoom_levels, resolution in DOWNLOAD_RESOLUTION:
        longitude_resolution, latitude_resolution = resolution
        min_zoom, max_zoom = zoom_levels

        for longitude in float_range(DOWNLOAD_BOUNDS[0][0], DOWNLOAD_BOUNDS[1][0], longitude_resolution):
            for latitude in float_range(DOWNLOAD_BOUNDS[0][1], DOWNLOAD_BOUNDS[1][1], latitude_resolution):
                bounds = box(longitude, latitude, longitude+longitude_resolution, latitude+latitude_resolution)
                fetch_data_from_arcgis_api_single_image.delay(layer_id=layer.id, bounds_wkt=bounds.wkt, min_zoom, max_zoom)


@app.task(
    queue=queues.FETCH_DATA_SINGLE_IMAGE,
)
def fetch_data_from_arcgis_api_single_image(layer_id: int, bounds_wkt: str, min_zoom: int, max_zoom:int):
    base_layer_url = {{ cookiecutter.base_layer_url | literal}}
    client = ArcGisClient(base_layer_url)
    client.format = "json"

    bounds = wkt.loads(bounds_wkt)
    params = {
        "format": "png",
        "transparent": "true",
        "size": ",".join(map(str, IMAGE_SIZE)),
    }

    image = client.export_raster_image(bounding_polygon=bounds, params=params)

    uid = uuid4()
    file_name = f"{layer_id}--{uid}.png"

    if "imageData" in image:
        image_binary = b64decode(image["imageData"])
    elif "href" in image:
        response = requests.get(image["href"], timeout=30)
        response.raise_for_status()
        image_binary = response.content
    else:
        raise ValueError("Don't know how to get image binary")

    extent = box(
        image["extent"]["xmin"],
        image["extent"]["ymin"],
        image["extent"]["xmax"],
        image["extent"]["ymax"],
    )

    file_content = ContentFile(image_binary, file_name)
    try:
        image_srid = int(image["extent"]["spatialReference"]["wkid"])
    except (KeyError, ValueError):
        image_srid = WGS84

    image_obj = models.{{ cookiecutter.model_name }}Image(
        layer_id=layer_id,
        name=file_name,
        bounds=GEOSGeometry(extent.wkt, srid=image_srid),
        min_zoom=min_zoom,
        max_zoom=max_zoom,
    )

    image_obj.image.save(file_name, file_content, save=True)
