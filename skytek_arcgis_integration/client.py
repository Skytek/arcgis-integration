from typing import Optional

import requests
from shapely.geometry import Polygon

FROM_SETTINGS = object()
WGS84 = 4326


class ArcGisClient:
    def __init__(
        self,
        base_layer_url: str,
        auth_key=FROM_SETTINGS,
        add_dummy_where=True,
        timeout=300,
    ) -> None:
        if auth_key is FROM_SETTINGS:
            try:
                from django.conf import (  # pylint: disable=import-outside-toplevel
                    settings,
                )

                auth_key = settings.ARCGIS_AUTH_KEY
            except (ImportError, AttributeError):
                auth_key = None
        self.auth_key = auth_key

        self.base_layer_url = base_layer_url
        self.add_dummy_where = add_dummy_where
        self.format = "geojson"
        self.fields = ("*",)
        self.timeout = timeout

    def get_feature_list(self, bounding_polygon: Optional[Polygon] = None, params=None):
        params = params or {}
        url = self.base_layer_url + "/query"

        if self.add_dummy_where and "where" not in params:
            params = {**params, "where": "1=1"}

        if self.fields:
            params = {**params, "outFields": ",".join(self.fields)}

        if bounding_polygon:
            params = self._geometry_params(bounding_polygon, params)

        response = self._do_request(url, params)
        if "error" in response:
            print(response)
        return response.get("features", [])

    def get_feature(self, object_id: str):
        url = self.base_layer_url + "/" + object_id
        return self._do_request(url)

    def get_info(self):
        url = self.base_layer_url
        return self._do_request(url, format="json")

    def export_raster_image(self, bounding_polygon: Polygon, params=None):
        params = params or {}
        url = self.base_layer_url + "/export"

        params = {
            "imageSR": WGS84,
            "transparent": "true",
            **params,
            **self._geometry_params_for_raster(bounding_polygon),
        }
        return self._do_request(url, params)

    def _geometry_params(self, bounding_polygon: Polygon, params=None):
        params = params or {}
        params = {
            **params,
            "geometry": ",".join(map(str, bounding_polygon.bounds)),
            "geometryType": "esriGeometryEnvelope",
            "inSR": WGS84,
            "spatialRel": "esriSpatialRelIntersects",
        }
        return params

    def _geometry_params_for_raster(self, bounding_polygon: Polygon):
        params = {
            "bbox": ",".join(map(str, bounding_polygon.bounds)),
            "bboxSR": WGS84,
        }
        return params

    def _extend_params(
        self, params=None, format=None
    ):  # pylint: disable=redefined-builtin
        params = params or {}
        params = {**params, "f": format or self.format}
        if self.auth_key:
            params = {**params, "token": self.auth_key}
        return params

    def _do_request(
        self, url, params=None, format=None
    ):  # pylint: disable=redefined-builtin
        params = self._extend_params(params, format)
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
