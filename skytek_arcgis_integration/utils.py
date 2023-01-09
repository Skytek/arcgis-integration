from datetime import datetime
from typing import Any, Optional, Type

from dateutil.parser import parse
from django.contrib.gis.geos import (
    GEOSGeometry,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def ensure_datetime(value: Any) -> Optional[datetime]:
    try:
        if not value:
            return None
        if isinstance(value, (int, float)) or (
            isinstance(value, str) and is_numeric(value)
        ):
            value = float(value)
            if value > 2**32:
                value /= 1000
            return datetime.fromtimestamp(value)
        return parse(value)
    except ValueError as ex:
        raise ValueError(f"Cannot convert {value} to datetime") from ex


def ensure_geometry(
    value: GEOSGeometry, expected_class: Type[GEOSGeometry]
) -> GEOSGeometry:
    if isinstance(value, expected_class):
        return value
    if issubclass(expected_class, MultiPolygon) and isinstance(value, Polygon):
        return MultiPolygon([value])
    if issubclass(expected_class, MultiPoint) and isinstance(value, Point):
        return MultiPoint([value])

    raise ValueError(
        f"Don't know how to convert {value.__class__.__name__} to {expected_class.__name__}"
    )
