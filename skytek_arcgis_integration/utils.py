from datetime import datetime
from typing import Any, Generator, Optional, Tuple, Type

from dateutil.parser import parse
from django.contrib.gis.geos import (
    GEOSGeometry,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import box


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


def divide_rectangle(
    polygon: ShapelyPolygon, dimensions: Tuple[int, int]
) -> Generator[ShapelyPolygon, None, None]:
    dim_x, dim_y = dimensions
    min_x, min_y, max_x, max_y = polygon.bounds
    step_x = (max_x - min_x) / dim_x
    step_y = (max_y - min_y) / dim_y

    for x in range(dim_x + 1):
        for y in range(dim_y + 1):
            yield box(
                min_x + step_x * x,
                min_y + step_y * y,
                min_x + step_x * (x + 1),
                min_y + step_y * (y + 1),
            )


def float_range(start: float, end: float, step: float) -> Generator[float, None, None]:
    curr = start
    while curr < end:
        yield curr
        curr += step
