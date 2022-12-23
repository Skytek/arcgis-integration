# Skytek Ltd - React
#
# Copyright (c) 2018 - 2022
# Author Skytek Ltd
#

from generic_map_api.routers import MapApiRouter

from . import views

router = MapApiRouter()
router.register("arc-gis", views.ParametrizedArcGisView, basename="arc-gis")

urlpatterns = router.urls
